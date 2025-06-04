from .app import app # Assuming app is initialized in app.py
from .views import * # Import views

# Example of registering views
# app.add_url_rule('/attendance/record', view_func=record_attendance, methods=['POST'])
# app.add_url_rule('/attendance/history/<subscriber_id>', view_func=attendance_history)

# Or define routes directly if preferred
