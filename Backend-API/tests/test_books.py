# Backend-API/tests/test_books.py

import pytest

def test_list_books_empty(client):
    """Test listing books when none are available."""
    response = client.get('/books')
    assert response.status_code == 200
    assert response.get_json() == []

def test_add_book_success(client):
    """Test successfully adding a new book."""
    response = client.post('/books', json={
        'title': 'Machine Learning Basics',
        'author': 'Alice Johnson',
        'publisher': 'AI Publishers',
        'category': 'Technology'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['title'] == 'Machine Learning Basics'
    assert data['available'] == True

def test_add_book_missing_fields(client):
    """Test adding a book with missing required fields."""
    response = client.post('/books', json={
        'title': 'Incomplete Book',
        'author': 'Bob Builder'
        # Missing 'publisher' and 'category'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'publisher' in data['message']
    assert 'category' in data['message']

def test_remove_book_success(client, init_database):
    """Test successfully removing a book."""
    # Add a book to remove
    response = client.post('/books', json={
        'title': 'Temporary Book',
        'author': 'Temp Author',
        'publisher': 'Temp Publisher',
        'category': 'Temp Category'
    })
    assert response.status_code == 201
    book_id = response.get_json()['id']

    # Remove the book
    response = client.delete(f'/books/{book_id}')
    assert response.status_code == 204

    # Verify removal
    response = client.get(f'/books/{book_id}')
    assert response.status_code == 404

def test_remove_book_not_found(client):
    """Test removing a non-existent book."""
    response = client.delete('/books/9999')  # Assuming 9999 does not exist
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == 'Resource not found'

def test_list_unavailable_books(client, init_database):
    """Test listing unavailable books with return dates."""
    # Borrow a book
    response = client.post('/books/2/borrow', json={
        'user_id': 1,  # Assuming user1 has ID 1
        'days': 10
    })
    assert response.status_code == 200

    # List unavailable books
    response = client.get('/books/unavailable')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['title'] == 'Database Design Principles'
    assert data[0]['available'] == False
    assert data[0]['borrowed_until'] is not None

