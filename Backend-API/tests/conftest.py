# Backend-API/tests/conftest.py

import pytest
from app import create_app, db
from models import User, Book

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for each test module."""
    app = create_app()
    app.config['TESTING'] = True
    # Use an in-memory SQLite database for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Provide a test client for the app."""
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """Initialize the database with some users and books."""
    with app.app_context():
        # Create test users
        user1 = User(email="admin1@example.com", first_name="Admin", last_name="One")
        user2 = User(email="admin2@example.com", first_name="Admin", last_name="Two")
        db.session.add_all([user1, user2])

        # Create test books
        book1 = Book(
            title="Advanced Python Programming",
            author="Dr. Gabriele Lanaro",
            publisher="Packt Publishing",
            category="Programming"
        )
        book2 = Book(
            title="Database Design Principles",
            author="Brymes Smith",
            publisher="DataPress",
            category="Database"
        )
        db.session.add_all([book1, book2])

        db.session.commit()

        yield db  # Provide the fixture value

        # Clean up after tests
        db.session.remove()
        db.drop_all()

