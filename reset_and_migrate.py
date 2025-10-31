from app import create_app, db
from app.modules import User, Professional, Service, Booking, Payment, Review
import os
from werkzeug.security import generate_password_hash

def reset_and_migrate():
    app = create_app()
    
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("Creating all tables...")
        db.create_all()
        print("Database reset and tables created successfully.")
        
        # Create a test user
        try:
            print("Creating test user...")
            user = User(
                username="testuser",
                email="test@example.com",
                first_name="Test",
                last_name="User",
                password_hash=generate_password_hash("password123"),
                role="admin",
                email_verified=True
            )
            db.session.add(user)
            db.session.commit()
            
            # Create a test professional
            print("Creating test professional...")
            professional = Professional(
                full_name="Test Professional",
                profession="Developer",
                bio="Experienced developer",
                user_id=user.id
            )
            db.session.add(professional)
            db.session.commit()
            
            print("Test data created successfully.")
        except Exception as e:
            print(f"Error creating test data: {e}")
            db.session.rollback()
            raise
        
        print("Database reset and migration complete!")

if __name__ == '__main__':
    reset_and_migrate()
