import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import logging

def generate_xmltv(fixtures):
    """
    Generate XMLTV data from a list of fixtures.

    Each fixture dict is expected to have:
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
        # fixture["name"] is something like "Celtic vs Dundee United"
        fixture_name = fixture.get("name", "")
        if " vs " not in fixture_name:
            logging.warning(f"Skipping unexpected fixture name: {fixture_name}")
            continue

        home_team, away_team = fixture_name.split(" vs ", 1)

        # Convert starting_at to datetime
        starting_at_str = fixture.get("starting_at", "")
        try:
            start_dt = datetime.strptime(starting_at_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logging.warning(f"Skipping fixture with invalid starting_at: {starting_at_str}")
            continue

        end_dt = start_dt + timedelta(minutes=120)  # 2 hours
        start_str = start_dt.strftime("%Y%m%d%H%M%S +0000")
        end_str = end_dt.strftime("%Y%m%d%H%M%S +0000")

        match_title = f"{home_team} vs {away_team}"

        for team in [home_team, away_team]:
            ch_id = team.lower().replace(" ", "_") + "_tv"
            if ch_id in channels:
                programme = ET.SubElement(
                    root, "programme",
                    {"start": start_str, "stop": end_str, "channel": ch_id}
                )
                ET.SubElement(programme, "title").text = match_title

    xml_data = ET.tostring(root, encoding="utf-8")
    xml_declaration = b'<?xml version="1.0" encoding="UTF-8"?>\n'
    return xml_declaration + xml_data
