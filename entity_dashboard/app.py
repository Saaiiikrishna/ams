from flask import Flask, session
from database.db_config import engine # Using the same engine
from database.models import Base # Ensure tables are known (though created by admin_panel's run)
import os

def create_app():
    app = Flask(__name__)
    # It's good practice to use environment variables for secret keys
    app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'your_entity_dashboard_secret_key') # Change in production!

    # If needed, create tables - though admin panel app.py already does this when run.
    # from database.models import create_db_and_tables
    # create_db_and_tables()

    from .routes import entity_bp
    app.register_blueprint(entity_bp, url_prefix='/dashboard') # Using /dashboard as prefix

    return app

if __name__ == '__main__':
    # This is for running the Flask dev server directly
    # In production, use a WSGI server like Gunicorn or uWSGI
    app = create_app()
    # Ensure tables are created if they don't exist (e.g. if running this app standalone first)
    from database.models import create_db_and_tables
    create_db_and_tables() # Idempotent
    print("Starting Entity Dashboard Flask development server...")
    app.run(port=5001, debug=True) # Running on a different port than admin_panel for concurrent dev
