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
    The expected pattern is:
      • A date line (e.g. "Saturday 15th February 2025")
      • A time line starting with "- " (e.g. "- 15:00")
      • A teams line starting with "- " (e.g. "- Celtic v Dundee United")
    Ordinal suffixes are removed from the date before combining with the time.
    """
    fixtures = []
    # Use a common browser user-agent to avoid potential blocking
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Error accessing {url}: {e}")
        return fixtures

    soup = BeautifulSoup(response.content, 'lxml')
    # Extract all non-empty lines from the page's text
    lines = [line.strip() for line in soup.get_text(separator="\n").splitlines() if line.strip()]

    # Regex pattern to match a date string, e.g. "Saturday 15th February 2025"
    date_pattern = re.compile(
        r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4}$'
    )
    i = 0
    while i < len(lines) - 2:
        # Look for a date line matching the expected pattern
        if date_pattern.match(lines[i]):
            try:
                # Expect the next two lines to contain time and teams (both prefixed by "- ")
                time_line = lines[i + 1]
                teams_line = lines[i + 2]
                if not (time_line.startswith("- ") and teams_line.startswith("- ")):
                    i += 1
                    continue

                time_str = time_line[2:].strip()
                teams_str = teams_line[2:].strip()

                # Remove ordinal suffixes (st, nd, rd, th) from the date string
                clean_date = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', lines[i])
                dt_str = f"{clean_date} {time_str}"
                fixture_date = datetime.strptime(dt_str, "%A %d %B %Y %H:%M")
                fixtures.append({
                    'date': fixture_date,
                    'teams': teams_str
                })
                # Skip ahead past these three lines
                i += 3
                continue
            except Exception as e:
                print(f"Error parsing fixture block starting at line {i}: {e}")
                i += 1
        else:
            i += 1

    # Debug: print the fixtures found
    print(f"Scraped {len(fixtures)} fixtures from {url}")
    for fx in fixtures:
        print(f"  - {fx['date']} : {fx['teams']}")

    return fixtures

def filter_next_two_weeks(fixtures):
    """
    Returns only fixtures scheduled from now up to 14 days ahead.
    """
    now = datetime.now()
    two_weeks = now + timedelta(days=14)
    return [fx for fx in fixtures if now <= fx['date'] <= two_weeks]

def generate_tv_guide(fixtures):
    """
    Generates an XML TV guide.
    For each channel, it adds a fixture element for any fixture whose teams text (lowercased)
    contains the channel's key (channel name without " TV"). If no fixture is found, a blank fixture is added.
    The XML is saved to the absolute path defined in GUIDE_XML.
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
                ET.SubElement
