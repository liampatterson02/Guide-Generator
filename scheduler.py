import logging
from apscheduler.schedulers.background import BackgroundScheduler
from fetcher import fetch_fixtures
from generator import generate_xmltv
from config import UPDATE_INTERVAL_MINUTES, ENABLE_M3U
from generator import generate_m3u

class TVGuideData:
    """
    Holds the latest fixture data and generated outputs (XMLTV, M3U).
    """
    xmltv = b""
    m3u = ""

tv_guide_data = TVGuideData()

def update_tv_guide():
    logging.info("Updating TV guide...")
    fixtures = fetch_fixtures()
    tv_guide_data.xmltv = generate_xmltv(fixtures)
    if ENABLE_M3U:
        tv_guide_data.m3u = generate_m3u(fixtures)
    else:
        tv_guide_data.m3u = ""
    logging.info("TV guide update complete.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_tv_guide, "interval", minutes=UPDATE_INTERVAL_MINUTES)
    scheduler.start()
    # Do an immediate update on startup
    update_tv_guide()
    return scheduler
