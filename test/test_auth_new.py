import os
import pytest
from flask import url_for, get_flashed_messages
from app import create_app, db
from app.modules import User, Professional
from bs4 import BeautifulSoup
import json
from config import TestingConfig

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@example.com', password='testpass123', follow_redirects=False):
        login_page = self._client.get('/auth/login')
        soup = BeautifulSoup(login_page.data, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': 'csrf-token'})
        
        login_data = {
            'email': email,
            'password': password,
            'remember_me': False,
            'submit': 'Sign In'
        }
        
        if csrf_input and 'value' in csrf_input.attrs:
            login_data['csrf_token'] = csrf_input['value']
        
        return self._client.post('/auth/login', data=login_data, follow_redirects=follow_redirects)

    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)
    
    def register(self, email, name, password, confirm_password, follow_redirects=False):
        register_page = self._client.get('/auth/register')
        soup = BeautifulSoup(register_page.data, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': 'csrf-token'})
        
        register_data = {
            'email': email,
            'full_name': name,
            'password': password,
            'password2': confirm_password,
            'submit': 'Register'
        }
        
        if csrf_input and 'value' in csrf_input.attrs:
            register_data['csrf_token'] = csrf_input['value']
        
        return self._client.post('/auth/register', data=register_data, follow_redirects=follow_redirects)

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create the app with test config
    app = create_app(TestingConfig)

    with app.app_context():
        db.create_all()
        
        # Create a test user
        user = User(
            email='test@example.com',
            full_name='Test User'
        )
        user.set_password('testpass123')
        db.session.add(user)
        
        # Create a professional profile for the test user
        professional = Professional(
            user=user,
            full_name='Test Professional',
            profession='Software Developer',
            bio='Test Bio',
            phone='1234567890',
            address='123 Test St',
            city='Test City',
            country='Test Country',
            years_experience=5,
            hourly_rate=50.0,
            is_available=True,
            location='Test Location',
            skills='Python, Flask, SQLAlchemy'
        )
        db.session.add(professional)
        db.session.commit()
    
    yield app
    
    # Clean up
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def auth(client):
    return AuthActions(client)

def test_home_page(client):
    """Test that the home page loads successfully."""
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    """Test the login page loads."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data or b'Sign In' in response.data

def test_successful_login(auth):
    """Test login with valid credentials."""
    response = auth.login(follow_redirects=True)
    assert response.status_code == 200
    # Check for logout button in the navigation bar
    assert b'Logout' in response.data

def test_failed_login(auth):
    """Test login with invalid credentials."""
    response = auth.login(password='wrongpassword', follow_redirects=True)
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data or b'Login' in response.data

def test_logout(auth):
    """Test logout functionality."""
    # Login first
    auth.login(follow_redirects=True)
    
    # Then logout
    response = auth.logout()
    
    # Should redirect to home page or login page
    assert response.status_code == 200
    assert b'Login' in response.data

def test_register_new_user(auth, app):
    """Test registration of a new user."""
    with app.app_context():
        # Make sure test user doesn't exist
        user = User.query.filter_by(email='newuser@example.com').first()
        if user:
            db.session.delete(user)
            db.session.commit()
    
    # Register a new user
    response = auth.register(
        email='newuser@example.com',
        name='New User',
        password='newpass123',
        confirm_password='newpass123',
        follow_redirects=True
    )
    
    # Should redirect to login page or dashboard
    assert response.status_code == 200
    assert b'Login' in response.data or b'Logout' in response.data
    
    # Check if user was created in the database
    with app.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.full_name == 'New User'

def test_register_existing_user(auth):
    """Test registration with an existing email."""
    # Try to register with an email that already exists
    response = auth.register(
        email='test@example.com',  # This email is already registered
        name='Existing User',
        password='testpass123',
        confirm_password='testpass123',
        follow_redirects=True
    )
    
    # Should show error message and stay on registration page
    assert response.status_code == 200
    assert b'Email already registered' in response.data or b'Register' in response.data

def test_protected_route_redirects_when_not_logged_in(client):
    """Test that protected routes redirect to login when not authenticated."""
    # Try to access a protected route
    response = client.get('/dashboard', follow_redirects=False)
    
    # Should redirect to login page with next parameter
    assert response.status_code == 302
    assert '/auth/login?next=%2Fdashboard' in response.location or '/auth/login' in response.location

def test_access_protected_route_when_logged_in(auth):
    """Test access to protected route when logged in."""
    # Login first
    auth.login(follow_redirects=True)
    
    # Try to access a protected route
    response = auth._client.get('/dashboard', follow_redirects=True)
    
    # Should be able to access the protected route
    assert response.status_code == 200
    assert b'Dashboard' in response.data or b'Welcome back' in response.data or b'Welcome' in response.data
