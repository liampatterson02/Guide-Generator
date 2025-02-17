import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import threading
import xml.etree.ElementTree as ET
from flask import Flask, send_file

app = Flask(__name__)

# Define an absolute path for the guide.xml file based on the current file's directory.
GUIDE_XML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guide.xml')

# URLs for fixture scraping
PREMIERSHIP_URL = "https://spfl.co.uk/league/premiership/fixtures"
CHAMPIONSHIP_URL = "https://spfl.co.uk/league/championship/fixtures"

# List of channels to include in the TV guide
CHANNELS = [
    "Aberdeen TV", "Celtic TV", "Dundee FC TV", "Dundee United TV",
    "Falkirk TV", "Hearts TV", "Hibernian TV", "Kilmarnock TV",
    "Livingston TV", "Motherwell TV", "Rangers TV", "Ross County TV",
    "St Johnstone TV", "St Mirren TV"
]

def scrape_fixtures(url):
    """
    Scrapes fixtures from the provided URL.
    This function assumes each fixture is contained in a <div class="fixture">
    with nested <span class="date-time"> and <span class="teams"> elements.
    Adjust class names and date format as needed.
    """
    fixtures = []
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return fixtures
        soup = BeautifulSoup(response.content, 'lxml')
        for fixture_div in soup.find_all('div', class_='fixture'):
            try:
                date_time_text = fixture_div.find('span', class_='date-time').text.strip()
                # Expected format e.g. "Saturday 03 October 2024 15:00"
                fixture_date = datetime.strptime(date_time_text, "%A %d %B %Y %H:%M")
                teams_text = fixture_div.find('span', class_='teams').text.strip()
                fixtures.append({
                    'date': fixture_date,
                    'teams': teams_text
                })
            except Exception:
                continue
    except Exception:
        pass
    return fixtures

def filter_next_two_weeks(fixtures):
    """
    Returns fixtures scheduled within the next 14 days.
    """
    now = datetime.now()
    two_weeks = now + timedelta(days=14)
    return [fx for fx in fixtures if now <= fx['date'] <= two_weeks]

def generate_tv_guide(fixtures):
    """
    Generates an XML TV guide for the defined channels.
    For each channel, if fixture data is available (the channel's key appears
    in the fixture's team text), add the fixture; otherwise, add a blank listing.
    The XML file is written to the absolute path defined by GUIDE_XML.
    """
    root = ET.Element('TVGuide')
    # Filter fixtures within the next two weeks
    fixtures = filter_next_two_weeks(fixtures)
    
    for channel in CHANNELS:
        channel_element = ET.SubElement(root, 'Channel', name=channel)
        # Use the channel's key (e.g., “Celtic” from “Celtic TV”) for matching
        key = channel.replace(" TV", "").lower()
        channel_fixtures = [fx for fx in fixtures if key in fx['teams'].lower()]
        
        if channel_fixtures:
            for fx in sorted(channel_fixtures, key=lambda f: f['date']):
                fixture_element = ET.SubElement(channel_element, 'Fixture')
                ET.SubElement(fixture_element, 'Date').text = fx['date'].strftime('%Y-%m-%d %H:%M')
                ET.SubElement(fixture_element, 'Teams').text = fx['teams']
        else:
            # Add a blank listing if no fixture is found for this channel
            ET.SubElement(channel_element, 'Fixture', status='blank')
    
    tree = ET.ElementTree(root)
    tree.write(GUIDE_XML, encoding='utf-8', xml_declaration=True)

def update_tv_guide():
    """
    Performs an endless loop: scrape fixtures, generate the guide, then sleep 24 hours.
    Updates run in a background thread.
    """
    while True:
        fixtures = scrape_fixtures(PREMIERSHIP_URL) + scrape_fixtures(CHAMPIONSHIP_URL)
        generate_tv_guide(fixtures)
        time.sleep(86400)  # 24 hours

@app.route('/guide.xml')
def serve_guide():
    """
    Serves the generated TV guide.
    Checks for file existence and returns a 404 if the file is not found.
    """
    if not os.path.exists(GUIDE_XML):
        return "Guide not available", 404
    return send_file(GUIDE_XML, mimetype='application/xml')

if __name__ == '__main__':
    # Generate the TV guide before starting the server
    fixtures = scrape_fixtures(PREMIERSHIP_URL) + scrape_fixtures(CHAMPIONSHIP_URL)
    generate_tv_guide(fixtures)
    
    # Start the guide update process in a background thread
    update_thread = threading.Thread(target=update_tv_guide, daemon=True)
    update_thread.start()
    
    # Run the Flask server on 0.0.0.0:5000
    app.run(host='0.0.0.0', port=5000)
