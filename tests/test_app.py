# tests/test_app.py
import pytest
from app.app import app  # Import the Flask instance from main.py

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Welcome to the Chatbot!" in response.data

def test_chat(client):
    response = client.post('/get_response', data=dict(user_input="Hello"))
    assert response.status_code == 200
    assert b"Hello" in response.data
