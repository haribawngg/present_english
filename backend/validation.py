"""HTTP request validation, separated from inference and Flask routes."""
from werkzeug.exceptions import UnprocessableEntity


def validate_prediction(body):
    if not isinstance(body, dict):
        raise UnprocessableEntity("Expected a JSON object.")
    messages = body.get("messages")
    model = body.get("model", "nb")
    explain = body.get("explain", False)
    if (not isinstance(messages, list) or not 1 <= len(messages) <= 100 or
            any(not isinstance(text, str) or not text.strip() or len(text) > 5000 for text in messages)):
        raise UnprocessableEntity("Send 1-100 nonblank messages, each at most 5000 characters.")
    if not isinstance(model, str) or not isinstance(explain, bool):
        raise UnprocessableEntity("model must be a string; explain must be boolean.")
    return messages, model, explain
