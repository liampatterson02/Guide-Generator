import logging
import os
from flask import Flask, Response, jsonify, send_file
from scheduler import start_scheduler, tv_guide_data
from config import UPDATE_INTERVAL_MINUTES, LOG_FILE

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

@app.route("/tvguide.xml")
def tvguide_xml():
    """Return the latest XMLTV data."""
    if tv_guide_data.xmltv:
        return Response(tv_guide_data.xmltv, mimetype="application/xml")
    return ("No TV guide data available.", 503)

@app.route("/monitor")
def monitor():
    """
    Return a basic JSON response indicating the status
    of the TV guide data.
    """
    size_xmltv = len(tv_guide_data.xmltv)
    return jsonify({
        "xmltv_size_bytes": size_xmltv,
        "update_interval_minutes": UPDATE_INTERVAL_MINUTES
    })

@app.route("/logs")
def logs():
    """Serve the log file content for debugging."""
    if os.path.exists(LOG_FILE):
        return send_file(LOG_FILE, mimetype="text/plain")
    return ("Log file not found.", 404)

if __name__ == "__main__":
    scheduler = start_scheduler(UPDATE_INTERVAL_MINUTES)
    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        scheduler.shutdown()
