import os
import sys # Import sys
from flask import Flask, request # Import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import logging # Import logging
from whitenoise import WhiteNoise
import tempfile # Import tempfile

# Load environment variables from .env file
load_dotenv()


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
# limiter = Limiter(
#     key_func=get_remote_address,
#     default_limits=["200 per day", "50 per hour"],
#     storage_uri="memory://"
# )

# ...

# limiter.init_app(app)

def create_app(config_class=None):
    # Create and configure the app
    if os.getenv('VERCEL'):
        instance_path = tempfile.gettempdir()
    else:
        instance_path = None

    app = Flask(__name__, instance_relative_config=False)

    # Set database URI from environment variable
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'SQLALCHEMY_DATABASE_URI',
        'sqlite:///app.db'  # fallback for local development
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    
    # Configure the app
    if config_class is None:
        from config import config
        config_name = os.getenv('FLASK_ENV', 'development')
        config_class = config[config_name]
    
    app.config.from_object(config_class)
    
    return app
    
    # Configure template and static folders
    base_dir = os.path.dirname(__file__)
    templates_path = os.path.abspath(os.path.join(base_dir, 'templates'))  # Fixed typo: 'templetes' -> 'templates'
    static_path = os.path.abspath(os.path.join(base_dir, 'static'))
    app.template_folder = templates_path
    app.static_folder = static_path
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['TEMPLATES_AUTO_RELOAD'] = True

    # Add whitenoise
    app.wsgi_app = WhiteNoise(app.wsgi_app, root=static_path, prefix='/static/')

    # Configure logging
    # Log to stdout
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    )
    stream_handler.setFormatter(formatter)
    app.logger.addHandler(stream_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Flask startup')

    # Log requests
    @app.before_request
    def log_request_info():
        app.logger.info(f'Request: {request.method} {request.url}')

    @app.after_request
    def log_response_info(response):
        app.logger.info(f'Response: {request.method} {request.url} Status: {response.status_code}')
        return response

    # Initialize Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models to ensure they are registered with SQLAlchemy
    from .modules import User, Service, Booking, Payment, Professional

    # Import and register Blueprints
    from .main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from .auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # Register geo blueprint
    from .geo_routes import geo_bp
    app.register_blueprint(geo_bp)

    # Register admin blueprint
    from .admin import admin_bp
    app.register_blueprint(admin_bp)

    return app
@login_manager.user_loader
def load_user(user_id):
    # local import to avoid circular dependency during app creation
    from .models import User
    return db.session.get(User, int(user_id))