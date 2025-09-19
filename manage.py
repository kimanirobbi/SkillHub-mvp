# manage.py
from app import create_app, db
from app.modules import User  # import existing models
from werkzeug.security import generate_password_hash

app = create_app()

# Run this file manually to create tables or test DB connection
if __name__ == "__main__":
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        print("All tables created successfully!")

        # --------- Seed Users ---------
        if not User.query.filter_by(email="alice@example.com").first():
            user1 = User(
                name="Alice Johnson",
                email="alice@example.com",
                phone="0712345678",
                password_hash=generate_password_hash("password123"),
                role="client"
            )
            db.session.add(user1)

        if not User.query.filter_by(email="bob@example.com").first():
            user2 = User(
                name="Bob Smith",
                email="bob@example.com",
                phone="0723456789",
                password_hash=generate_password_hash("securepass"),
                role="professional"
            )
            db.session.add(user2)

        db.session.commit()
        print("Users seeded successfully!")