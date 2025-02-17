import requests
from datetime import datetime, timedelta, timezone
from config import SPORTMONKS_API_TOKEN, LEAGUE_IDS
import logging

def fetch_fixtures():
    """
    Fetch fixtures from the SportMonks API for the next 14 days
    for the leagues specified in LEAGUE_IDS.
    """
    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=14)).strftime("%Y-%m-%d")
    all_fixtures = []

    for league_id in LEAGUE_IDS:
        url = (
            f"https://api.sportmonks.com/v3/football/fixtures/between/"
            f"{start_date}/{end_date}?api_token={SPORTMONKS_API_TOKEN}"
            f"&filters[league_id]={league_id}"
        )
        logging.info(f"Fetching fixtures from: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            logging.error(f"Error fetching data from SportMonks (league {league_id}): "
                          f"{response.status_code} - {response.text}")
            continue

        data = response.json().get("data", [])
        logging.info(f"Fetched {len(data)} fixtures for league {league_id}")
        all_fixtures.extend(data)

    return all_fixtures
