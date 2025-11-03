import pytest
import os
from app import create_app, db
from app.models import User
from app.modules import Professional
from config import TestingConfig

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create the app with test config
    app = create_app(TestingConfig)
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        
        # Create a test user
        user = User(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        user.set_password('testpass123')
        
        # Create a test professional
        professional = Professional(
            user=user,
            full_name='Test Professional',
            profession='Tester',
            bio='Test bio',
            location='Test Location'
        )
        
        db.session.add(user)
        db.session.add(professional)
        db.session.commit()
    
    yield app
    
    # Clean up after the test
    with app.app_context():
        db.session.remove()
        db.drop_all()
        db.get_engine(app).dispose()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email='test@example.com', password='testpass123'):
        return self._client.post(
            '/auth/login',
            data={'email': email, 'password': password},
            # Add follow_redirects if the login redirects on success
            follow_redirects=True
        )
    
    def logout(self):
        return self._client.get('/logout', follow_redirects=True)

@pytest.fixture
def auth(client):
    return AuthActions(client)

def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Welcome' in response.data  # Adjust based on your home page content

def test_login_page(client):
    """Test that the login page loads successfully."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'Login' in response.data  # Adjust based on your login page

def test_successful_login(client, auth):
    """Test login with valid credentials."""
    response = auth.login()
    assert response.status_code == 200
    # Adjust these assertions based on your app's behavior after login
    assert b'Dashboard' in response.data or b'Logout' in response.data

def test_failed_login(client):
    """Test login with invalid credentials."""
    response = client.post('/login', data={
        'email': 'wrong@example.com',
        'password': 'wrongpass'
    }, follow_redirects=True)
    assert b'Invalid email or password' in response.data

def test_logout(client, auth):
    """Test logout functionality."""
    auth.login()
    response = auth.logout()
    assert b'You have been logged out' in response.data  # Adjust based on your flash message

def test_protected_route_redirects_when_not_logged_in(client):
    """Test that protected routes redirect to login when not authenticated."""
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302  # Redirect to login
    assert '/login' in response.location
