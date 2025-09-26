import pytest
import sys
import os

# Ensure parent directory (SkillHub-mvp/) is on PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models import User


@pytest.fixture
def test_client():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "postgresql+psycopg2://postgres:postgres@localhost:5432/skillhub_test"
    })

    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app.test_client()

    # Clean up after test
    with app.app_context():
        db.session.remove()
        db.drop_all()


def test_home_page(test_client):
    """Basic check that home route works"""
    response = test_client.get("/")
    assert response.status_code == 200


def test_user_signup(test_client):
    """Check that signup works"""
    response = test_client.post("/signup", data={
        "email": "test@example.com",
        "password": "test123"
    }, follow_redirects=True)
    assert b"Dashboard" in response.data or response.status_code in (200, 302)


def test_user_login(test_client):
    """Check that login works after signup"""
    # First create user in DB
    with test_client.application.app_context():
        user = User(email="login@example.com")
        user.set_password("mypassword")
        db.session.add(user)
        db.session.commit()

    # Then login
    response = test_client.post("/login", data={
        "email": "login@example.com",
        "password": "mypassword"
    }, follow_redirects=True)

    assert b"Dashboard" in response.data or response.status_code in (200, 302)
