import os
from dotenv import load_dotenv

load_dotenv()  # Load from .env if present

SPORTMONKS_API_TOKEN = os.getenv("SPORTMONKS_API_TOKEN", "YOUR_API_TOKEN_HERE")
UPDATE_INTERVAL_MINUTES = int(os.getenv("UPDATE_INTERVAL_MINUTES", "15"))
LOG_FILE = os.getenv("LOG_FILE", "tvguide.log")

# Hard-code the league to 501 (Scottish Premiership).
LEAGUE_ID = "501"
