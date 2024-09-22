# Backend-API/tests/test_users.py

def test_list_users_empty(client):
    """Test listing users when none are enrolled."""
    response = client.get('/users')
    assert response.status_code == 200
    assert response.get_json() == []

def test_list_users(client, init_database):
    """Test listing all enrolled users."""
    response = client.get('/users')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['email'] == "admin1@example.com"
    assert data[1]['email'] == "admin2@example.com"

def test_list_borrowed_books_empty(client, init_database):
    """Test listing users with no borrowed books."""
    response = client.get('/users/borrowed')
    assert response.status_code == 200
    assert response.get_json() == []

def test_list_borrowed_books(client, init_database):
    """Test listing users who have borrowed books."""
    # Borrow a book for user1
    response = client.post('/books/1/borrow', json={
        'user_id': 1,  # Assuming user1 has ID 1
        'days': 7
    })
    assert response.status_code == 200

    response = client.get('/users/borrowed')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['email'] == "admin1@example.com"
    assert len(data[0]['borrowed_books']) == 1
    assert data[0]['borrowed_books'][0]['title'] == "Advanced Python Programming"

