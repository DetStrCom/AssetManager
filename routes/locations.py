from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required
from app import db
from models import Location
from forms import LocationForm
from routes.helpers import admin_required

locations_bp = Blueprint('locations', __name__, url_prefix='/locations')


@locations_bp.route('')
@login_required
def location_list():
    locations = Location.query.order_by(Location.office_name).all()
    return render_template('locations/list.html', locations=locations)


@locations_bp.route('/create', methods=['GET', 'POST'])
@admin_required
def location_create():
    form = LocationForm()

    if form.validate_on_submit():
        location = Location(
            office_name=form.office_name.data,
            address=form.address.data,
            city=form.city.data,
            country=form.country.data,
            contact_phone=form.contact_phone.data
        )

        db.session.add(location)
        db.session.commit()

        flash(f'Location {location.office_name} created successfully!', 'success')
        return redirect(url_for('locations.location_list'))

    return render_template('locations/create.html', form=form)


@locations_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def location_edit(id):
    location = Location.query.get_or_404(id)
    form = LocationForm(obj=location)

    if form.validate_on_submit():
        location.office_name = form.office_name.data
        location.address = form.address.data
        location.city = form.city.data
        location.country = form.country.data
        location.contact_phone = form.contact_phone.data

        db.session.commit()
        flash(f'Location {location.office_name} updated successfully!', 'success')
        return redirect(url_for('locations.location_list'))

    return render_template('locations/edit.html', form=form, location=location)


@locations_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def location_delete(id):
    location = Location.query.get_or_404(id)

    if location.assets:
        flash(f'Cannot delete "{location.office_name}" — it still has {len(location.assets)} asset(s) assigned.', 'error')
        return redirect(url_for('locations.location_list'))

    if location.users:
        flash(f'Cannot delete "{location.office_name}" — it still has {len(location.users)} user(s) assigned.', 'error')
        return redirect(url_for('locations.location_list'))

    name = location.office_name
    db.session.delete(location)
    db.session.commit()

    flash(f'Location {name} deleted successfully!', 'success')
    return redirect(url_for('locations.location_list'))
