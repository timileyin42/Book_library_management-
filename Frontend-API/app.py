# frontend_api/app.py

import os
import logging
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from logging.handlers import RotatingFileHandler

from errors import register_error_handlers

# Initialize extensions
db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URI', 
        'postgresql://user:password@localhost:5432/frontend_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Extensions
    db.init_app(app)
    ma.init_app(app)

    # Enable CORS for all routes
    CORS(app)

    # Setup Logging
    setup_logging(app)

    # Register Error Handlers
    register_error_handlers(app)

    # Create and register API
    api = Api(app)
    register_routes(api)

    # Create Database Tables if they don't exist
    with app.app_context():
        db.create_all()

    return app

def setup_logging(app):
    """Set up logging configuration."""
    log_directory = 'logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)  # Use makedirs for potential nested directories
    file_handler = RotatingFileHandler(
        os.path.join(log_directory, 'frontend_api.log'), 
        maxBytes=10240, 
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Frontend API startup")

def register_routes(api):
    """Register API resources with the Flask-Restful API."""
    from routes.users import UserListResource
    from routes.books import BookListResource, BookResource, BookBorrowResource

    api.add_resource(UserListResource, '/users')
    api.add_resource(BookListResource, '/books')
    api.add_resource(BookResource, '/books/<string:book_id>')
    api.add_resource(BookBorrowResource, '/books/<string:book_id>/borrow')

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000)

