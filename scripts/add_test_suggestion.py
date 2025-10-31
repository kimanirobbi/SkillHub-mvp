from app import create_app, db
from app.modules import AISuggestion
from datetime import datetime

def add_test_suggestion():
    app = create_app()
    with app.app_context():
        try:
            test_suggestion = AISuggestion(
                job_id=1,
                professional_id=1,
                score=0.85,
                distance_km=12.5,
                similarity_score=0.9,
                distance_score=0.6,
                is_contacted=False,
                is_interested=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.session.add(test_suggestion)
            db.session.commit()
            print("Successfully added test suggestion to the database.")
            print(f"New suggestion ID: {test_suggestion.id}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Error adding test suggestion: {str(e)}")

if __name__ == "__main__":
    add_test_suggestion()
