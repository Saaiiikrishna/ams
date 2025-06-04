from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_config import SessionLocal
from database.models import Entity, EntityAdmin
from sqlalchemy.exc import IntegrityError
import bcrypt

admin_bp = Blueprint('admin', __name__, template_folder='templates')

def get_db_session():
    return SessionLocal()

@admin_bp.route('/entities', methods=['GET'])
def list_entities():
    db = get_db_session()
    entities = db.query(Entity).order_by(Entity.id).all()
    db.close()
    return render_template('entities/list.html', entities=entities)

def safe_float(value_str):
    if value_str and value_str.strip():
        try:
            return float(value_str)
        except ValueError:
            return None # Or raise an error, or return a specific marker
    return None

@admin_bp.route('/entities/create', methods=['GET', 'POST'])
def create_entity():
    if request.method == 'POST':
        db = get_db_session()
        try:
            latitude_str = request.form.get('latitude', '')
            longitude_str = request.form.get('longitude', '')

            new_entity = Entity(
                name=request.form['name'],
                address=request.form.get('address'),
                latitude=safe_float(latitude_str),
                longitude=safe_float(longitude_str),
                contact_person_name=request.form.get('contact_person_name'),
                contact_person_mobile=request.form.get('contact_person_mobile'),
                email=request.form['email']
            )
            db.add(new_entity)
            db.commit()
            flash('Entity created successfully!', 'success')
            return redirect(url_for('admin.list_entities'))
        except IntegrityError as e:
            db.rollback()
            flash(f'Error creating entity: Email might already exist. ({e})', 'danger')
        except ValueError as e: # Catch specific error from float conversion if safe_float re-raises
            db.rollback()
            flash(f'Error creating entity: Invalid number format for latitude or longitude. ({e})', 'danger')
        except Exception as e:
            db.rollback()
            flash(f'An unexpected error occurred: {e}', 'danger')
        finally:
            db.close()
    return render_template('entities/create.html')

@admin_bp.route('/entities/<int:entity_id>/update', methods=['GET', 'POST'])
def update_entity(entity_id):
    db = get_db_session()
    entity = db.query(Entity).get(entity_id)
    if not entity:
        flash('Entity not found!', 'danger')
        db.close()
        return redirect(url_for('admin.list_entities'))

    if request.method == 'POST':
        try:
            latitude_str = request.form.get('latitude', '')
            longitude_str = request.form.get('longitude', '')

            entity.name = request.form['name']
            entity.address = request.form.get('address')
            entity.latitude = safe_float(latitude_str)
            entity.longitude = safe_float(longitude_str)
            entity.contact_person_name = request.form.get('contact_person_name')
            entity.contact_person_mobile = request.form.get('contact_person_mobile')
            entity.email = request.form['email']

            db.commit()
            flash('Entity updated successfully!', 'success')
            return redirect(url_for('admin.list_entities'))
        except IntegrityError:
            db.rollback()
            flash('Error updating entity: Email might already exist for another entity.', 'danger')
        except ValueError as e: # Catch specific error from float conversion
            db.rollback()
            flash(f'Error updating entity: Invalid number format for latitude or longitude. ({e})', 'danger')
        except Exception as e:
            db.rollback()
            flash(f'An unexpected error occurred: {e}', 'danger')

        # If POST and error, re-render with entity
        # The session should be closed before re-rendering
        # No need to close db explicitly here if it's handled by the calling structure or teardown
        # But since we are not using a global session manager like g.db + teardown in admin_panel, close it.
        if db.is_active : db.close() # ensure closed before re-render
        return render_template('entities/update.html', entity=entity)

    # For GET request, db should be closed after use.
    db.close()
    return render_template('entities/update.html', entity=entity)


@admin_bp.route('/entities/<int:entity_id>/delete', methods=['POST'])
def delete_entity(entity_id):
    db = get_db_session()
    entity = db.query(Entity).get(entity_id)
    if entity:
        try:
            if entity.admins or entity.subscribers:
                flash('Cannot delete entity: It has associated admins or subscribers. Please remove them first.', 'warning')
                db.close()
                return redirect(url_for('admin.list_entities'))

            db.delete(entity)
            db.commit()
            flash('Entity deleted successfully!', 'success')
        except Exception as e:
            db.rollback()
            flash(f'Error deleting entity: {e}', 'danger')
        finally:
            db.close()
    else:
        flash('Entity not found!', 'danger')
        if db.is_active: db.close() # If entity not found, db might still be open
    return redirect(url_for('admin.list_entities'))

@admin_bp.route('/entities/<int:entity_id>/assign_admin', methods=['GET', 'POST'])
def assign_admin_credentials(entity_id):
    db = get_db_session()
    entity = db.query(Entity).get(entity_id)
    if not entity:
        flash('Entity not found!', 'danger')
        db.close()
        return redirect(url_for('admin.list_entities'))

    entity_admin = db.query(EntityAdmin).filter_by(entity_id=entity.id).first()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required.', 'danger')
            db.close() # Close session before re-rendering
            return render_template('entities/assign_admin.html', entity=entity, entity_admin=entity_admin)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            if entity_admin:
                entity_admin.username = username
                entity_admin.password_hash = hashed_password.decode('utf-8')
                flash('Admin credentials updated successfully.', 'success')
            else:
                new_admin = EntityAdmin(
                    username=username,
                    password_hash=hashed_password.decode('utf-8'),
                    entity_id=entity.id
                )
                db.add(new_admin)
                flash('Admin credentials assigned successfully.', 'success')

            db.commit()
            # db.close() will be handled by finally
            return redirect(url_for('admin.list_entities'))
        except IntegrityError:
            db.rollback()
            flash('Error assigning credentials: Username might already exist.', 'danger')
        except Exception as e:
            db.rollback()
            flash(f'An unexpected error occurred: {e}', 'danger')
        finally:
            if db.is_active: db.close() # Ensure session is closed

        # If error, re-render form (db is closed by finally)
        return render_template('entities/assign_admin.html', entity=entity, entity_admin=entity_admin, username=username)

    # For GET request
    db.close()
    return render_template('entities/assign_admin.html', entity=entity, entity_admin=entity_admin)
