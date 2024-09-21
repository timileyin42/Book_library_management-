# frontend_api/tests/test_users.py

import pytest
from models import User
from app import db
from flask import url_for

@pytest.fixture
def new_user():
    """Fixture to create a new user object."""
    user = User(
        email='uniqueuser@example.com',
        first_name='Unique',
        last_name='User'
    )
    return user

def test_create_user_success(client, new_user):
    """Test successful user creation."""
    response = client.post('/users', json={
        'email': new_user.email,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['email'] == new_user.email
    assert data['first_name'] == new_user.first_name
    assert data['last_name'] == new_user.last_name
    assert 'id' in data

def test_create_user_duplicate_email(client, new_user):
    """Test that creating a user with an existing email fails."""
    # First, create the user
    client.post('/users', json={
        'email': new_user.email,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name
    })
    
    # Attempt to create the same user again
    response = client.post('/users', json={
        'email': new_user.email,
        'first_name': 'Another',
        'last_name': 'User'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == 'User with this email already exists'

@pytest.mark.parametrize("missing_field, payload", [
    ('email', {'first_name': 'New', 'last_name': 'User'}),
    ('first_name', {'email': 'jane.doe@example.com', 'last_name': 'Doe'}),
    ('last_name', {'email': 'newuser@example.com', 'first_name': 'New'}),
])
def test_create_user_missing_fields(client, missing_field, payload):
    """Test that creating a user with missing required fields fails."""
    response = client.post('/users', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == f"{missing_field.replace('_', ' ').capitalize()} is required"

@pytest.mark.parametrize("invalid_email", [
    'invalidemail',          # Missing @ and domain
    'invalid@.com',          # Missing domain name
    'invalid@com',           # Missing top-level domain
    'invalid@domain.c',      # TLD too short
    '@no-local-part.com',    # Missing local part
    'no-at-symbol.com',      # Missing @
])
def test_create_user_invalid_email(client, invalid_email):
    """Test that creating a user with an invalid email format fails."""
    response = client.post('/users', json={
        'email': invalid_email,
        'first_name': 'Invalid',
        'last_name': 'Email'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'email' in data['message'].lower()

def test_create_user_invalid_data_types(client):
    """Test that creating a user with invalid data types fails."""
    # Email as a non-string type
    response = client.post('/users', json={
        'email': 12345,
        'first_name': 'Number',
        'last_name': 'User'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'email' in data['message'].lower()
    
    # first_name as a list instead of string
    response = client.post('/users', json={
        'email': 'valid.email@example.com',
        'first_name': ['First'],
        'last_name': 'User'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'first name' in data['message'].lower()
    
    # last_name as None
    response = client.post('/users', json={
        'email': 'another.valid@example.com',
        'first_name': 'Another',
        'last_name': None
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'last name' in data['message'].lower()

def test_create_user_extra_fields(client, new_user):
    """Test that creating a user with extra unexpected fields ignores them or returns an error."""
    response = client.post('/users', json={
        'email': new_user.email,
        'first_name': new_user.first_name,
        'last_name': new_user.last_name,
        'age': 30  # Extra field not defined in the schema
    })
    # Depending on implementation, either ignore extra fields or return an error
    # Here, assuming extra fields are ignored
    assert response.status_code == 201
    data = response.get_json()
    assert 'age' not in data

def test_create_user_invalid_json(client):
    """Test that creating a user with invalid JSON fails."""
    # Sending data as form data instead of JSON
    response = client.post('/users', data={
        'email': 'formdata@example.com',
        'first_name': 'Form',
        'last_name': 'Data'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data

def test_create_user_no_json(client):
    """Test that creating a user without JSON data fails."""
    response = client.post('/users')
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data

def test_create_user_empty_json(client):
    """Test that creating a user with empty JSON fails."""
    response = client.post('/users', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'message' in data

def test_create_user_invalid_email_domain(client):
    """Test that creating a user with an invalid email domain fails."""
    response = client.post('/users', json={
        'email': 'user@invalid_domain',
        'first_name': 'User',
        'last_name': 'InvalidDomain'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert 'email' in data['message'].lower()

