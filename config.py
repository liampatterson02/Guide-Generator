import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env if present

SPORTMONKS_API_TOKEN = os.getenv("SPORTMONKS_API_TOKEN", "YOUR_API_TOKEN_HERE")
UPDATE_INTERVAL_MINUTES = int(os.getenv("UPDATE_INTERVAL_MINUTES", "15"))
LEAGUE_IDS = os.getenv("LEAGUE_IDS", "501")  # Comma-separated list of league IDs
LEAGUE_IDS = [l.strip() for l in LEAGUE_IDS.split(",") if l.strip()]

# For demonstration, store logs in a file. Adjust path if needed.
LOG_FILE = os.getenv("LOG_FILE", "tvguide.log")

# By default, generate M3U? (Yes/No)
ENABLE_M3U = os.getenv("ENABLE_M3U", "Yes").lower() in ["yes", "true", "1"]
