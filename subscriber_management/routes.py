from .app import app # Assuming app is initialized in app.py
from .views import * # Import views

# Example of registering views
# app.add_url_rule('/subscribers', view_func=list_subscribers)
# app.add_url_rule('/subscriber/new', view_func=new_subscriber, methods=['GET', 'POST'])
# app.add_url_rule('/subscriber/assign_nfc/<subscriber_id>', view_func=assign_nfc, methods=['POST'])

# Or define routes directly if preferred
