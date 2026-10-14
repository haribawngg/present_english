from flask import jsonify, request
from werkzeug.exceptions import HTTPException


def register_middleware(app):
    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(detail=error.description), error.code

    @app.after_request
    def headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        if request.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
        return response
