import os
from app import create_app, db
from app.modules import User, Professional, Service, Review, Booking, Payment
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

def create_tables():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully.")

def create_test_data():
    print("Creating test data...")
    
    # Create test user
    user = User(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
        password_hash=generate_password_hash('password123', method='pbkdf2:sha256'),
        role='client',
        is_active=True,
        email_verified=True
    )
    db.session.add(user)
    db.session.commit()
    
    # Create test professional
    professional = Professional(
        full_name='John Doe',
        profession='Plumber',
        bio='Experienced plumber with 10+ years of experience',
        user_id=user.id
    )
    db.session.add(professional)
    db.session.commit()
    
    # Create test service
    service = Service(
        title='Plumbing Repair',
        description='Professional plumbing repair services',
        category='Plumbing',
        price=100.00,
        provider_id=user.id,
        professional_id=professional.id,
        is_active=True
    )
    db.session.add(service)
    db.session.commit()
    
    print("Test data created successfully!")
    print(f"Test user email: test@example.com")
    print(f"Test password: password123")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Drop all tables
        print("Dropping all tables...")
        db.drop_all()
        print("All tables dropped.")
        
        # Create new tables
        create_tables()
        
        # Create test data
        create_test_data()
        
        print("\nSetup complete! You can now run the application.")
