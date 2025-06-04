from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app, jsonify, Response
from database.db_config import SessionLocal
from database.models import EntityAdmin, Entity, Subscriber, AttendanceSession, AttendanceRecord
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc, and_, func as sqlfunc
from sqlalchemy.orm import aliased, column_property, joinedload # Added joinedload
import bcrypt
from functools import wraps
import os
from werkzeug.utils import secure_filename
import datetime
import csv
import io

entity_bp = Blueprint('entity', __name__, template_folder='templates')

UPLOAD_FOLDER = 'uploads/subscriber_photos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and            filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_session():
    return SessionLocal()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'entity_admin_id' not in session or 'entity_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('entity.login'))

        g.db = get_db_session()
        g.entity_admin = g.db.query(EntityAdmin).get(session['entity_admin_id'])
        g.entity = g.db.query(Entity).get(session['entity_id'])

        if not g.entity_admin or not g.entity:
            flash('Session error. Please log in again.', 'danger')
            session.clear()
            return redirect(url_for('entity.login'))
        return f(*args, **kwargs)
    return decorated_function

@entity_bp.app_context_processor
def inject_global_vars():
    return dict(entity=getattr(g, 'entity', None), entity_admin=getattr(g, 'entity_admin', None))

@entity_bp.teardown_app_request
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# ... (Login, Logout, Dashboard Home, Subscriber CRUD routes - unchanged) ...
@entity_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'entity_admin_id' in session: return redirect(url_for('entity.dashboard_home'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db_session()
        try:
            entity_admin = db.query(EntityAdmin).filter_by(username=username).first()
            if entity_admin and bcrypt.checkpw(password.encode('utf-8'), entity_admin.password_hash.encode('utf-8')):
                session['entity_admin_id'] = entity_admin.id
                session['entity_admin_username'] = entity_admin.username
                session['entity_id'] = entity_admin.entity_id
                flash('Logged in successfully!', 'success')
                return redirect(url_for('entity.dashboard_home'))
            else: flash('Invalid username or password.', 'danger')
        finally: db.close()
    return render_template('auth/login.html')

@entity_bp.route('/logout')
def logout():
    session.clear(); flash('You have been logged out.', 'info')
    return redirect(url_for('entity.login'))

@entity_bp.route('/')
@login_required
def dashboard_home(): return render_template('dashboard/home.html')

@entity_bp.route('/subscribers', methods=['GET'])
@login_required
def list_subscribers():
    subscribers = g.db.query(Subscriber).filter_by(entity_id=g.entity.id).order_by(Subscriber.name).all()
    return render_template('subscribers/list.html', subscribers=subscribers)

@entity_bp.route('/subscribers/add', methods=['GET', 'POST'])
@login_required
def add_subscriber():
    if request.method == 'POST':
        name = request.form['name']; nfc_card_id = request.form['card_uid']
        email = request.form.get('email'); mobile = request.form.get('mobile')
        photo_file = request.files.get('photo'); saved_photo_filename = None
        if photo_file and photo_file.filename!='' and allowed_file(photo_file.filename):
            saved_photo_filename = secure_filename(photo_file.filename)
            flash(f'Photo "{saved_photo_filename}" processed conceptually.', 'info')
        if not name or not nfc_card_id:
            flash('Name and Card UID are required.', 'danger')
            return render_template('subscribers/add.html', form_data=request.form)
        try:
            new_subscriber = Subscriber(name=name, nfc_card_id=nfc_card_id, email=email if email else None, mobile=mobile, photo_filename=saved_photo_filename, entity_id=g.entity.id)
            g.db.add(new_subscriber); g.entity.total_registered_subscribers += 1; g.db.commit()
            flash('Subscriber added successfully!', 'success')
            return redirect(url_for('entity.list_subscribers'))
        except IntegrityError as e:
            g.db.rollback(); err_msg = str(e.orig).lower()
            if 'subscribers.nfc_card_id' in err_msg: flash('Error: Card UID already registered.', 'danger')
            elif 'subscribers.email' in err_msg: flash('Error: Email already registered.', 'danger')
            else: flash('Error adding subscriber. Check inputs.', 'danger')
        except Exception as e: g.db.rollback(); flash(f'Unexpected error: {str(e)}', 'danger')
        return render_template('subscribers/add.html', form_data=request.form)
    return render_template('subscribers/add.html', form_data={})

@entity_bp.route('/subscribers/<int:subscriber_id>/update', methods=['GET', 'POST'])
@login_required
def update_subscriber(subscriber_id):
    subscriber = g.db.query(Subscriber).filter_by(id=subscriber_id, entity_id=g.entity.id).first_or_404()
    if request.method == 'POST':
        subscriber.name = request.form['name']; subscriber.nfc_card_id = request.form['card_uid']
        subscriber.email = request.form.get('email') if request.form.get('email') else None
        subscriber.mobile = request.form.get('mobile')
        photo_file = request.files.get('photo')
        if photo_file and photo_file.filename!='' and allowed_file(photo_file.filename):
            subscriber.photo_filename = secure_filename(photo_file.filename)
            flash(f'Photo "{subscriber.photo_filename}" processed.', 'info')
        if not subscriber.name or not subscriber.nfc_card_id:
            flash('Name and Card UID are required.', 'danger')
            return render_template('subscribers/update.html', subscriber=subscriber)
        try:
            g.db.commit(); flash('Subscriber updated successfully!', 'success')
            return redirect(url_for('entity.list_subscribers'))
        except IntegrityError as e:
            g.db.rollback(); err_msg = str(e.orig).lower()
            if 'subscribers.nfc_card_id' in err_msg: flash('Error: Card UID already registered.', 'danger')
            elif 'subscribers.email' in err_msg: flash('Error: Email already registered.', 'danger')
            else: flash('Error updating subscriber.', 'danger')
        except Exception as e: g.db.rollback(); flash(f'Unexpected error: {str(e)}', 'danger')
        return render_template('subscribers/update.html', subscriber=subscriber)
    return render_template('subscribers/update.html', subscriber=subscriber)

@entity_bp.route('/subscribers/<int:subscriber_id>/delete', methods=['POST'])
@login_required
def delete_subscriber(subscriber_id):
    subscriber = g.db.query(Subscriber).filter_by(id=subscriber_id, entity_id=g.entity.id).first_or_404()
    if g.db.query(AttendanceRecord).filter_by(subscriber_id=subscriber.id).first():
        flash(f'Cannot delete subscriber {subscriber.name} as they have attendance records.', 'warning')
        return redirect(url_for('entity.list_subscribers'))
    try:
        g.db.delete(subscriber)
        if g.entity.total_registered_subscribers > 0: g.entity.total_registered_subscribers -= 1
        g.db.commit(); flash('Subscriber deleted successfully!', 'success')
    except Exception as e: g.db.rollback(); flash(f'Error deleting subscriber: {str(e)}', 'danger')
    return redirect(url_for('entity.list_subscribers'))

# --- Attendance Session Routes ---
@entity_bp.route('/attendance/sessions', methods=['GET'])
@login_required
def list_attendance_sessions():
    subquery = g.db.query(AttendanceRecord.session_id, sqlfunc.count(AttendanceRecord.id).label('attendee_count')).group_by(AttendanceRecord.session_id).subquery()
    sessions_with_counts = g.db.query(AttendanceSession, subquery.c.attendee_count).outerjoin(subquery, AttendanceSession.id == subquery.c.session_id).filter(AttendanceSession.entity_id == g.entity.id).order_by(desc(AttendanceSession.date), desc(AttendanceSession.start_time)).all()
    sessions_data = [{'session': session, 'attendee_count': count or 0} for session, count in sessions_with_counts]
    return render_template('attendance/sessions_list.html', sessions_data=sessions_data)

@entity_bp.route('/attendance/sessions/create', methods=['GET', 'POST'])
@login_required
def create_attendance_session():
    if request.method == 'POST':
        date_str = request.form.get('date'); time_str = request.form.get('start_time')
        purpose = request.form.get('purpose')
        if not date_str or not time_str:
            flash('Date and Start Time are required.', 'danger')
            return render_template('attendance/session_create.html', form_data=request.form)
        try:
            session_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            session_time = datetime.datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            flash('Invalid date or time format.', 'danger')
            return render_template('attendance/session_create.html', form_data=request.form)
        try:
            new_session = AttendanceSession(entity_id=g.entity.id, date=session_date, start_time=session_time, purpose=purpose, is_active=True)
            g.db.add(new_session); g.db.commit()
            flash('Attendance session created successfully!', 'success')
            return redirect(url_for('entity.scan_attendance', session_id=new_session.id))
        except Exception as e: g.db.rollback(); flash(f'Error creating session: {str(e)}', 'danger')
        return render_template('attendance/session_create.html', form_data=request.form)
    default_date = datetime.date.today().strftime('%Y-%m-%d')
    default_time = datetime.datetime.now().strftime('%H:%M')
    return render_template('attendance/session_create.html', form_data={'date': default_date, 'start_time': default_time})

@entity_bp.route('/attendance/sessions/<int:session_id>/toggle_active', methods=['POST'])
@login_required
def toggle_attendance_session_active(session_id):
    session_to_toggle = g.db.query(AttendanceSession).filter_by(id=session_id, entity_id=g.entity.id).first_or_404()
    try:
        session_to_toggle.is_active = not session_to_toggle.is_active; g.db.commit()
        status = "activated" if session_to_toggle.is_active else "deactivated"
        flash(f'Session "{session_to_toggle.purpose or session_to_toggle.id}" has been {status}.', 'success')
    except Exception as e: g.db.rollback(); flash(f'Error toggling session status: {str(e)}', 'danger')
    return redirect(url_for('entity.list_attendance_sessions'))

@entity_bp.route('/attendance/sessions/<int:session_id>/delete', methods=['POST'])
@login_required
def delete_attendance_session(session_id):
    session_to_delete = g.db.query(AttendanceSession).filter_by(id=session_id, entity_id=g.entity.id).first_or_404()
    if g.db.query(AttendanceRecord).filter_by(session_id=session_id).first():
        flash(f'Cannot delete session "{session_to_delete.purpose or session_to_delete.id}" as it has attendance records.', 'warning')
        return redirect(url_for('entity.list_attendance_sessions'))
    try:
        g.db.delete(session_to_delete); g.db.commit()
        flash(f'Session "{session_to_delete.purpose or session_to_delete.id}" deleted.', 'success')
    except Exception as e: g.db.rollback(); flash(f'Error deleting session: {str(e)}', 'danger')
    return redirect(url_for('entity.list_attendance_sessions'))

@entity_bp.route('/attendance/sessions/<int:session_id>/scan', methods=['GET', 'POST'])
@login_required
def scan_attendance(session_id):
    attendance_session = g.db.query(AttendanceSession).filter_by(id=session_id, entity_id=g.entity.id).first_or_404()
    if not attendance_session.is_active:
        flash('This attendance session is not active.', 'warning')
        return redirect(url_for('entity.list_attendance_sessions'))
    if request.method == 'POST':
        card_uid_scanned = request.form.get('card_uid')
        if not card_uid_scanned:
            flash('Card UID cannot be empty.', 'danger')
            return redirect(url_for('entity.scan_attendance', session_id=session_id))
        subscriber = g.db.query(Subscriber).filter(Subscriber.nfc_card_id == card_uid_scanned, Subscriber.entity_id == g.entity.id).first()
        response_data = {}
        if subscriber:
            existing_record = g.db.query(AttendanceRecord).filter_by(session_id=attendance_session.id, subscriber_id=subscriber.id).first()
            if existing_record:
                flash(f'{subscriber.name} ({subscriber.nfc_card_id}) is already present.', 'info')
                response_data = {'status': 'already_present', 'name': subscriber.name, 'card_uid': subscriber.nfc_card_id, 'scan_time': existing_record.scan_time.strftime('%Y-%m-%d %H:%M:%S')}
            else:
                try:
                    new_record = AttendanceRecord(session_id=attendance_session.id, subscriber_id=subscriber.id)
                    g.db.add(new_record); g.db.commit()
                    flash(f'Welcome, {subscriber.name}! Attendance recorded.', 'success')
                    response_data = {'status': 'success', 'name': subscriber.name, 'card_uid': subscriber.nfc_card_id, 'scan_time': new_record.scan_time.strftime('%Y-%m-%d %H:%M:%S')}
                except Exception as e: g.db.rollback(); flash(f'Error recording: {str(e)}', 'danger'); response_data = {'status': 'error', 'message': str(e)}
        else:
            flash(f'Subscriber with Card UID "{card_uid_scanned}" not found.', 'danger')
            response_data = {'status': 'not_found', 'card_uid': card_uid_scanned}
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest': return jsonify(response_data)
        return redirect(url_for('entity.scan_attendance', session_id=session_id))
    recent_attendees = g.db.query(AttendanceRecord).join(Subscriber).filter(AttendanceRecord.session_id == attendance_session.id).order_by(desc(AttendanceRecord.scan_time)).limit(20).all()
    return render_template('attendance/scan_page.html', session=attendance_session, recent_attendees=recent_attendees)

@entity_bp.route('/attendance/sheet', methods=['GET'])
@entity_bp.route('/attendance/sheet/<string:date_str>', methods=['GET'])
@login_required
def daily_attendance_sheet(date_str=None):
    if date_str is None: target_date = datetime.date.today()
    else:
        try: target_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError: flash('Invalid date format.', 'danger'); return redirect(url_for('entity.daily_attendance_sheet'))

    sessions_on_date_query = g.db.query(AttendanceSession).filter(
        AttendanceSession.entity_id == g.entity.id,
        AttendanceSession.date == target_date
    )
    # Eagerly load attendance_records and their associated subscriber for these sessions
    sessions_on_date = sessions_on_date_query.options(
        joinedload(AttendanceSession.attendance_records).joinedload(AttendanceRecord.subscriber)
    ).all()

    all_entity_subscribers = g.db.query(Subscriber).filter_by(entity_id=g.entity.id).all()

    attendee_subscriber_ids = set()
    # Build detailed_attendance and attendee_subscriber_ids more efficiently
    detailed_attendance = []
    all_records_for_date = g.db.query(AttendanceRecord)        .join(AttendanceSession)        .filter(AttendanceSession.entity_id == g.entity.id, AttendanceSession.date == target_date)        .options(joinedload(AttendanceRecord.subscriber))        .all()

    session_to_records_map = {}
    for record in all_records_for_date:
        attendee_subscriber_ids.add(record.subscriber_id)
        if record.session_id not in session_to_records_map:
            session_to_records_map[record.session_id] = []
        session_to_records_map[record.session_id].append(record)

    for s in sessions_on_date: # Iterate over already fetched sessions_on_date
        session_records_list = []
        for r in session_to_records_map.get(s.id, []):
            # subscriber object is already loaded on r due to joinedload
            session_records_list.append({'subscriber': r.subscriber, 'scan_time': r.scan_time})

        # Sort by subscriber name for display consistency
        session_records_list.sort(key=lambda x: x['subscriber'].name)
        detailed_attendance.append({'session': s, 'records': session_records_list})


    attendees_list = [sub for sub in all_entity_subscribers if sub.id in attendee_subscriber_ids]
    absentees_list = [sub for sub in all_entity_subscribers if sub.id not in attendee_subscriber_ids]

    export_type = request.args.get('export')
    if export_type:
        output = io.StringIO(); writer = csv.writer(output)
        if export_type == 'attendees':
            writer.writerow(['ID', 'Name', 'NFC Card UID', 'Email', 'Mobile'])
            for sub in attendees_list: writer.writerow([sub.id, sub.name, sub.nfc_card_id, sub.email, sub.mobile])
            filename = f"attendees_{target_date.strftime('%Y-%m-%d')}.csv"
        elif export_type == 'absentees':
            writer.writerow(['ID', 'Name', 'NFC Card UID', 'Email', 'Mobile'])
            for sub in absentees_list: writer.writerow([sub.id, sub.name, sub.nfc_card_id, sub.email, sub.mobile])
            filename = f"absentees_{target_date.strftime('%Y-%m-%d')}.csv"
        else: return redirect(url_for('entity.daily_attendance_sheet', date_str=target_date.strftime('%Y-%m-%d')))
        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": f"attachment; filename={filename}"})

    return render_template('attendance/daily_sheet.html', target_date=target_date, sessions_on_date=sessions_on_date, attendees=attendees_list, absentees=absentees_list, detailed_attendance=detailed_attendance)

@entity_bp.route('/subscribers/<int:subscriber_id>/attendance', methods=['GET'])
@login_required
def view_subscriber_attendance(subscriber_id):
    subscriber = g.db.query(Subscriber).filter_by(id=subscriber_id, entity_id=g.entity.id).first_or_404()
    end_date = datetime.date.today(); start_date = end_date - datetime.timedelta(days=365)
    form_start_date_str = request.args.get('start_date', start_date.strftime('%Y-%m-%d'))
    form_end_date_str = request.args.get('end_date', end_date.strftime('%Y-%m-%d'))
    try:
        query_start_date = datetime.datetime.strptime(form_start_date_str, '%Y-%m-%d').date()
        query_end_date = datetime.datetime.strptime(form_end_date_str, '%Y-%m-%d').date()
    except ValueError:
        flash("Invalid date format for filtering. Using default range (last year).", "warning")
        query_start_date = start_date; query_end_date = end_date
        form_start_date_str = start_date.strftime('%Y-%m-%d'); form_end_date_str = end_date.strftime('%Y-%m-%d')

    attendance_history = g.db.query(AttendanceRecord, AttendanceSession)                             .join(AttendanceSession, AttendanceRecord.session_id == AttendanceSession.id)                             .filter(AttendanceRecord.subscriber_id == subscriber_id)                             .filter(AttendanceSession.date >= query_start_date)                             .filter(AttendanceSession.date <= query_end_date)                             .order_by(desc(AttendanceSession.date), desc(AttendanceSession.start_time))                             .all() # This query is specific and likely efficient enough.

    export = request.args.get('export')
    if export == 'csv':
        output = io.StringIO(); writer = csv.writer(output)
        writer.writerow(['Session ID', 'Session Purpose', 'Session Date', 'Session Time', 'Scan Time'])
        for record, session_item in attendance_history: writer.writerow([session_item.id, session_item.purpose or 'N/A', session_item.date.strftime('%Y-%m-%d'), session_item.start_time.strftime('%H:%M:%S'), record.scan_time.strftime('%Y-%m-%d %H:%M:%S')])
        filename = f"attendance_history_{subscriber.name.replace(' ','_')}_{query_start_date}_{query_end_date}.csv"
        return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition": f"attachment; filename={filename}"})
    return render_template('subscribers/attendance_history.html', subscriber=subscriber, history=attendance_history, start_date=form_start_date_str, end_date=form_end_date_str)

@entity_bp.route('/reports/subscriber_attendance', methods=['GET'])
@login_required
def report_subscriber_attendance_form():
    subscribers = g.db.query(Subscriber).filter_by(entity_id=g.entity.id).order_by(Subscriber.name).all()
    return render_template('reports/subscriber_attendance_form.html', subscribers=subscribers)
