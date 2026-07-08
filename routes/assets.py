from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from models import Asset, Asset_Category
from forms import AssetForm
from routes.helpers import admin_required

assets_bp = Blueprint('assets', __name__, url_prefix='/assets')


@assets_bp.route('')
@login_required
def asset_list():
    page = request.args.get('page', 1, type=int)
    search_query = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '')
    category_filter = request.args.get('category', '', type=int)

    query = Asset.query

    if search_query:
        search_term = f'%{search_query}%'
        query = query.filter(
            db.or_(
                Asset.asset_tag.ilike(search_term),
                Asset.name.ilike(search_term),
                Asset.serial_number.ilike(search_term),
                Asset.description.ilike(search_term),
            )
        )

    if status_filter:
        query = query.filter_by(status=status_filter)

    if category_filter:
        query = query.filter_by(category_id=category_filter)

    assets = query.order_by(Asset.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )

    categories = Asset_Category.query.all()
    statuses = ['Available', 'In Use', 'Maintenance', 'Retired']

    return render_template('assets/list.html', assets=assets, categories=categories,
                           statuses=statuses, status_filter=status_filter,
                           category_filter=category_filter, search_query=search_query)


@assets_bp.route('/<int:id>')
@login_required
def asset_view(id):
    asset = Asset.query.get_or_404(id)
    return render_template('assets/view.html', asset=asset)


@assets_bp.route('/create', methods=['GET', 'POST'])
@login_required
def asset_create():
    form = AssetForm()

    if form.validate_on_submit():
        asset = Asset(
            asset_tag=form.asset_tag.data,
            name=form.name.data,
            description=form.description.data,
            serial_number=form.serial_number.data,
            purchase_date=form.purchase_date.data,
            purchase_price=form.purchase_price.data,
            status=form.status.data,
            assigned_to_user_id=form.assigned_to_user_id.data if form.assigned_to_user_id.data > 0 else None,
            category_id=form.category_id.data,
            location_id=form.location_id.data,
            warranty_expiry=form.warranty_expiry.data
        )

        db.session.add(asset)
        db.session.commit()

        flash(f'Asset {asset.asset_tag} created successfully!', 'success')
        return redirect(url_for('assets.asset_list'))

    return render_template('assets/create.html', form=form)


@assets_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def asset_edit(id):
    asset = Asset.query.get_or_404(id)
    form = AssetForm(obj=asset)
    form.original_asset_tag = asset.asset_tag

    if not current_user.is_admin():
        if asset.assigned_to_user_id != current_user.id:
            flash('You can only edit assets assigned to you.', 'error')
            return redirect(url_for('assets.asset_list'))

        del form.asset_tag
        del form.purchase_date
        del form.purchase_price
        del form.assigned_to_user_id
        del form.category_id
        del form.location_id
        del form.warranty_expiry

    if form.validate_on_submit():
        if current_user.is_admin():
            asset.asset_tag = form.asset_tag.data
            asset.name = form.name.data
            asset.description = form.description.data
            asset.serial_number = form.serial_number.data
            asset.purchase_date = form.purchase_date.data
            asset.purchase_price = form.purchase_price.data
            asset.status = form.status.data
            asset.assigned_to_user_id = form.assigned_to_user_id.data if form.assigned_to_user_id.data > 0 else None
            asset.category_id = form.category_id.data
            asset.location_id = form.location_id.data
            asset.warranty_expiry = form.warranty_expiry.data
        else:
            asset.description = form.description.data
            asset.status = form.status.data

        db.session.commit()
        flash(f'Asset {asset.asset_tag} updated successfully!', 'success')
        return redirect(url_for('assets.asset_view', id=asset.id))

    return render_template('assets/edit.html', form=form, asset=asset)


@assets_bp.route('/<int:id>/delete', methods=['POST'])
@admin_required
def asset_delete(id):
    asset = Asset.query.get_or_404(id)
    asset_tag = asset.asset_tag

    db.session.delete(asset)
    db.session.commit()

    flash(f'Asset {asset_tag} deleted successfully!', 'success')
    return redirect(url_for('assets.asset_list'))
