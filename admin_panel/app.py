from flask import Flask
from database.db_config import engine  # Use the engine from the central db_config
from database.models import Base  # Import Base to ensure tables are known

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_super_secret_key' # Change in production!

    # Ensure all tables are created (idempotent)
    # For a more robust setup, especially with migrations, Alembic is recommended.
    # Base.metadata.create_all(bind=engine) # This might be better placed in a run.py or manage.py

    from .routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

if __name__ == '__main__':
    # This is for running the Flask dev server directly
    # In production, use a WSGI server like Gunicorn or uWSGI
    app = create_app()
    # Need to create tables before running if they don't exist
    # This is a simple way for now.
    from database.models import create_db_and_tables
    create_db_and_tables()
    print("Starting Flask development server...")
    app.run(debug=True)
