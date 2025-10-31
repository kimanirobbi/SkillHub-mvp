def recommend(skills):
    data = [
        {"name": "John the Plumber", "skills": ["plumbing", "maintenance"]},
        {"name": "Mary the Designer", "skills": ["ui", "ux", "figma"]},
        {"name": "Sam the Dev", "skills": ["python", "flask", "sqlalchemy"]}
    ]
    return [p for p in data if any(s in p["skills"] for s in skills)]