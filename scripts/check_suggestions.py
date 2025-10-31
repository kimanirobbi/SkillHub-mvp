from app import create_app
from app.modules import AISuggestion

app = create_app()

with app.app_context():
    count = AISuggestion.query.filter(AISuggestion.score < 0.7).count()
    print(f"Suggestions with score < 0.7: {count}")
    
    # Print all suggestions for reference
    print("\nAll suggestions:")
    for s in AISuggestion.query.all():
        print(f"- ID: {s.id}, Score: {s.score:.2f}, Professional ID: {s.professional_id}")
