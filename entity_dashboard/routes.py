from .app import app # Assuming app is initialized in app.py
from .views import * # Import views

# Example of registering view from views.py
# app.add_url_rule('/dashboard/<entity_id>', view_func=dashboard)

# Or define routes directly:
# @app.route('/entity/new', methods=['GET', 'POST'])
# def new_entity():
#     # Logic to create a new entity
#     return "New Entity Page"
