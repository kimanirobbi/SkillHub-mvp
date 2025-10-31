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

def create_app(config_class=None):
    # Create and configure the app
    app = Flask(__name__)
    
    # Configure the app
    if config_class is None:
        from config import config
        config_name = os.getenv('FLASK_ENV', 'development')
        config_class = config[config_name]
    
    app.config.from_object(config_class)
    
    # Configure template and static folders
    base_dir = os.path.dirname(__file__)
    templates_path = os.path.abspath(os.path.join(base_dir, 'templates'))  # Fixed typo: 'templetes' -> 'templates'
    static_path = os.path.abspath(os.path.join(base_dir, 'static'))
    app.template_folder = templates_path
    app.static_folder = static_path
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