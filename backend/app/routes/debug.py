"""
Temporary debug endpoint to check database users
DELETE THIS FILE AFTER USE - IT'S A SECURITY RISK
"""
from flask import Blueprint, jsonify
from app.models.user import User

debug_bp = Blueprint('debug', __name__, url_prefix='/api/debug')


@debug_bp.route('/users', methods=['GET'])
def list_users():
    """
    TEMPORARY DEBUG ENDPOINT - DELETE AFTER USE
    Lists all users in database (without sensitive info)
    """
    try:
        users = User.query.all()
        user_list = []

        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'is_admin': user.is_admin,
                'created_at': str(user.created_at)
            })

        return jsonify({
            'total_users': len(user_list),
            'users': user_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
