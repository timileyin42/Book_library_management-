# frontend_api/tests/test_books.py

import pytest
from models import User, Book
from app import db
from datetime import datetime, timedelta

@pytest.fixture
def new_user():
    """Fixture to create a new user object."""
    user = User(
        email='borrower@example.com',
        first_name='Borrow',
        last_name='User'
    )
    return user

@pytest.fixture
def new_book():
    """Fixture to create a new book object."""
    book = Book(
        title='Sample Book Title',
        author='Sample Author',
        publisher='Sample Publisher',
        category='Sample Category'
    )
    return book

def test_list_books_empty(client):
    """Test that listing books when none are available returns an empty list."""
    response = client.get('/books')
    assert response.status_code == 200
    data = response.get_json()
    assert data == []

def test_add_and_list_books(client):
    """Test adding books directly to the database and listing them."""
    # Add books directly to the database
    with client.application.app_context():
        book1 = Book(
            title='The C Programming Language',
            author='Brain W.Kernighan',
            publisher='Prentice Hall Software Series',
            category='Technology'
        )
        book2 = Book(
            title='Beginning Programming with C for Dummies',
            author='Dan Gookin',
            publisher='John Wiley & Sons, Inc., Hoboken',
            category='Technology'
        )
        db.session.add(book1)
        db.session.add(book2)
        db.session.commit()

    # List all available books
    response = client.get('/books')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    # Verify the books are correctly listed
    titles = [book['title'] for book in data]
    assert 'The C Programming Language' in titles
    assert 'Beginning Programming with C for Dummies' in titles

