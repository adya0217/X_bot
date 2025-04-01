import tweepy
import os
from utils.logging_utils import log_message
from config.settings import LAST_MENTION_FILE
import json
import datetime
import time

class TwitterService:
    def __init__(self):
        self.client = None
        self.api = None
        self.bot_id = None
        self.bot_username = None
        self.last_mention_id = None
        self.processed_mentions = set()
        self.initialize_twitter()
        self.load_last_mention_id()

    def initialize_twitter(self):
        try:
            twitter_auth = tweepy.OAuthHandler(os.getenv("API_KEY"), os.getenv("API_SECRET"))
            twitter_auth.set_access_token(os.getenv("ACCESS_TOKEN"), os.getenv("ACCESS_SECRET"))
            
            self.client = tweepy.Client(
                bearer_token=os.getenv("BEARER_TOKEN"),
                consumer_key=os.getenv("API_KEY"),
                consumer_secret=os.getenv("API_SECRET"),
                access_token=os.getenv("ACCESS_TOKEN"),
                access_token_secret=os.getenv("ACCESS_SECRET"),
                wait_on_rate_limit=True
            )
            
            self.api = tweepy.API(twitter_auth, wait_on_rate_limit=True)
            
            user = self.api.verify_credentials()
            self.bot_id = user.id
            self.bot_username = user.screen_name
            log_message(f"Authenticated as {self.bot_username} (ID: {self.bot_id})")
            
        except Exception as e:
            log_message(f"Authentication error: {e}")
            self.bot_id = None

    def load_last_mention_id(self):
        """Load the last processed mention ID from file"""
        try:
            if os.path.exists(LAST_MENTION_FILE):
                with open(LAST_MENTION_FILE, 'r') as f:
                    data = json.load(f)
                    self.last_mention_id = data.get('last_id')
                    
                    # Load processed mentions
                    processed = data.get('processed_mentions', [])
                    for mention in processed:
                        self.processed_mentions.add(mention['id'])
                    
                    log_message(f"Loaded {len(self.processed_mentions)} processed mentions")
            else:
                log_message("No previous mention data found, starting fresh")
                self.last_mention_id = None
                self.processed_mentions = set()
        except Exception as e:
            log_message(f"Error loading last mention data: {e}")
            self.last_mention_id = None
            self.processed_mentions = set()

    def save_last_mention_id(self, mention_id):
        """Save the last processed mention ID to file"""
        try:
            current_time = datetime.datetime.now().isoformat()
            processed_mentions = [
                {'id': mid, 'timestamp': current_time}
                for mid in self.processed_mentions
            ]
            
            data = {
                'last_id': str(mention_id),
                'timestamp': current_time,
                'processed_mentions': processed_mentions
            }
            
            with open(LAST_MENTION_FILE, 'w') as f:
                json.dump(data, f)
            log_message(f"Updated last mention ID to: {mention_id}")
        except Exception as e:
            log_message(f"Error saving last mention data: {e}")

    def is_mention_processed(self, mention_id):
        """Check if a mention has already been processed"""
        return str(mention_id) in self.processed_mentions

    def mark_mention_processed(self, mention_id):
        """Mark a mention as processed"""
        self.processed_mentions.add(str(mention_id))
        self.save_last_mention_id(self.last_mention_id)

    def get_mentions(self):
        """Get mentions using v2 API with rate limit handling"""
        try:
            if not self.bot_id:
                log_message("Bot ID not available. Cannot fetch mentions.")
                return []

            current_time = datetime.datetime.now().strftime("%H:%M:%S")
            log_message(f"[{current_time}] Checking for mentions...")
            
            try:
                # Use v2 API's user mentions endpoint
                mentions = self.client.get_users_mentions(
                    id=self.bot_id,
                    max_results=10,
                    tweet_fields=["text", "created_at", "author_id"]
                )
                
                if mentions and hasattr(mentions, 'data'):
                    mentions_list = mentions.data if isinstance(mentions.data, list) else [mentions.data]
                    log_message(f"[{current_time}] Found {len(mentions_list)} mentions")
                    
                    # Filter out already processed mentions
                    new_mentions = [
                        mention for mention in mentions_list
                        if not self.is_mention_processed(mention.id)
                    ]
                    
                    if new_mentions:
                        log_message(f"[{current_time}] Found {len(new_mentions)} new mentions to process")
                        
                        # Update last mention ID
                        newest_id = str(max(int(mention.id) for mention in mentions_list))
                        self.last_mention_id = newest_id
                        self.save_last_mention_id(newest_id)
                        
                        return new_mentions
                    else:
                        log_message(f"[{current_time}] All mentions have already been processed")
                        return []
                else:
                    log_message(f"[{current_time}] No mentions found")
                    return []
                
            except tweepy.errors.TweepyException as api_error:
                if "Rate limit exceeded" in str(api_error):
                    log_message(f"[{current_time}] Rate limit hit! Waiting for reset...")
                    # Wait for 15 minutes before trying again
                    time.sleep(900)  # 15 minutes
                elif "401" in str(api_error):
                    log_message(f"[{current_time}] Authentication error - please check your API credentials")
                elif "403" in str(api_error):
                    log_message(f"[{current_time}] Access denied - you may have hit your API tier limits")
                else:
                    log_message(f"[{current_time}] Twitter API error: {api_error}")
                return []
            
            except Exception as api_error:
                log_message(f"[{current_time}] Error with Twitter API: {api_error}")
                return []
            
        except Exception as e:
            log_message(f"[{current_time}] Error fetching mentions: {e}")
            return []

    def reply_to_tweet(self, tweet_id, media_id):
        """Reply to a tweet with media"""
        try:
            log_message(f"Attempting to reply to tweet {tweet_id} with media {media_id}")
            
            # Try v2 API first
            try:
                response = self.client.create_tweet(
                    text="Here's your meme! 🎭",
                    media_ids=[media_id],
                    in_reply_to_tweet_id=tweet_id
                )
                
                log_message(f"Successfully replied to tweet {tweet_id} using v2 API")
                return response
                
            except Exception as v2_error:
                log_message(f"V2 API reply error: {v2_error}")
                
                # Try v1.1 API as fallback
                try:
                    response = self.api.update_status(
                        status="Here's your meme! 🎭",
                        in_reply_to_status_id=tweet_id,
                        media_ids=[media_id],
                        auto_populate_reply_metadata=True
                    )
                    
                    log_message(f"Successfully replied to tweet {tweet_id} using v1.1 API")
                    return response
                except Exception as v1_error:
                    log_message(f"V1.1 API reply error: {v1_error}")
                    return None
                
        except Exception as e:
            log_message(f"Error replying to tweet: {e}")
            return None

    def check_specific_tweet(self, tweet_id):
        """Debug method to check a specific tweet"""
        try:
            # Try to look up the tweet
            tweet = self.client.get_tweet(tweet_id)
            log_message(f"Found tweet: {tweet.data.text}")
            return tweet.data
        except Exception as e:
            log_message(f"Error finding tweet {tweet_id}: {e}")
            return None

    def process_specific_mention(self, tweet_id, meme_service):
        """Process a specific mention by ID"""
        try:
            log_message(f"🔍 Directly checking tweet {tweet_id}...")
            
            # Check if already processed
            if self.is_mention_processed(tweet_id):
                log_message(f"Already processed tweet {tweet_id}")
                return False
            
            # Try to get the tweet
            try:
                # v2 API lookup
                response = self.client.get_tweet(
                    id=tweet_id,
                    tweet_fields=["text", "created_at"]
                )
                
                if response and hasattr(response, 'data'):
                    mention = response.data
                    tweet_text = mention.text
                    log_message(f"Found tweet to process: {tweet_text}")
                    
                    # Process the mention
                    keywords = meme_service.analyze_tweet_with_groq(tweet_text)
                    log_message(f"Extracted keywords: {keywords}")
                    
                    meme_source, media_type = meme_service.get_meme_for_keywords(keywords, tweet_text)
                    log_message(f"Got meme source: {meme_source}, type: {media_type}")
                    
                    if meme_source:
                        media_id = meme_service.download_and_upload_meme(meme_source, media_type)
                        log_message(f"Media upload returned ID: {media_id}")
                        
                        if media_id:
                            # Force a reply using v1.1 API
                            try:
                                response = self.api.update_status(
                                    status="Here's your meme! 🎭",
                                    in_reply_to_status_id=tweet_id,
                                    media_ids=[media_id],
                                    auto_populate_reply_metadata=True
                                )
                                
                                log_message(f"✅ Successfully replied to tweet {tweet_id}")
                                self.mark_mention_processed(tweet_id)
                                return True
                            except Exception as v1_error:
                                log_message(f"V1.1 API reply error: {v1_error}")
                                
                                # Try with v2 API as fallback
                                try:
                                    response = self.client.create_tweet(
                                        text="Here's your meme! 🎭", 
                                        media_ids=[media_id],
                                        in_reply_to_tweet_id=tweet_id
                                    )
                                    
                                    log_message(f"✅ Successfully replied to tweet {tweet_id} using v2 API")
                                    self.mark_mention_processed(tweet_id)
                                    return True
                                except Exception as v2_error:
                                    log_message(f"V2 API reply error: {v2_error}")
                                    return False
                        else:
                            log_message("Failed to upload media")
                            return False
                    else:
                        log_message("Failed to get meme source")
                        return False
                else:
                    log_message(f"Could not find tweet {tweet_id}")
                    return False
                
            except Exception as e:
                log_message(f"Error processing specific mention: {e}")
                return False
            
        except Exception as e:
            log_message(f"Error in process_specific_mention: {e}")
            return False

    def reset_mention_tracking(self):
        """Reset mention tracking to start fresh"""
        try:
            log_message("Resetting mention tracking")
            self.last_mention_id = None
            self.processed_mentions = set()
            if os.path.exists(LAST_MENTION_FILE):
                os.remove(LAST_MENTION_FILE)
        except Exception as e:
            log_message(f"Error resetting mention tracking: {e}") 