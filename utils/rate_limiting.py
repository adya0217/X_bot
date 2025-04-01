import json
import datetime
import time
import os
from utils.logging_utils import log_message
from config.settings import RATE_LIMIT_FILE

def reset_rate_limits():
    default_limits = {
        "mentions_api": {"calls_remaining": 150, "reset_time": None},
        "dm_api": {"calls_remaining": 15, "reset_time": None}
    }
    save_rate_limits(default_limits)
    log_message("Rate limits have been reset to defaults")
    return default_limits

def load_rate_limits():
    try:
        if os.path.exists(RATE_LIMIT_FILE):
            with open(RATE_LIMIT_FILE, "r") as f:
                rate_limits = json.load(f)
                # Validation logic here...
                return rate_limits
        return reset_rate_limits()
    except Exception as e:
        log_message(f"Error loading rate limits: {e}. Resetting to defaults.")
        return reset_rate_limits()

def save_rate_limits(rate_limits):
    with open(RATE_LIMIT_FILE, "w") as f:
        json.dump(rate_limits, f)

def log_rate_limits():
    """Log current rate limits"""
    rate_limits = load_rate_limits()
    for api, limits in rate_limits.items():
        log_message(f"{api}: {limits['calls_remaining']} remaining, resets at {limits['reset_time']}")

def update_rate_limits(api_name, response):
    try:
        rate_limits = load_rate_limits()
        if hasattr(response, "headers") and response.headers:
            if "x-rate-limit-remaining" in response.headers:
                rate_limits[api_name]["calls_remaining"] = int(response.headers["x-rate-limit-remaining"])
            if "x-rate-limit-reset" in response.headers:
                reset_time = int(response.headers["x-rate-limit-reset"])
                rate_limits[api_name]["reset_time"] = datetime.datetime.fromtimestamp(reset_time).isoformat()
            save_rate_limits(rate_limits)
    except Exception as e:
        log_message(f"Error updating rate limits: {e}")

# Rest of your rate limiting functions... 