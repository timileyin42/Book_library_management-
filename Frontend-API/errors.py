from flask import jsonify
from werkzeug.exceptions import HTTPException

def register_error_handlers(app):
    """Register global error handlers for the Flask app."""

    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        response = e.get_response()
        response.data = jsonify({
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }).data
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the exception
        app.logger.error(f"Unhandled Exception: {e}")
        
        # Return a generic error message
        return jsonify({
            "code": 500,
            "name": "Internal Server Error",
            "description": "An unexpected error has occurred."
        }), 500

