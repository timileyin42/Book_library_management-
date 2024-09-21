# frontend_api/tests/conftest.py

import pytest
from app import create_app, db
from models import User, Book

@pytest.fixture(scope='module')
def app():
    """Create a Flask app configured for testing."""
    app = create_app()
    app.config['TESTING'] = True
    # Use an in-memory SQLite database for testing purposes
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        # Create tables for the database schema before yielding the app
        db.create_all()
        yield app
        # Clean up the database and remove session after all tests in the module
        db.session.remove()
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    """Provide a test client for the Flask app."""
    return app.test_client()

@pytest.fixture(scope='function')
def init_database(app):
    """Initialize the database with some default values."""
    with app.app_context():
        # Create default test users
        user1 = User(email="john.doe@example.com", first_name="John", last_name="Doe")
        user2 = User(email="jane.smith@example.com", first_name="Jane", last_name="Smith")
        db.session.add_all([user1, user2])
        
        # Create default test books
        book1 = Book(
            title="The Pragmatic Programmer",
            author="Andrew Hunt",
            publisher="Addison-Wesley",
            category="Technology"
        )
        book2 = Book(
            title="Clean Code",
            author="Robert C. Martin",
            publisher="Prentice Hall",
            category="Technology"
        )
        db.session.add_all([book1, book2])
        
        db.session.commit()

        yield db  # This yields a clean database after every function

        # Clean up database after the test function
        db.session.remove()
        db.drop_all()


