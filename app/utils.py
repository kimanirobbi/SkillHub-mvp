from functools import wraps
from flask import abort
from flask_login import current_user, login_required

def role_required(role):
    """Decorator to restrict access based on user role"""
    def wrapper(fn):
        @wraps(fn)
        @login_required
        def decorated_view(*args, **kwargs):
            if current_user.role != role:
                abort(403)  # Forbidden
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
