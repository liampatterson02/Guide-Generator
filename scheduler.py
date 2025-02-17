import logging
from apscheduler.schedulers.background import BackgroundScheduler
from fetcher import fetch_fixtures
from generator import generate_xmltv

class TVGuideData:
    """Holds the latest XMLTV data in memory."""
    xmltv = b""

tv_guide_data = TVGuideData()

def update_tv_guide():
    logging.info("Updating TV guide...")
    fixtures = fetch_fixtures()
    tv_guide_data.xmltv = generate_xmltv(fixtures)
    logging.info("TV guide update complete.")

def start_scheduler(interval_minutes):
    scheduler = BackgroundScheduler()
    scheduler.add_job(update_tv_guide, "interval", minutes=interval_minutes)
    scheduler.start()
    # Do an immediate update on startup
    update_tv_guide()
    return scheduler