@pytest.mark.parametrize("invalid_field, invalid_value, expected_message", [
    ('publisher', '', 'Publisher is required'),
    ('category', '', 'Category is required'),
])
def test_add_book_missing_fields(client, invalid_field, invalid_value, expected_message):
    """Test adding a book with missing required fields fails."""
    valid_payload = {
        'title': 'Valid Book Title',
        'author': 'Valid Author',
        'publisher': 'Valid Publisher',
        'category': 'Valid Category'
    }
    payload = valid_payload.copy()
    payload[invalid_field] = invalid_value
    response = client.post('/books', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert expected_message.lower() in data['message'].get(invalid_field, '').lower()

@pytest.mark.parametrize("invalid_data_type, field, value", [
    ('integer', 'title', 123),
    ('list', 'author', ['Author One']),
    ('none', 'publisher', None),
    ('boolean', 'category', True),
])
def test_add_book_invalid_data_types(client, invalid_data_type, field, value):
    """Test adding a book with invalid data types for fields fails."""
    payload = {
        'title': 'Another Valid Title',
        'author': 'Another Valid Author',
        'publisher': 'Another Valid Publisher',
        'category': 'Another Valid Category'
    }
    payload[field] = value
    response = client.post('/books', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert field.replace('_', ' ') in data['message'].lower()

def test_add_book_extra_fields(client):
    """Test adding a book with extra unexpected fields is handled appropriately."""
    payload = {
        'title': 'Extra Field Book',
        'author': 'Extra Author',
        'publisher': 'Extra Publisher',
        'category': 'Extra Category',
        'isbn': '123-4567890123'  # Extra field not defined in the schema
    }
    response = client.post('/books', json=payload)
    # Assuming extra fields are ignored and the book is created successfully
    assert response.status_code == 201
    data = response.get_json()
    assert 'isbn' not in data

def test_add_book_invalid_json(client):
    """Test adding a book with invalid JSON payload fails."""
    # Sending data as form data instead of JSON
    response = client.post('/books', data={
        'title': 'Form Data Book',
        'author': 'Form Author',
        'publisher': 'Form Publisher',
        'category': 'Form Category'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data

def test_add_book_no_json(client):
    """Test adding a book without JSON data fails."""
    response = client.post('/books')
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data

def test_add_book_empty_json(client):
    """Test adding a book with empty JSON payload fails."""
    response = client.post('/books', json={})
    assert response.status_code == 400
    data = response.get_json()
    # Expect messages for all required fields
    assert 'title' in data['message']
    assert 'author' in data['message']
    assert 'publisher' in data['message']
    assert 'category' in data['message']

def test_filter_books(client):
    """Test filtering books by publisher and category."""
    # Add books directly to the database
    with client.application.app_context():
        book1 = Book(
            title='The C Programming Language',
            author='Brain W.Kernighan',
            publisher='Prentice Hall Software Series',
            category='Technology'
        )
        book2 = Book(
            title='Beginning Programming with C for Dummies',
            author='Dan Gookin',
            publisher='John Wiley & Sons, Inc., Hoboken',
            category='Technology'
        )
        book3 = Book(
            title='The Obstacle Is The Way',
            author='Ryan Holiday',
            publisher='The Penguin Group Penguin Group',
            category='Philosophy'
        )
        db.session.add_all([book1, book2, book3])
        db.session.commit()

    # Filter by publisher
    response = client.get('/books', query_string={'publisher': 'Prentice Hall Software Series'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['publisher'] == 'Prentice Hall Software Series'

    # Filter by category
    response = client.get('/books', query_string={'category': 'Technology'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    categories = [book['category'] for book in data]
    assert all(category == 'Technology' for category in categories)

    # Filter by publisher and category
    response = client.get('/books', query_string={'publisher': 'John Wiley & Sons, Inc., Hoboken', 'category': 'Technology'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['publisher'] == 'John Wiley & Sons, Inc., Hoboken'
    assert data[0]['category'] == 'Technology'

@pytest.mark.parametrize("invalid_filter, value", [
    ('publisher', 'Non-Existent Publisher'),
    ('category', 'Non-Existent Category'),
])
def test_filter_books_no_results(client, invalid_filter, value):
    """Test filtering books that do not match any records."""
    # Add a sample book
    with client.application.app_context():
        book = Book(
            title='Existing Book',
            author='Existing Author',
            publisher='Existing Publisher',
            category='Existing Category'
        )
        db.session.add(book)
        db.session.commit()

    # Apply filter that yields no results
    response = client.get('/books', query_string={invalid_filter: value})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 0

def test_get_single_book(client):
    """Test retrieving a single book by ID."""
    # Add a book directly to the database
    with client.application.app_context():
        book = Book(
            title='Learning SQL',
            author='Alice Johnson',
            publisher='DataBooks',
            category='Database'
        )
        db.session.add(book)
        db.session.commit()
        book_id = book.id

    # Retrieve the book by ID
    response = client.get(f'/books/{book_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Learning SQL'
    assert data['author'] == 'Alice Johnson'
    assert data['publisher'] == 'DataBooks'
    assert data['category'] == 'Database'

    # Attempt to retrieve a non-existent book
    response = client.get('/books/non-existent-id')
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Book not found or not available'

@pytest.mark.parametrize("invalid_book_id", [
    '',  # Empty ID
    'invalid-id-format',  # Invalid format
    '12345678-1234-5678-1234-567812345678',  # Assuming UUID format but not present
])
def test_get_single_book_invalid_id(client, invalid_book_id):
    """Test retrieving a book with invalid or non-existent ID formats."""
    response = client.get(f'/books/{invalid_book_id}')
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Book not found or not available'

def test_borrow_book_success(client, new_user, new_book):
    """Test successfully borrowing a book."""
    # Add user and book to the database
    with client.application.app_context():
        db.session.add(new_user)
        db.session.add(new_book)
        db.session.commit()
        user_id = new_user.id
        book_id = new_book.id

    # Borrow the book
    response = client.post(f'/books/{book_id}/borrow', json={
        'user_id': user_id,
        'days': 14
    })
    assert response.status_code == 200
    data = response.get_json()
    assert 'borrowed until' in data['message']

    # Verify the book is no longer available
    response = client.get('/books')
    data = response.get_json()
    assert all(book['id'] != book_id for book in data)

def test_borrow_book_already_borrowed(client, new_user, new_book):
    """Test borrowing a book that has already been borrowed."""
    # Add user and book to the database and borrow the book
    with client.application.app_context():
        db.session.add(new_user)
        db.session.add(new_book)
        db.session.commit()
        user_id = new_user.id
        book_id = new_book.id

        # First borrow
        new_book.available = False
        new_book.borrowed_by = user_id
        new_book.borrowed_until = datetime.utcnow().date() + timedelta(days=14)
        db.session.commit()

    # Attempt to borrow the same book again
    response = client.post(f'/books/{book_id}/borrow', json={
        'user_id': user_id,
        'days': 7
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'Book not available for borrowing'

def test_borrow_book_invalid_user(client, new_book):
    """Test borrowing a book with an invalid user ID."""
    # Add book to the database
    with client.application.app_context():
        db.session.add(new_book)
        db.session.commit()
        book_id = new_book.id

    # Attempt to borrow with invalid user ID
    response = client.post(f'/books/{book_id}/borrow', json={
        'user_id': 'invalid-user-id',
        'days': 7
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'User not found'

@pytest.mark.parametrize("invalid_days", [
    -1,    # Negative days
    0,     # Zero days
    'seven',  # Non-integer days
    1.5,   # Float days
    None,  # Missing days
])
def test_borrow_book_invalid_days(client, new_user, new_book, invalid_days):
    """Test borrowing a book with invalid 'days' parameter."""
    # Add user and book to the database
    with client.application.app_context():
        db.session.add(new_user)
        db.session.add(new_book)
        db.session.commit()
        user_id = new_user.id
        book_id = new_book.id

    # Prepare payload
    payload = {
        'user_id': user_id,
        'days': invalid_days
    }
    # Remove 'days' if it is None to simulate missing field
    if invalid_days is None:
        payload.pop('days')

    response = client.post(f'/books/{book_id}/borrow', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert 'days' in data['message'].lower()

def test_borrow_book_extra_fields(client, new_user, new_book):
    """Test borrowing a book with extra unexpected fields."""
    # Add user and book to the database
    with client.application.app_context():
        db.session.add(new_user)
        db.session.add(new_book)
        db.session.commit()
        user_id = new_user.id
        book_id = new_book.id

    # Prepare payload with an extra field
    payload = {
        'user_id': user_id,
        'days': 7,
        'extra_field': 'extra_value'
    }

    response = client.post(f'/books/{book_id}/borrow', json=payload)
    # Assuming extra fields are ignored and the borrow is processed successfully
    assert response.status_code == 200
    data = response.get_json()
    assert 'borrowed until' in data['message']

def test_borrow_book_missing_fields(client, new_book):
    """Test borrowing a book with missing required fields."""
    # Add book to the database without a user
    with client.application.app_context():
        db.session.add(new_book)
        db.session.commit()
        book_id = new_book.id

    # Missing 'user_id'
    response = client.post(f'/books/{book_id}/borrow', json={
        'days': 7
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'user_id' in data['message'].get('user_id', '').lower()

    # Missing 'days'
    response = client.post(f'/books/{book_id}/borrow', json={
        'user_id': 'some-user-id'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'days' in data['message'].get('days', '').lower()

def test_borrow_book_invalid_json(client, new_user, new_book):
    """Test borrowing a book with invalid JSON payload fails."""
    # Add user and book to the database
    with client.application.app_context():
        db.session.add(new_user)
        db.session.add(new_book)
        db.session.commit()
        user_id = new_user.id
        book_id = new_book.id

    # Sending data as form data instead of JSON
    response = client.post(f'/books/{book_id}/borrow', data={
        'user_id': user_id,
        'days': 7
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data

def test_borrow_book_no_json(client):
    """Test borrowing a book without JSON data fails."""
    response = client.post('/books/some-book-id/borrow')
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data

def test_borrow_book_empty_json(client):
    """Test borrowing a book with empty JSON payload fails."""
    response = client.post('/books/some-book-id/borrow', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data

