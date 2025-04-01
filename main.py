import threading
import time
from config.settings import load_environment
from utils.logging_utils import log_message
from utils.rate_limiting import reset_rate_limits, log_rate_limits
from services.twitter_service import TwitterService
from services.groq_service import GroqService
from services.meme_service import MemeService
import datetime

def fetch_and_reply_to_mentions(twitter_service, meme_service):
    while True:
        try:
            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            log_message(f"[{current_time}] Checking for mentions...")
            mentions = twitter_service.get_mentions()
            
            if mentions:
                log_message(f"[{current_time}] Processing {len(mentions)} new mentions")
                
                for mention in mentions:
                    try:
                        # Get the tweet text
                        tweet_text = mention.text if hasattr(mention, 'text') else mention.full_text
                        tweet_id = mention.id
                        log_message(f"[{current_time}] Processing mention: {tweet_text}")
                        
                        # Process the mention with enhanced analysis
                        analysis = meme_service.analyze_tweet_with_groq(tweet_text)
                        log_message(f"[{current_time}] Enhanced analysis: {analysis}")
                        
                        meme_source, media_type = meme_service.get_meme_for_keywords(analysis, tweet_text)
                        log_message(f"[{current_time}] Got meme source: {meme_source}, type: {media_type}")
                        
                        if meme_source:
                            media_id = meme_service.download_and_upload_meme(meme_source, media_type)
                            if media_id:
                                result = twitter_service.reply_to_tweet(tweet_id, media_id)
                                if result:
                                    log_message(f"[{current_time}] ✅ Successfully replied to mention {tweet_id}")
                                else:
                                    log_message(f"[{current_time}] ❌ Failed to reply to mention {tweet_id}")
                            else:
                                log_message(f"[{current_time}] Failed to upload media")
                        else:
                            log_message(f"[{current_time}] Failed to get meme source")
                        
                        # Mark as processed
                        twitter_service.mark_mention_processed(tweet_id)
                        
                        # Wait between processing mentions to respect rate limits
                        time.sleep(5)  # Wait 5 seconds between replies
                    
                    except Exception as mention_e:
                        log_message(f"[{current_time}] Error processing mention: {mention_e}")
                
                # After processing all mentions, wait before next check
                log_message(f"[{current_time}] Waiting 5 seconds before next mention check...")
                time.sleep(5)
                continue
            
        except Exception as e:
            log_message(f"[{current_time}] Error in mention processing: {e}")
        
        # Check every 5 seconds to stay within rate limits
        log_message(f"[{current_time}] Waiting 5 seconds before checking for new mentions...")
        time.sleep(5)

def fetch_and_process_dms(twitter_service, meme_service):
    while True:
        try:
            log_message("DM functionality is limited in the current Twitter API.")
            log_message("For testing, send a mention to the bot instead.")
            time.sleep(120)  # Sleep for 2 minutes before next check
        except Exception as e:
            log_message(f"Error in DM processing: {e}")
            time.sleep(60)

def main():
    print("Starting meme bot setup...")
    
    # Load environment variables
    load_environment()
    
    # Initialize services
    twitter_service = TwitterService()
    groq_service = GroqService()
    meme_service = MemeService(twitter_service, groq_service)
    
    if not twitter_service.bot_id:
        log_message("Error: Bot ID not available. Authentication failed.")
        return
    
    # Reset mention tracking on startup
    twitter_service.reset_mention_tracking()
    log_message("Mention tracking reset - bot will detect all mentions")
    
    # Reset rate limits
    log_message("Resetting rate limits to defaults...")
    reset_rate_limits()
    log_rate_limits()
    
    # Start monitoring threads
    mention_thread = threading.Thread(target=fetch_and_reply_to_mentions, 
                                    args=(twitter_service, meme_service))
    dm_thread = threading.Thread(target=fetch_and_process_dms, 
                               args=(twitter_service, meme_service))
    
    mention_thread.daemon = True
    dm_thread.daemon = True
    
    mention_thread.start()
    dm_thread.start()
    
    log_message("Bot is now running and will respond to all mentions. Press Ctrl+C to stop.")
    
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        log_message("Bot is shutting down...")

if __name__ == "__main__":
    main() 