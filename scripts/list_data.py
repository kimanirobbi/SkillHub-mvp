from app import create_app, db
from app.modules import Job, Professional

def list_data():
    app = create_app()
    with app.app_context():
        try:
            # List all jobs
            print("\n=== Jobs ===")
            jobs = Job.query.all()
            for job in jobs:
                print(f"ID: {job.id}, Title: {job.title}")
            
            # List all professionals
            print("\n=== Professionals ===")
            professionals = Professional.query.all()
            for prof in professionals:
                print(f"ID: {prof.id}, Name: {prof.first_name} {prof.last_name}")
            
        except Exception as e:
            print(f"Error listing data: {str(e)}")

if __name__ == '__main__':
    list_data()
