from flask import Flask, Response
import requests
import time
import threading
import xml.etree.ElementTree as ET
import os
from datetime import datetime, timedelta

app = Flask(__name__)

SPORTMONKS_API_TOKEN = os.getenv("SPORTMONKS_API_TOKEN", "your_api_token_here")
API_URL = f"https://api.sportmonks.com/v3/football/fixtures/between/{datetime.now().strftime('%Y-%m-%d')}/{(datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d')}?api_token={SPORTMONKS_API_TOKEN}"

tv_guide_data = None
UPDATE_INTERVAL = 60 * 60  # Update every hour


def fetch_tv_guide():
    global tv_guide_data
    print("Fetching TV guide data...")
    response = requests.get(API_URL)
    
    if response.status_code == 200:
        data = response.json().get("data", [])
        tv_guide_data = generate_tv_guide(data)
        print("TV guide updated successfully.")
    else:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")


def generate_tv_guide(fixtures):
    root = ET.Element("tv", {"generator-info-name": "Scottish Football TV Guide Generator"})

    channels = {
        "aberdeen_tv": "Aberdeen TV",
        "celtic_tv": "Celtic TV",
        "dundee_fc_tv": "Dundee FC TV",
        "dundee_utd_tv": "Dundee Utd TV",
        "falkirk_tv": "Falkirk TV",
        "hearts_tv": "Hearts TV",
        "hibs_tv": "Hibs TV",
        "kilmarnock_tv": "Kilmarnock TV",
        "livingston_tv": "Livingston TV",
        "motherwell_tv": "Motherwell TV",
        "rangers_tv": "Rangers TV",
        "ross_county_tv": "Ross County TV",
        "st_johnstone_tv": "St Johnstone TV",
        "st_mirren_tv": "St Mirren TV",
    }

    # Add channel elements
    for channel_id, display_name in channels.items():
        channel_elem = ET.SubElement(root, "channel", {"id": channel_id})
        ET.SubElement(channel_elem, "display-name").text = display_name

    # Add programme elements
    for fixture in fixtures:
        home_team, away_team = fixture["name"].split(" vs ")
        start_time = datetime.strptime(fixture["starting_at"], "%Y-%m-%d %H:%M:%S")
        end_time = start_time + timedelta(minutes=120)
        
        formatted_start = start_time.strftime("%Y%m%d%H%M%S +0000")
        formatted_end = end_time.strftime("%Y%m%d%H%M%S +0000")

        for team in [home_team, away_team]:
            channel_id = f"{team.lower().replace(' ', '_')}_tv"
            if channel_id in channels:
                programme_elem = ET.SubElement(root, "programme", {
                    "start": formatted_start,
                    "stop": formatted_end,
                    "channel": channel_id,
                })
                ET.SubElement(programme_elem, "title").text = f"{home_team} vs {away_team}"

    return ET.tostring(root, encoding="utf-8")


@app.route("/tvguide.xml")
def serve_tv_guide():
    if tv_guide_data:
        return Response(tv_guide_data, mimetype="application/xml")
    return "Guide not available", 503


def update_tv_guide_loop():
    while True:
        fetch_tv_guide()
        time.sleep(UPDATE_INTERVAL)


if __name__ == "__main__":
    fetch_tv_guide()  # Fetch immediately on start
    threading.Thread(target=update_tv_guide_loop, daemon=True).start()
    app.run(host="0.0.0.0", port=5000)
