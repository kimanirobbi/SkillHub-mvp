import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    # Point template_folder to the project root so render_template can find login.html, signup.html, etc.
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    app = Flask(__name__, template_folder=project_root)

    # Configurations from .env
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback-secret")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///skillhub.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models to ensure they are registered with SQLAlchemy
    from .modules import User, Service, Booking, Payment

    # Import and register Blueprints
    from .routes import auth_bp
    app.register_blueprint(auth_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    # local import to avoid circular dependency during app creation
    from .modules import User
    return db.session.get(User, int(user_id))