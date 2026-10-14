from flask import Blueprint, jsonify, send_from_directory
from backend.config import FRONTEND_DIST

frontend = Blueprint("frontend", __name__)


@frontend.get("/")
def index():
    if not (FRONTEND_DIST / "index.html").is_file():
        return jsonify(detail="Build frontend first: npm --prefix frontend run build"), 503
    return send_from_directory(FRONTEND_DIST, "index.html")


@frontend.get("/assets/<path:filename>")
def assets(filename):
    return send_from_directory(FRONTEND_DIST / "assets", filename)
