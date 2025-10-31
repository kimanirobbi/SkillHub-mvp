import os
import tempfile
import pytest
from app import create_app, db as _db
from flask_migrate import upgrade

@pytest.fixture(scope='module')
def app():
    """Create and configure a new app instance for testing."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///' + db_path,
        'WTF_CSRF_ENABLED': False
    })

    # Create the database and load test data
    with app.app_context():
        _db.create_all()
        upgrade()
        
    yield app
    
    # Clean up the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='module')
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture(scope='module')
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()

@pytest.fixture(scope='function')
def db(app):
    """A database for the tests."""
    with app.app_context():
        _db.drop_all()
        _db.create_all()
        upgrade()
        
        yield _db
        
        _db.session.remove()
        _db.drop_all()
        _db.get_engine(app).dispose()

class AuthActions(object):
    def __init__(self, client):
        self._client = client
    
    def login(self, email='test@example.com', password='testpassword'):
        return self._client.post(
            '/login',
            data={'email': email, 'password': password},
            follow_redirects=True
        )
    
    def logout(self):
        return self._client.get('/logout', follow_redirects=True)

@pytest.fixture
def auth(client):
    return AuthActions(client)
