from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from models import User, Asset
from routes.helpers import admin_required

users_bp = Blueprint('users', __name__)


@users_bp.route('/users')
@admin_required
def user_list():
    users = User.query.order_by(User.username).all()
    return render_template('users/list.html', users=users)


@users_bp.route('/users/<int:id>/toggle-active', methods=['POST'])
@admin_required
def user_toggle_active(id):
    user = User.query.get_or_404(id)

    if user.id == current_user.id:
        flash('You cannot deactivate your own account.', 'error')
        return redirect(url_for('users.user_list'))

    user.is_active = not user.is_active
    db.session.commit()

    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.username} has been {status}.', 'success')
    return redirect(url_for('users.user_list'))


@users_bp.route('/profile')
@login_required
def user_profile():
    user_assets = Asset.query.filter_by(assigned_to_user_id=current_user.id).all()
    return render_template('users/profile.html', user_assets=user_assets)
