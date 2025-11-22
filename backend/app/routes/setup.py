"""
Setup routes for initial configuration
These routes help with initial setup and should be protected
"""
from flask import Blueprint, request, jsonify
from app.models.user import db, User
import os

setup_bp = Blueprint('setup', __name__, url_prefix='/api/setup')


@setup_bp.route('/promote-admin', methods=['POST'])
def promote_admin():
    """
    One-time setup endpoint to promote a user to admin
    Requires SETUP_SECRET environment variable to be set

    POST /api/setup/promote-admin
    Body: {
        "secret": "your-setup-secret",
        "username": "username-to-promote"
    }
    """
    try:
        # Get setup secret from environment
        setup_secret = os.environ.get('SETUP_SECRET')

        if not setup_secret:
            return jsonify({
                'error': 'Setup not configured. Please set SETUP_SECRET environment variable.'
            }), 501

        data = request.get_json()

        # Verify secret
        if not data.get('secret') or data.get('secret') != setup_secret:
            return jsonify({'error': 'Invalid setup secret'}), 403

        # Get username to promote
        username = data.get('username')
        if not username:
            return jsonify({'error': 'Username required'}), 400

        # Find and promote user
        user = User.query.filter_by(username=username).first()

        if not user:
            return jsonify({'error': f'User "{username}" not found'}), 404

        if user.is_admin:
            return jsonify({
                'message': f'User "{username}" is already an admin',
                'user': user.to_dict(include_admin=True)
            }), 200

        # Promote to admin
        user.is_admin = True
        db.session.commit()

        return jsonify({
            'message': f'Successfully promoted "{username}" to admin',
            'user': user.to_dict(include_admin=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@setup_bp.route('/status', methods=['GET'])
def setup_status():
    """
    Check if initial setup is needed
    Returns information about admin users and setup status
    """
    try:
        total_users = User.query.count()
        admin_users = User.query.filter_by(is_admin=True).count()
        setup_secret_configured = bool(os.environ.get('SETUP_SECRET'))

        return jsonify({
            'total_users': total_users,
            'admin_users': admin_users,
            'setup_secret_configured': setup_secret_configured,
            'needs_setup': admin_users == 0
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
