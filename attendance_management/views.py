from flask import render_template, request, jsonify
from .app import app # Assuming app is initialized in app.py
# from .models import AttendanceRecord, Subscriber
# from database.db_config import Session # Assuming a shared session
from datetime import datetime

# @app.route('/attendance/record', methods=['POST'])
# def record_attendance():
#     data = request.json
#     nfc_tag_id = data.get('nfc_tag_id')
#     event_type = data.get('event_type', 'tap') # e.g., 'tap', 'entry', 'exit'
#
#     session = Session()
#     subscriber = session.query(Subscriber).filter_by(nfc_tag_id=nfc_tag_id).first()
#
#     if not subscriber:
#         session.close()
#         return jsonify(success=False, message="NFC tag not recognized or subscriber not found"), 404
#
#     if not subscriber.is_active:
#         session.close()
#         return jsonify(success=False, message="Subscriber is inactive"), 403
#
#     record = AttendanceRecord(
#         subscriber_id=subscriber.id,
#         timestamp=datetime.utcnow(),
#         event_type=event_type
#     )
#     session.add(record)
#     session.commit()
#     session.close()
#     return jsonify(success=True, message=f"Attendance recorded for {subscriber.name}")

# @app.route('/attendance/history/<subscriber_id>')
# def attendance_history(subscriber_id):
#     # session = Session()
#     # records = session.query(AttendanceRecord).filter_by(subscriber_id=subscriber_id).order_by(AttendanceRecord.timestamp.desc()).all()
#     # subscriber = session.query(Subscriber).get(subscriber_id)
#     # session.close()
#     # return render_template('attendance_history.html', records=records, subscriber_name=subscriber.name if subscriber else "N/A")
#     return f"Attendance history for Subscriber {subscriber_id}"
