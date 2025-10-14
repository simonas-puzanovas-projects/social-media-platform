from functools import wraps
from flask import session, redirect, url_for, jsonify, request

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"success": False}), 401

        return f(*args, **kwargs)
    return decorated_function