"""
Admin authentication middleware for Flask routes.
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User

def admin_required(fn):
    """
    Decorator to require admin privileges for a route.
    Must be used after @jwt_required() decorator.
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verify JWT token first
        verify_jwt_in_request()

        # Get current user from JWT
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403

        return fn(*args, **kwargs)

    return wrapper
