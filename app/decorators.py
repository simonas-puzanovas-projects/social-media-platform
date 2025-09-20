from functools import wraps
from flask import session, redirect, url_for, jsonify, request

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # For AJAX requests, return JSON error
            if request.is_json or request.headers.get('Content-Type') == 'application/json':
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            # For regular requests, redirect to login
            return redirect(url_for('bp_auth.login'))
        return f(*args, **kwargs)
    return decorated_function