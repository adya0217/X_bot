import os
from utils.logging_utils import log_message
from groq import Groq

class GroqService:
    def __init__(self):
        try:
            self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
            log_message("Groq client initialized successfully")
        except Exception as e:
            log_message(f"Error initializing Groq client: {e}")
            self.client = None
            log_message("Using fallback keyword extraction")

    def analyze_text(self, text):
        """Analyze text to extract keywords, sentiment, and context"""
        try:
            if not self.client:
                return self._fallback_keyword_extraction(text)
            
            prompt = f"""Analyze this tweet and provide a detailed breakdown for meme generation:

Tweet: "{text}"

Please provide:
1. Main keywords (3-5 words that capture the core meaning)
2. Sentiment (positive/negative/neutral)
3. Context (what's happening in the tweet)
4. Meme style (reaction/relatable/sarcastic/funny)
5. Emoji suggestions (2-3 relevant emojis)

Format the response as:
KEYWORDS: word1, word2, word3
SENTIMENT: positive/negative/neutral
CONTEXT: brief description
STYLE: style1, style2
EMOJIS: emoji1, emoji2, emoji3"""
            
            completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": "You are a meme analysis expert. Analyze tweets to extract the best elements for meme generation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            response = completion.choices[0].message.content.strip()
            log_message(f"Groq analysis response: {response}")
            
            # Parse the response
            analysis = {}
            for line in response.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    analysis[key.strip()] = value.strip()
            
            # Extract keywords and additional context
            keywords = [k.strip() for k in analysis.get('KEYWORDS', '').split(',')]
            sentiment = analysis.get('SENTIMENT', 'neutral')
            context = analysis.get('CONTEXT', '')
            style = [s.strip() for s in analysis.get('STYLE', '').split(',')]
            emojis = [e.strip() for e in analysis.get('EMOJIS', '').split(',')]
            
            # Combine all information
            result = {
                'keywords': keywords,
                'sentiment': sentiment,
                'context': context,
                'style': style,
                'emojis': emojis
            }
            
            log_message(f"Enhanced analysis result: {result}")
            return result
            
        except Exception as e:
            log_message(f"Error in Groq analysis: {e}")
            return self._fallback_keyword_extraction(text)

    def _fallback_keyword_extraction(self, text):
        """Simple keyword extraction when Groq is unavailable"""
        log_message("Using fallback keyword extraction")
        # Remove mentions and URLs
        words = text.split()
        keywords = [word for word in words 
                   if not word.startswith('@') 
                   and not word.startswith('http') 
                   and not word.startswith('#')
                   and len(word) > 3]
        
        # Take up to 3 words as keywords
        selected = keywords[:3] if keywords else ["meme", "reaction"]
        log_message(f"Fallback keywords: {selected}")
        return {
            'keywords': selected,
            'sentiment': 'neutral',
            'context': 'general',
            'style': ['reaction'],
            'emojis': ['😂', '💀']
        } 