from app import create_app, db
from app.modules import AISuggestion, Job, Professional, User
from datetime import datetime, timezone

def add_test_data():
    app = create_app()
    with app.app_context():
        try:
            # Create a test user if it doesn't exist
            user = User.query.filter_by(email='test@example.com').first()
            if not user:
                user = User(
                    username='testuser',
                    email='test@example.com',
                    first_name='Test',
                    last_name='User',
                    is_active=True
                )
                user.set_password('testpassword')
                db.session.add(user)
                db.session.commit()
                print(f"Created test user with email: {user.email}")

            # Create a test professional if it doesn't exist
            professional = Professional.query.filter_by(user_id=user.id).first()
            if not professional:
                professional = Professional(
                    user_id=user.id,
                    full_name='Test Professional',
                    bio='Test bio',
                    location='Test Location'
                )
                db.session.add(professional)
                db.session.commit()

            # Create a test job if it doesn't exist
            job = Job.query.filter_by(title='Test Job').first()
            if not job:
                job = Job(
                    title='Test Job',
                    description='This is a test job',
                    location='Test Location',
                    user_id=user.id
                )
                db.session.add(job)
                db.session.commit()

            # Now add the AI suggestion
            test_row = AISuggestion(
                job_id=job.id,
                professional_id=professional.id,
                score=0.85,
                distance_km=10.0,
                similarity_score=0.9,
                distance_score=0.6,
                is_contacted=False,
                is_interested=True,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc)
            )
            db.session.add(test_row)
            db.session.commit()
            
            print("Successfully added test data:")
            print(f"- User ID: {user.id}")
            print(f"- Professional ID: {professional.id}")
            print(f"- Job ID: {job.id}")
            print(f"- AI Suggestion ID: {test_row.id}")
            
            # Verify the count
            count = AISuggestion.query.count()
            print(f"\nTotal AI suggestions in database: {count}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding test data: {str(e)}")

if __name__ == '__main__':
    add_test_data()
