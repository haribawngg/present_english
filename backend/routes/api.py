"""API routes. Registered at /api plus legacy root aliases by the factory."""
from flask import Blueprint, current_app, jsonify, request
from werkzeug.exceptions import BadRequest, ServiceUnavailable
from backend.validation import validate_prediction

api = Blueprint("api", __name__)


def service():
    return current_app.extensions["prediction_service"]


@api.before_request
def require_models():
    if not service().ready:
        raise ServiceUnavailable("Models unavailable. Run setup/training and restart backend.")


@api.get("/health")
def health():
    return jsonify(status="ready", backend="flask")


@api.get("/models")
def models():
    return jsonify(models=service().models, default="nb", labels=["ham", "spam"])


@api.get("/metrics")
def metrics():
    return jsonify(service().report)


@api.post("/predict")
def predict():
    messages, model, explain = validate_prediction(request.get_json(silent=True))
    if model not in service().models:
        raise BadRequest("Unknown/untrained model; see GET /api/models.")
    return jsonify(predictions=service().predict(messages, model, explain))
