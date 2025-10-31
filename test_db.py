from app import create_app, db
from app.modules import User

def test_db():
    app = create_app()
    with app.app_context():
        # Test database connection
        print("Testing database connection...")
        try:
            # Try to query the User table
            user_count = User.query.count()
            print(f"Successfully connected to database. Found {user_count} users.")
            
            # Print database URL
            print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Check if the bio column exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('users')]
            print("Columns in users table:", columns)
            print("Does 'bio' column exist?", 'bio' in columns)
            
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")

if __name__ == "__main__":
    test_db()
