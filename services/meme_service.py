import random
import requests
import tempfile
import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from utils.logging_utils import log_message
from services.unsplash_service import UnsplashService
from services.tenor_service import TenorService

class MemeService:
    def __init__(self, twitter_service, groq_service):
        self.twitter_service = twitter_service
        self.groq_service = groq_service
        self.unsplash_service = UnsplashService()
        self.tenor_service = TenorService()
        
        # Enhanced meme templates with more Gen-Z humor
        self.meme_templates = {
            "reaction": [
                "me rn: {}\nmy brain: {}",
                "nobody:\nliterally nobody:\nme: {}",
                "pov: {}",
                "*me {} ing intensifies*",
                "when {} hits different fr fr"
            ],
            "modern": [
                "bestie {} do be {} tho",
                "it's giving {}",
                "{} energy is immaculate rn",
                "main character moment: {}",
                "living my {} era"
            ],
            "gen_z": [
                "no cap fr fr {}",
                "slay {} bestie",
                "based {} moment",
                "lowkey {} highkey {}",
                "not me {} ing rn 💀"
            ],
            "vibes": [
                "the {} vibes are astronomical",
                "caught in {} behavior",
                "real {} hours",
                "manifesting {} energy ✨",
                "it's {} o'clock somewhere"
            ],
            "internet": [
                "me: {}\ninternet: {}",
                "404 {} not found",
                "downloading {} vibes...",
                "error: too much {} energy",
                "buffering... {} loading"
            ]
        }

    def analyze_tweet_with_groq(self, tweet_text):
        """Analyze tweet text to extract keywords and context"""
        # Use Groq service's analyze_text method
        return self.groq_service.analyze_text(tweet_text)

    def create_meme(self, image_url, meme_text):
        try:
            # Download the image
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGB if necessary
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if needed
            max_size = (1200, 1200)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Create drawing object
            draw = ImageDraw.Draw(img)
            
            # Try to load a fun font, fallback to default if not available
            try:
                # Try different font paths
                font_paths = [
                    "C:/Windows/Fonts/Impact.ttf",
                    "C:/Windows/Fonts/Arial.ttf",
                    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                    "arial.ttf"
                ]
                font = None
                for path in font_paths:
                    try:
                        font = ImageFont.truetype(path, 60)
                        break
                    except:
                        continue
                if not font:
                    font = ImageFont.load_default()
            except:
                font = ImageFont.load_default()
            
            # Add text with better positioning and style
            text_color = (255, 255, 255)  # White
            outline_color = (0, 0, 0)      # Black
            
            # Split text into lines
            lines = meme_text.split('\n')
            
            # Calculate total text height
            line_height = 70
            total_height = line_height * len(lines)
            
            # Position text at bottom with padding
            padding = 20
            start_y = img.height - total_height - padding
            
            # Draw each line
            for i, line in enumerate(lines):
                # Calculate line width for centering
                try:
                    text_width = draw.textlength(line, font=font)
                except:
                    # Fallback for older Pillow versions
                    text_width = font.getsize(line)[0]
                
                x = (img.width - text_width) / 2
                y = start_y + (i * line_height)
                
                # Draw outline
                outline_width = 3
                for dx in range(-outline_width, outline_width + 1):
                    for dy in range(-outline_width, outline_width + 1):
                        draw.text((x + dx, y + dy), line, outline_color, font=font)
                
                # Draw main text
                draw.text((x, y), line, text_color, font=font)
            
            # Add random emoji watermark
            emojis = ["💀", "😭", "💅", "✨", "🔥", "💯", "🤌", "😤"]
            watermark = random.choice(emojis)
            watermark_size = 40
            watermark_padding = 10
            draw.text((watermark_padding, watermark_padding), watermark, text_color, font=ImageFont.truetype("arial.ttf", watermark_size))
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
                img.save(temp_file, format="JPEG", quality=95)
                return temp_file.name
                
        except Exception as e:
            log_message(f"Error creating meme: {e}")
            return None

    def generate_meme_text(self, analysis, tweet_text):
        """Generate meme text using enhanced analysis"""
        try:
            keywords = analysis['keywords']
            sentiment = analysis['sentiment']
            context = analysis['context']
            style = analysis['style']
            emojis = analysis['emojis']
            
            # Select template based on sentiment and style
            if 'sarcastic' in style:
                template_type = "gen_z"
            elif 'relatable' in style:
                template_type = "reaction"
            elif 'funny' in style:
                template_type = "modern"
            else:
                template_type = random.choice(list(self.meme_templates.keys()))
            
            template = random.choice(self.meme_templates[template_type])
            
            # Add sentiment-appropriate slang
            if sentiment == 'positive':
                slang = ["fr fr", "bestie", "slay", "bussin", "sheesh", "living for this"]
            elif sentiment == 'negative':
                slang = ["��", "😭", "literally", "ngl", "iykyk"]
            else:
                slang = [
                    "fr fr", "no cap", "bestie", "literally", "slay",
                    "based", "bussin", "sheesh", "lowkey", "highkey",
                    "ngl", "iykyk", "rent free", "living for this",
                    "main character energy"
                ]
            
            # Format the template with keywords and context
            try:
                if template.count('{}') == 1:
                    meme_text = template.format(random.choice(keywords))
                elif template.count('{}') == 2:
                    meme_text = template.format(
                        random.choice(keywords),
                        random.choice(slang) if random.random() < 0.5 else random.choice(keywords)
                    )
                else:
                    meme_text = f"{random.choice(keywords)} {random.choice(slang)}"
                
                # Add context-appropriate emoji
                if emojis:
                    meme_text += f" {random.choice(emojis)}"
                
                # 30% chance to add an extra slang term
                if random.random() < 0.3:
                    meme_text += f" {random.choice(slang)}"
                
                return meme_text
            except Exception as format_error:
                log_message(f"Error formatting template: {format_error}")
                return f"{random.choice(keywords)} {random.choice(slang)}"
                
        except Exception as e:
            log_message(f"Error generating meme text: {e}")
            return "vibing rn fr fr"

    def get_meme_for_keywords(self, analysis, tweet_text):
        """Get meme based on enhanced analysis"""
        try:
            keywords = analysis['keywords']
            sentiment = analysis['sentiment']
            context = analysis['context']
            style = analysis['style']
            
            # Adjust GIF probability based on context and style
            gif_probability = 0.5  # default
            if 'reaction' in style:
                gif_probability = 0.7  # higher chance for reaction memes
            elif 'funny' in style:
                gif_probability = 0.6  # slightly higher for funny content
            
            # Try GIF first if probability check passes
            if random.random() < gif_probability:
                gif_url = self.tenor_service.search_gif(keywords)
                if gif_url:
                    return gif_url, "gif"
            
            # Try Unsplash for static memes
            image_url = self.unsplash_service.search_image(keywords)
            if image_url:
                meme_text = self.generate_meme_text(analysis, tweet_text)
                meme_path = self.create_meme(image_url, meme_text)
                if meme_path:
                    return meme_path, "image"
            
            # If all else fails, try one more time with different keywords
            backup_keywords = ["funny", "meme", "reaction"]
            image_url = self.unsplash_service.search_image(backup_keywords)
            if image_url:
                meme_text = self.generate_meme_text(analysis, tweet_text)
                meme_path = self.create_meme(image_url, meme_text)
                if meme_path:
                    return meme_path, "image"
            
            return None, None
            
        except Exception as e:
            log_message(f"Error getting meme for keywords: {e}")
            return None, None

    def download_and_upload_meme(self, meme_source, media_type):
        try:
            if media_type == "gif":
                # Download GIF and upload directly
                response = requests.get(meme_source, stream=True)
                if response.status_code != 200:
                    log_message(f"Failed to download GIF: {response.status_code}")
                    return None
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name
                    log_message(f"Downloaded GIF to {temp_file_path}")
            else:
                # Use the generated meme image path
                temp_file_path = meme_source
                log_message(f"Using meme image at {temp_file_path}")
            
            # Upload to Twitter
            log_message(f"Uploading media to Twitter: {temp_file_path}")
            media = self.twitter_service.api.media_upload(temp_file_path)
            
            if media and hasattr(media, 'media_id'):
                log_message(f"Successfully uploaded media, got ID: {media.media_id}")
                
                # Clean up
                os.unlink(temp_file_path)
                
                return media.media_id
            else:
                log_message("Media upload returned unexpected result")
                return None
            
        except Exception as e:
            log_message(f"Error uploading meme: {e}")
            # Try to clean up the file even if there was an error
            try:
                if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
            except:
                pass
            return None 