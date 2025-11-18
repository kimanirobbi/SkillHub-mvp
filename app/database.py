from flask import Flask
from .database import db
from .routes import bp as main_bp

def create_app():
    app = Flask(__name__)

    # PostgreSQL connection string
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+psycopg2://postgres:Robbi2025.@localhost:5432/skillhub"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_bp)

    return app
