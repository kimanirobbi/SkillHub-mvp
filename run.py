from dotenv import load_dotenv
load_dotenv()

from app import create_app

app = create_app()

# Add this print statement for debugging
print(f"DEBUG: SQLALCHEMY_DATABASE_URI is {app.config.get('SQLALCHEMY_DATABASE_URI')}")

if __name__ == "__main__":
    app.run(debug=True)
