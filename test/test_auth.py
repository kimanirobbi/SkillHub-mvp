import pytest
import pytest
from flask import url_for, get_flashed_messages
from app import create_app, db
from app.modules import User, Professional
from bs4 import BeautifulSoup
import json

class AuthActions(object):
    def __init__(self, client):
        self._client = client

    def login(self, email='test@example.com', password='testpass123', follow_redirects=False):
        # Get the login page to extract CSRF token
        login_page = self._client.get('/auth/login')
        soup = BeautifulSoup(login_page.data, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': 'csrf-token'})
        
        # Prepare login data
        login_data = {
            'email': email,
            'password': password,
            'remember_me': False,
            'submit': 'Sign In'
        }
        
        # Add CSRF token if it exists
        if csrf_input and 'value' in csrf_input.attrs:
            login_data['csrf_token'] = csrf_input['value']
        
        # Submit the login form
        return self._client.post('/auth/login', data=login_data, follow_redirects=follow_redirects)

    def logout(self):
        return self._client.get('/auth/logout', follow_redirects=True)
    
    def register(self, email, name, password, confirm_password, follow_redirects=False):
        # Get the register page to extract CSRF token
        register_page = self._client.get('/auth/register')
        soup = BeautifulSoup(register_page.data, 'html.parser')
        csrf_input = soup.find('input', {'name': 'csrf_token'}) or soup.find('input', {'name': 'csrf-token'})
        
        # Prepare registration data
        register_data = {
            'email': email,
            'full_name': name,
            'password': password,
            'password2': confirm_password,
            'submit': 'Register'
        }
        
        # Add CSRF token if it exists
        if csrf_input and 'value' in csrf_input.attrs:
            register_data['csrf_token'] = csrf_input['value']
        
        # Submit the registration form
        return self._client.post('/auth/register', data=register_data, follow_redirects=follow_redirects)

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
            full_name='Test User',
            role='professional'  # Add role here
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
        if hasattr(db, 'engine'):db.engine.dispose() 

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

def test_successful_login(client, auth):
    """Test login with valid credentials."""
    response = auth.login(follow_redirects=True)
    
    # Check if login was successful
    assert response.status_code == 200
    assert b'Logout' in response.data  # Should see logout button when logged in
    assert b'Test User' in response.data  # Should see user's name when logged in

def test_failed_login(auth):
    """Test login with invalid credentials."""
    response = auth.login(password='wrongpassword', follow_redirects=True)
    
    # Should show error message and stay on login page
    assert response.status_code == 200
    assert b'Invalid email or password' in response.data or b'Login' in response.data

def test_logout(auth):
    """Test logout functionality."""
    # First login
    auth.login(follow_redirects=True)
    
    # Then logout
    response = auth.logout()
    
    # Should redirect to home page or login page
    assert response.status_code == 200
    assert b'Login' in response.data  # Should see login button after logout

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
        email='test@example.com',  # This email is already registered in the test DB
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
    
    # Should redirect to login page
    assert response.status_code == 302
    assert '/auth/login' in response.location

def test_access_protected_route_when_logged_in(auth):
    """Test access to protected route when logged in."""
    # Login first
    auth.login(follow_redirects=True)
    
    # Try to access a protected route
    response = auth._client.get('/dashboard', follow_redirects=True)
    
    # Should be able to access the protected route
    assert response.status_code == 200
    assert b'Dashboard' in response.data or b'Welcome' in response.data






