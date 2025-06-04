from flask import render_template, request, redirect, url_for, jsonify
from .app import app # Assuming app is initialized in app.py
# from .models import Subscriber # Import models
# from database.db_config import Session # Assuming a shared session

# @app.route('/subscribers')
# def list_subscribers():
#     # session = Session()
#     # subscribers = session.query(Subscriber).all()
#     # session.close()
#     # return render_template('subscribers.html', subscribers=subscribers)
#     return "List of Subscribers"

# @app.route('/subscriber/new', methods=['GET', 'POST'])
# def new_subscriber():
#     if request.method == 'POST':
#         # Logic to add new subscriber
#         # name = request.form['name']
#         # email = request.form['email']
#         # new_sub = Subscriber(name=name, email=email)
#         # session = Session()
#         # session.add(new_sub)
#         # session.commit()
#         # session.close()
#         # return redirect(url_for('list_subscribers'))
#     # return render_template('new_subscriber.html')
#     return "New Subscriber Form"

# @app.route('/subscriber/assign_nfc/<subscriber_id>', methods=['POST'])
# def assign_nfc(subscriber_id):
#     # nfc_tag_id = request.json.get('nfc_tag_id')
#     # session = Session()
#     # subscriber = session.query(Subscriber).get(subscriber_id)
#     # if subscriber:
#     #     subscriber.nfc_tag_id = nfc_tag_id
#     #     session.commit()
#     #     session.close()
#     #     return jsonify(success=True, message="NFC tag assigned")
#     # return jsonify(success=False, message="Subscriber not found"), 404
#     return f"Assign NFC to Subscriber {subscriber_id}"
