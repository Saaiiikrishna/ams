from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.db_config import SessionLocal
from database.models import Entity, EntityAdmin # Assuming your models are in database.models
from sqlalchemy.exc import IntegrityError
import bcrypt # For password hashing

admin_bp = Blueprint('admin', __name__, template_folder='templates')

def get_db_session():
    return SessionLocal()

@admin_bp.route('/entities', methods=['GET'])
def list_entities():
    db = get_db_session()
    entities = db.query(Entity).order_by(Entity.id).all()
    db.close()
    return render_template('entities/list.html', entities=entities)

@admin_bp.route('/entities/create', methods=['GET', 'POST'])
def create_entity():
    if request.method == 'POST':
        db = get_db_session()
        try:
            new_entity = Entity(
                name=request.form['name'],
                address=request.form.get('address'),
                latitude=float(request.form['latitude']) if request.form.get('latitude') else None,
                longitude=float(request.form['longitude']) if request.form.get('longitude') else None,
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
            entity.name = request.form['name']
            entity.address = request.form.get('address')
            entity.latitude = float(request.form['latitude']) if request.form.get('latitude') else None
            entity.longitude = float(request.form['longitude']) if request.form.get('longitude') else None
            entity.contact_person_name = request.form.get('contact_person_name')
            entity.contact_person_mobile = request.form.get('contact_person_mobile')
            entity.email = request.form['email']
            db.commit()
            flash('Entity updated successfully!', 'success')
            # db.close() # already closed in finally
            return redirect(url_for('admin.list_entities'))
        except IntegrityError:
            db.rollback()
            flash('Error updating entity: Email might already exist for another entity.', 'danger')
        except Exception as e:
            db.rollback()
            flash(f'An unexpected error occurred: {e}', 'danger')
        # finally: # No finally here, render_template needs entity if error
            # if db.is_active: db.close() # Ensure close if an error happens before commit

        # If POST and error, re-render with entity
        # The session should still be active or reopened if necessary.
        # For simplicity, we assume the session is fine or rely on get_db_session() again if needed.
        # However, careful session management is crucial in complex scenarios.
        # Let's ensure the entity is passed back for the form.
        # db.close() # Close before rendering
        # return render_template('entities/update.html', entity=entity) # This was causing issues with session

    # If it's a GET request or a POST that failed and needs to re-render
    if request.method == 'POST': # an error occurred, entity is already loaded
        db.close() # close after error before re-rendering
        return render_template('entities/update.html', entity=entity)

    # For GET request
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
        if db.is_active: db.close()
    return redirect(url_for('admin.list_entities'))

@admin_bp.route('/entities/<int:entity_id>/assign_admin', methods=['GET', 'POST'])
def assign_admin_credentials(entity_id):
    db = get_db_session()
    entity = db.query(Entity).get(entity_id)
    if not entity:
        flash('Entity not found!', 'danger')
        db.close()
        return redirect(url_for('admin.list_entities'))

    # Assuming one admin per entity for now for simplicity, or find the first one.
    # A more complex system might allow multiple admins.
    entity_admin = db.query(EntityAdmin).filter_by(entity_id=entity.id).first()

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Username and password are required.', 'danger')
            db.close()
            return render_template('entities/assign_admin.html', entity=entity, entity_admin=entity_admin)

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        try:
            if entity_admin:
                # Update existing admin
                entity_admin.username = username
                entity_admin.password_hash = hashed_password.decode('utf-8')
                flash('Admin credentials updated successfully.', 'success')
            else:
                # Create new admin
                new_admin = EntityAdmin(
                    username=username,
                    password_hash=hashed_password.decode('utf-8'),
                    entity_id=entity.id
                )
                db.add(new_admin)
                flash('Admin credentials assigned successfully.', 'success')

            db.commit()
            db.close()
            return redirect(url_for('admin.list_entities'))
        except IntegrityError:
            db.rollback()
            flash('Error assigning credentials: Username might already exist.', 'danger')
        except Exception as e:
            db.rollback()
            flash(f'An unexpected error occurred: {e}', 'danger')
        finally:
            if db.is_active: db.close()
        # If error, re-render form
        return render_template('entities/assign_admin.html', entity=entity, entity_admin=entity_admin, username=username)


    db.close()
    return render_template('entities/assign_admin.html', entity=entity, entity_admin=entity_admin)
