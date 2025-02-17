import requests
import logging
from datetime import datetime, timedelta
from config import SPORTMONKS_API_TOKEN, LEAGUE_ID

def fetch_fixtures():
    """
    Fetch fixtures for league 501 (Scottish Premiership) for the next 14 days.
    Returns a list of fixture dicts.
    """
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")

    url = (
        f"https://api.sportmonks.com/v3/football/fixtures/between/"
        f"{start_date}/{end_date}"
        f"?api_token={SPORTMONKS_API_TOKEN}"
        f"&filters[league_id]={LEAGUE_ID}"
    )

    logging.info(f"Fetching fixtures from: {url}")
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Error fetching data from SportMonks: "
                      f"{response.status_code} - {response.text}")
        return []

    data = response.json().get("data", [])
    logging.info(f"Fetched {len(data)} fixtures for league {LEAGUE_ID}")
    return data
