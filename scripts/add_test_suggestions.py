"""
Script to add test AI suggestions to the database.
Run with: flask shell < scripts/add_test_suggestions.py
"""
import random
from datetime import datetime, timedelta
from app import create_app, db
from app.modules import Job, Professional, AISuggestion

def create_test_suggestions():
    print("Creating test AI suggestions...")
    
    # Get the first job and professional (or create them if they don't exist)
    job = Job.query.first()
    if not job:
        print("Creating test job...")
        from app.modules import User
        user = User.query.first()
        if not user:
            user = User(
                username='testuser',
                email='test@example.com',
                password_hash='testpass'
            )
            db.session.add(user)
            db.session.commit()
            
        job = Job(
            title='Web Development Project',
            description='Need a website built with React and Node.js',
            profession='Web Developer',
            location='Nairobi, Kenya',
            status='open',
            poster_id=user.id
        )
        db.session.add(job)
        db.session.commit()
    
    professionals = Professional.query.limit(5).all()
    if not professionals:
        print("Creating test professionals...")
        from app.modules import User
        user = User.query.first()
        
        professions = ['Web Developer', 'Designer', 'Mobile Developer', 'Data Scientist', 'DevOps Engineer']
        
        for i in range(5):
            prof_user = User(
                username=f'proftest{i+1}',
                email=f'prof{i+1}@example.com',
                password_hash=f'profpass{i+1}'
            )
            db.session.add(prof_user)
            db.session.commit()
            
            professional = Professional(
                full_name=f'Professional {i+1}',
                profession=professions[i % len(professions)],
                bio=f'Experienced {professions[i % len(professions)]} with 5+ years of experience',
                user_id=prof_user.id,
                location=f'Nairobi, Kenya',
                latitude=-1.2921 + random.uniform(-0.1, 0.1),  # Randomize location slightly
                longitude=36.8219 + random.uniform(-0.1, 0.1)
            )
            db.session.add(professional)
            professionals.append(professional)
        
        db.session.commit()
    
    # Create test matches
    matches = []
    for i, prof in enumerate(professionals):
        matches.append({
            "professional": prof,
            "score": 0.7 + (i * 0.05),  # Scores from 0.7 to 0.9
            "similarity": 0.6 + (i * 0.05),  # Similarity scores
            "distance_score": 0.8 - (i * 0.05),  # Distance scores
            "distance_km": 5.0 - (i * 0.5)  # Distance in km
        })
    
    # Create the suggestions
    success, message = job.create_ai_suggestions(matches)
    print(message)
    
    # Verify the count
    count = AISuggestion.query.count()
    print(f"Total suggestions in database: {count}")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        create_test_suggestions()
