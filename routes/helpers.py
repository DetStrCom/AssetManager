from functools import wraps
from flask import flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import security_logger


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_admin():
            security_logger.warning(
                f"ACCESS_DENIED: user={current_user.username} "
                f"path={request.path} ip={request.remote_addr}"
            )
            flash('You need admin privileges to access this page.', 'error')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
