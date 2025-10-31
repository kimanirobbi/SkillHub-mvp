from app import create_app, db
from flask_migrate import Migrate
import os

def fix_alembic():
    app = create_app()
    with app.app_context():
        # Drop the existing alembic_version table if it exists
        db.engine.execute('DROP TABLE IF EXISTS alembic_version;')
        print("Dropped existing alembic_version table.")
        
        # Create a new alembic_version table
        db.engine.execute('CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL);')
        print("Created new alembic_version table.")
        
        # Get the latest migration file
        migrations_dir = os.path.join('migrations', 'versions')
        if os.path.exists(migrations_dir):
            migration_files = [f for f in os.listdir(migrations_dir) if f.endswith('.py')]
            if migration_files:
                # Sort to get the latest migration
                migration_files.sort()
                latest_migration = migration_files[-1]
                # Extract the revision ID from the filename
                revision_id = latest_migration.split('_')[0]
                # Insert the latest revision into alembic_version
                db.engine.execute(f"INSERT INTO alembic_version (version_num) VALUES ('{revision_id}');")
                print(f"Set current database version to: {revision_id}")
                return
        
        print("No migration files found. Please run 'flask db migrate' first.")

if __name__ == '__main__':
    fix_alembic()
