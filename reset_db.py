from app import create_app, db
import os

app = create_app()

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("All tables dropped.")
    
    # Remove migration versions
    migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations', 'versions')
    if os.path.exists(migrations_dir):
        for file in os.listdir(migrations_dir):
            if file.endswith('.py') and file != '__init__.py':
                os.remove(os.path.join(migrations_dir, file))
        print("Migration versions cleared.")
    
    print("Database reset complete. You can now run 'flask db migrate' and 'flask db upgrade' to recreate the database schema.")
