import logging
import os
from flask import Flask, Response, jsonify, send_file
from scheduler import start_scheduler, tv_guide_data
from config import LOG_FILE, ENABLE_M3U

app = Flask(__name__)

# Set up logging
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

@app.route("/guide.m3u")
def tvguide_m3u():
    """Return an M3U playlist (if enabled)."""
    if not ENABLE_M3U:
        return ("M3U generation is disabled.", 503)
    if tv_guide_data.m3u:
        return Response(tv_guide_data.m3u, mimetype="audio/x-mpegurl")
    return ("No M3U data available.", 503)

@app.route("/monitor")
def monitor():
    """
    Return a basic JSON response indicating whether
    the TV guide data is loaded and how large it is.
    """
    size_xmltv = len(tv_guide_data.xmltv)
    size_m3u = len(tv_guide_data.m3u)
    return jsonify({
        "xmltv_size_bytes": size_xmltv,
        "m3u_size_bytes": size_m3u,
        "m3u_enabled": ENABLE_M3U
    })

@app.route("/logs")
def logs():
    """Serve the log file content for debugging."""
    if os.path.exists(LOG_FILE):
        return send_file(LOG_FILE, mimetype="text/plain")
    return ("Log file not found.", 404)

if __name__ == "__main__":
    # Start the background scheduler
    scheduler = start_scheduler()
    # Run Flask
    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        scheduler.shutdown()
