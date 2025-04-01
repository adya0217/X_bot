import os
from dotenv import load_dotenv

# File paths
RATE_LIMIT_FILE = "rate_limits.json"
LAST_MENTION_FILE = "last_mention.json"
LAST_DM_FILE = "last_dm.json"

def load_environment():
    # Try to load from the script directory first
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(script_dir, '.env')
    print(f"Looking for .env file at: {env_path}")
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f".env file found at script directory: {script_dir}")
    else:
        # Try to load from current directory
        load_dotenv()
        print(f"Current directory: {os.getcwd()}")
        print(f".env file exists in current directory: {os.path.exists('.env')}")

    # Debug: Print environment variable status
    print("Checking environment variables:")
    print(f"API_KEY: {'✓' if os.getenv('API_KEY') else '✗'}")
    print(f"API_SECRET: {'✓' if os.getenv('API_SECRET') else '✗'}")
    print(f"ACCESS_TOKEN: {'✓' if os.getenv('ACCESS_TOKEN') else '✗'}")
    print(f"ACCESS_SECRET: {'✓' if os.getenv('ACCESS_SECRET') else '✗'}")
    print(f"BEARER_TOKEN: {'✓' if os.getenv('BEARER_TOKEN') else '✗'}")
    print(f"GROQ_API_KEY: {'✓' if os.getenv('GROQ_API_KEY') else '✗'}") 