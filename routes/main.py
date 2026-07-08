from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from models import Asset

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')


@main_bp.route('/dashboard')
@login_required
def dashboard():
    total_assets = Asset.query.count()
    available_assets = Asset.query.filter_by(status='Available').count()
    in_use_assets = Asset.query.filter_by(status='In Use').count()
    maintenance_assets = Asset.query.filter_by(status='Maintenance').count()

    recent_assets = Asset.query.order_by(Asset.created_at.desc()).limit(5).all()

    return render_template('dashboard.html',
                           total_assets=total_assets,
                           available_assets=available_assets,
                           in_use_assets=in_use_assets,
                           maintenance_assets=maintenance_assets,
                           recent_assets=recent_assets)
