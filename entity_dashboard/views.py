from flask import render_template, request, redirect, url_for
from .app import app # Assuming app is initialized in app.py
# from .models import Entity, EntityData # Import models

# @app.route('/dashboard/<entity_id>')
# def dashboard(entity_id):
#     # Fetch entity and its data
#     # entity = Entity.query.get(entity_id)
#     # data = EntityData.query.filter_by(entity_id=entity_id).all()
#     # return render_template('dashboard.html', entity=entity, data=data)
#     return f"Dashboard for Entity {entity_id}"

# Add more views as needed
