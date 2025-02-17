import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import xml.etree.ElementTree as ET
from flask import Flask, send_file
import threading

app = Flask(__name__)

# URLs to scrape fixtures from
PREMIERSHIP_URL = "https://spfl.co.uk/league/premiership/fixtures"
CHAMPIONSHIP_URL = "https://spfl.co.uk/league/championship/fixtures"

# List of channels to be included in the TV guide
CHANNELS = [
    "Aberdeen TV", "Celtic TV", "Dundee FC TV", "Dundee United TV",
    "Falkirk TV", "Hearts TV", "Hibernian TV", "Kilmarnock TV",
    "Livingston TV", "Motherwell TV", "Rangers TV", "Ross County TV",
    "St Johnstone TV", "St Mirren TV"
]

def scrape_fixtures(url):
    """
    Scrapes fixtures from the given URL.
    This function assumes that each fixture is contained within a <div class="fixture"> element,
    with a nested <span class="date-time"> element and a <span class="teams"> element.
    Adjust the selectors and date format as needed.
    """
    fixtures = []
    try:
        response = requests.get(url)
        if response.status_code != 200:
            return fixtures
        soup = BeautifulSoup(response.content, 'lxml')
    
        # Find fixture elements – adjust the class names if needed
        for fixture_div in soup.find_all('div', class_='fixture'):
            try:
                # Example: get date and time from a single span
                date_time_text = fixture_div.find('span', class_='date-time').text.strip()
                # Expected format e.g. "Saturday 03 October 2024 15:00"
                fixture_date = datetime.strptime(date_time_text, "%A %d %B %Y %H:%M")
                # Get teams text – adjust the selector if needed
                teams_text = fixture_div.find('span', class_='teams').text.strip()
                fixtures.append({
                    'date': fixture_date,
                    'teams': teams_text
                })
            except Exception:
                # Skip fixture elements with unexpected structure
                continue
    except Exception:
        pass

    return fixtures

def filter_next_two_weeks(fixtures):
    """
    Returns fixtures that are scheduled within the next 14 days.
    """
    now = datetime.now()
    two_weeks = now + timedelta(days=14)
    return [fixture for fixture in fixtures if now <= fixture['date'] <= two_weeks]

def generate_tv_guide(fixtures):
    """
    Generates an XML TV guide. For each channel (e.g., "Celtic TV"), it checks for fixtures where
    the team's name (i.e. the part before " TV") appears in the fixture's teams string (case insensitive).
    If fixtures exist, they are added under the channel element.
    Otherwise, a blank listing element is added.
    """
    root = ET.Element('TVGuide')
    
    # Filter fixtures for the next two weeks
    fixtures = filter_next_two_weeks(fixtures)
    
    for channel in CHANNELS:
        channel_element = ET.SubElement(root, 'Channel', name=channel)
        key = channel.replace(" TV", "").lower()
        # Find fixtures which mention this channel's key
        channel_fixtures = [fx for fx in fixtures if key in fx['teams'].lower()]
        
        if channel_fixtures:
            for fx in sorted(channel_fixtures, key=lambda f: f['date']):
                fixture_element = ET.SubElement(channel_element, 'Fixture')
                ET.SubElement(fixture_element, 'Date').text = fx['date'].strftime('%Y-%m-%d %H:%M')
                ET.SubElement(fixture_element, 'Teams').text = fx['teams']
        else:
            # Add a blank listing if no fixtures are available for this channel
            ET.SubElement(channel_element, 'Fixture', status='blank')

    tree = ET.ElementTree(root)
    tree.write('guide.xml', encoding='utf-8', xml_declaration=True)

def update_tv_guide():
    """
    Performs a daily update. This function scrapes fixtures from both URLs,
    generates the TV guide XML, and waits for 24 hours before re-running.
    """
    while True:
        # Scrape fixtures from both sources
        fixtures = scrape_fixtures(PREMIERSHIP_URL) + scrape_fixtures(CHAMPIONSHIP_URL)
        generate_tv_guide(fixtures)
        # You might also want to log or print status here.
        time.sleep(86400)  # Wait for 24 hours

@app.route('/guide.xml')
def serve_guide():
    """
    Serves the generated TV guide XML.
    """
    return send_file('guide.xml', mimetype='application/xml')

if __name__ == '__main__':
    # Start the update process in a background thread. It initially updates the guide.
    update_thread = threading.Thread(target=update_tv_guide, daemon=True)
    update_thread.start()
    
    # Optionally, run a one-time update before starting the server
    fixtures = scrape_fixtures(PREMIERSHIP_URL) + scrape_fixtures(CHAMPIONSHIP_URL)
    generate_tv_guide(fixtures)
    
    # Run the Flask development server on 0.0.0.0:5000
    app.run(host='0.0.0.0', port=5000)
