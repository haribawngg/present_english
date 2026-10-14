"""Application factory: configure, load services, and register blueprints."""
import os
from flask import Flask
from backend.config import DEFAULT_MODEL_DIR, MAX_CONTENT_LENGTH
from backend.middleware import register_middleware
from backend.routes.api import api
from backend.routes.frontend import frontend
from backend.services.prediction import PredictionService


def create_app(artifact_dir=None):
    app = Flask(__name__, static_folder=None)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    directory = artifact_dir or os.environ.get("MODEL_DIR", str(DEFAULT_MODEL_DIR))
    app.extensions["prediction_service"] = PredictionService(directory)
    register_middleware(app)
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(api, name="legacy_api")
    app.register_blueprint(frontend)
    return app
