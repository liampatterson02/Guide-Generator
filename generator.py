import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import logging

def generate_xmltv(fixtures):
    """
    Generate XMLTV data from a list of fixtures.
    Each fixture is expected to have:
      - 'name': e.g. 'Celtic vs Dundee United'
      - 'starting_at': e.g. '2025-02-15 15:00:00'
    """
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

    # Create <channel> elements
    for channel_id, display_name in channels.items():
        channel_elem = ET.SubElement(root, "channel", {"id": channel_id})
        ET.SubElement(channel_elem, "display-name").text = display_name

    # Create <programme> elements
    for fixture in fixtures:
        try:
            home_team, away_team = fixture["name"].split(" vs ")
        except ValueError:
            # If the 'name' field isn't in the expected format, skip
            logging.warning(f"Skipping fixture with unexpected name: {fixture.get('name')}")
            continue

        # Convert starting_at to a datetime
        try:
            start_dt = datetime.strptime(fixture["starting_at"], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logging.warning(f"Skipping fixture with invalid starting_at: {fixture.get('starting_at')}")
            continue

        end_dt = start_dt + timedelta(minutes=120)  # 2 hours

        # Format times for XMLTV: YYYYMMDDHHMMSS +0000
        start_str = start_dt.strftime("%Y%m%d%H%M%S +0000")
        end_str = end_dt.strftime("%Y%m%d%H%M%S +0000")

        match_title = f"{home_team} vs {away_team}"
        # Identify the channel IDs
        for team in [home_team, away_team]:
            ch_id = team.lower().replace(" ", "_") + "_tv"
            if ch_id in channels:
                programme_elem = ET.SubElement(
                    root, "programme",
                    {
                        "start": start_str,
                        "stop": end_str,
                        "channel": ch_id
                    }
                )
                ET.SubElement(programme_elem, "title").text = match_title

    xml_data = ET.tostring(root, encoding="utf-8")
    xml_declaration = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    return xml_declaration + xml_data

def generate_m3u(fixtures):
    """
    Generate a basic M3U playlist that lists the channels as M3U entries.
    This is a simplistic example for demonstration.
    """
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

    # Typically M3U lines: #EXTM3U, #EXTINF:-1 tvg-id="..." tvg-name="...", etc.
    lines = ["#EXTM3U"]
    for ch_id, display_name in channels.items():
        # In a real setup, you'd link to actual streams. Here we just show placeholders.
        lines.append(f'#EXTINF:-1 tvg-id="{ch_id}" group-title="Scottish Football", {display_name}')
        lines.append(f"http://example.com/stream/{ch_id}")
    return "\n".join(lines) + "\n"
