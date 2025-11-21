from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.models.user import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()

        # Validate required fields
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400

        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            display_name=data.get('display_name', data['username'])
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        # Create access token (identity must be string)
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'message': 'User created successfully',
            'access_token': access_token,
            'user': user.to_dict(include_email=True, include_admin=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400

        # Find user
        user = User.query.filter_by(username=data['username']).first()

        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid username or password'}), 401

        # Update online status
        user.is_online = True
        user.last_seen = datetime.utcnow()
        db.session.commit()

        # Create access token (identity must be string)
        access_token = create_access_token(identity=str(user.id))

        return jsonify({
            'access_token': access_token,
            'user': user.to_dict(include_email=True, include_admin=True)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if user:
            user.is_online = False
            user.last_seen = datetime.utcnow()
            db.session.commit()

        return jsonify({'message': 'Logged out successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict(include_email=True, include_admin=True)), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
