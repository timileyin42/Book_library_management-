import os
from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import logging
from logging.handlers import RotatingFileHandler

from errors import register_error_handlers

db = SQLAlchemy()
ma = Marshmallow()

def create_app():
    app = Flask(__name__)

    # Database Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'postgresql://user:password@localhost:5432/backend_db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize Extensions
    db.init_app(app)
    ma.init_app(app)

    # Enable CORS
    CORS(app)

    # Setup Logging
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/backend_api.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info("Backend API startup")

    # Register Error Handlers
    register_error_handlers(app)

    api = Api(app)

    # Register API Resources
    from routes.users import UserListResource, UserBorrowedBooksResource
    from routes.books import BookListResource, BookResource, UnavailableBooksResource

    api.add_resource(UserListResource, '/users')
    api.add_resource(UserBorrowedBooksResource, '/users/borrowed')
    api.add_resource(BookListResource, '/books')
    api.add_resource(BookResource, '/books/<int:book_id>')
    api.add_resource(UnavailableBooksResource, '/books/unavailable')

    # Create Database Tables
    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8001)

