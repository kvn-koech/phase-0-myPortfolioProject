import os
import pytest
from app import app, db, ContactMessage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client

def test_contact_success(client):
    response = client.post('/api/contact', json={
        'name': 'Test User',
        'email': 'test@example.com',
        'message': 'Hello from test!'
    })
    assert response.status_code == 201
    assert response.get_json()['success'] is True

def test_contact_missing_fields(client):
    response = client.post('/api/contact', json={
        'name': 'Test User',
        # missing email and message
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False
    assert 'Missing required fields' in response.get_json()['error']

def test_contact_invalid_email(client):
    response = client.post('/api/contact', json={
        'name': 'Test User',
        'email': 'not-an-email',
        'message': 'Hello from test!'
    })
    assert response.status_code == 400
    assert response.get_json()['success'] is False
    assert 'Invalid email address' in response.get_json()['error']
