import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

def create_app():
    # Configure template and static folders explicitly
    base_dir = os.path.dirname(__file__)
    templates_path = os.path.abspath(os.path.join(base_dir, 'templetes'))
    static_path = os.path.abspath(os.path.join(base_dir, 'static'))
    app = Flask(
        __name__,
        template_folder=templates_path,
        static_folder=static_path,
        static_url_path='/static'
    )

    # Configurations from .env
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "fallback-secret")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL", "sqlite:///skillhub.db")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    # Development: disable static file caching and auto-reload templates
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    limiter.init_app(app)

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models to ensure they are registered with SQLAlchemy
    from .modules import User, Service, Booking, Payment, Professional

    # Import and register Blueprints
    from .routes import auth_bp
    app.register_blueprint(auth_bp)

    # Register geo blueprint
    from .geo_routes import geo_bp
    app.register_blueprint(geo_bp)

    return app

@login_manager.user_loader
def load_user(user_id):
    # local import to avoid circular dependency during app creation
    from .modules import User
    return db.session.get(User, int(user_id))