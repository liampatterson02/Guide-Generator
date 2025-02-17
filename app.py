import os
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import threading
import xml.etree.ElementTree as ET
from flask import Flask, send_file

app = Flask(__name__)

# Absolute path for the TV guide file
GUIDE_XML = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'guide.xml')

# Fixture page URLs
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
    Scrapes fixtures from a SPFL fixtures page by processing the plain text.
    The method expects the following three-line pattern:
      • A date line (e.g. "Saturday 15th February 2025")
      • A time line (starting with "- ", e.g. "- 15:00")
      • A teams line (starting with "- ", e.g. "- Celtic v Dundee United")
    It removes ordinal suffixes from the date before combining it with the time.
    """
    fixtures = []
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception:
        return fixtures

    soup = BeautifulSoup(response.content, 'lxml')
    # Extract lines of text from the page
    lines = soup.get_text(separator="\n").splitlines()
    # Remove extra whitespace and blank lines
    lines = [line.strip() for line in lines if line.strip()]

    # Regex pattern to match a date string e.g. "Saturday 15th February 2025"
    date_pattern = re.compile(r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4}$')
    
    i = 0
    while i < len(lines) - 2:
        if date_pattern.match(lines[i]):
            try:
                # Expected next line: time prefixed with "- "
                time_line = lines[i+1]
                if not time_line.startswith("- "):
                    i += 1
                    continue
                time_str = time_line[2:].strip()
                
                # Expected following line: teams prefixed with "- "
                teams_line = lines[i+2]
                if not teams_line.startswith("- "):
                    i += 1
                    continue
                teams_str = teams_line[2:].strip()
                
                # Remove suffixes like 'th', 'st', 'nd', 'rd' from the date
                clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', lines[i])
                dt_str = f"{clean_date} {time_str}"
                fixture_date = datetime.strptime(dt_str, "%A %d %B %Y %H:%M")
                fixtures.append({'date': fixture_date, 'teams': teams_str})
                i += 3
                continue
            except Exception:
                i += 1
        else:
            i += 1
    return fixtures

def filter_next_two_weeks(fixtures):
    """
    Returns only fixtures that fall within the next 14 days.
    """
    now = datetime.now()
    two_weeks = now + timedelta(days=14)
    return [fx for fx in fixtures if now <= fx['date'] <= two_weeks]

def generate_tv_guide(fixtures):
    """
    Generates an XML TV guide.
    For each channel (e.g. "Celtic TV"), the app checks if any fixture's teams value (case-insensitive)
    contains the corresponding team name (i.e. "Celtic"). If fixtures exist, they are added in order;
    if not, a blank fixture listing is added.
    """
    root = ET.Element('TVGuide')
    fixtures = filter_next_two_weeks(fixtures)
    
    for channel in CHANNELS:
        channel_element = ET.SubElement(root, 'Channel', name=channel)
        key = channel.replace(" TV", "").lower()
        channel_fixtures = [fx for fx in fixtures if key in fx['teams'].lower()]
        if channel_fixtures:
            for fx in sorted(channel_fixtures, key=lambda f: f['date']):
                fixture_element = ET.SubElement(channel_element, 'Fixture')
                ET.SubElement(fixture_element, 'Date').text = fx['date'].strftime('%Y-%m-%d %H:%M')
                ET.SubElement(fixture_element, 'Teams').text = fx['teams']
        else:
            ET.SubElement(channel_element, 'Fixture', status='blank')
    
    tree = ET.ElementTree(root)
    tree.write(GUIDE_XML, encoding='utf-8', xml_declaration=True)

def update_tv_guide():
    """
    In a background thread the app continuously:
      • Scrapes fixtures from both the Premiership and Championship pages,
      • Generates the TV guide XML,
      • Then waits 24 hours before repeating.
    """
    while True:
        all_fixtures = scrape_fixtures(PREMIERSHIP_URL) + scrape_fixtures(CHAMPIONSHIP_URL)
        generate_tv_guide(all_fixtures)
        time.sleep(86400)  # 24 hours

@app.route('/guide.xml')
@app.route('/tvguide.xml')
def serve_guide():
    """
    Serves the generated TV guide XML.
    If the guide file is missing, it creates a default one with blank fixtures.
    """
    if not os.path.exists(GUIDE_XML):
        generate_tv_guide([])
    return send_file(GUIDE_XML, mimetype='application/xml')

if __name__ == '__main__':
    # Pre-generate guide once on startup
    all_fixtures = scrape_fixtures(PREMIERSHIP_URL) + scrape_fixtures(CHAMPIONSHIP_URL)
    generate_tv_guide(all_fixtures)
    
    # Start the background updater thread
    update_thread = threading.Thread(target=update_tv_guide, daemon=True)
    update_thread.start()
    
    # Run the Flask server on port 5000 (accessible at /guide.xml or /tvguide.xml)
    app.run(host='0.0.0.0', port=5000)
