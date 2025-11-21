from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import db, User
from app.models.user_game import UserGame
from app.models.game import Game
from datetime import datetime

users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/library', methods=['GET'])
@jwt_required()
def get_library():
    try:
        user_id = int(get_jwt_identity())
        user_games = UserGame.query.filter_by(user_id=user_id).all()
        return jsonify([ug.to_dict() for ug in user_games]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/library/<int:game_id>', methods=['POST'])
@jwt_required()
def add_to_library(game_id):
    try:
        user_id = int(get_jwt_identity())

        # Check if game exists
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        # Check if already in library
        existing = UserGame.query.filter_by(user_id=user_id, game_id=game_id).first()
        if existing:
            return jsonify({'error': 'Game already in library'}), 400

        # Add to library
        user_game = UserGame(user_id=user_id, game_id=game_id)
        db.session.add(user_game)
        db.session.commit()

        return jsonify(user_game.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/library/<int:game_id>', methods=['DELETE'])
@jwt_required()
def remove_from_library(game_id):
    try:
        user_id = int(get_jwt_identity())

        user_game = UserGame.query.filter_by(user_id=user_id, game_id=game_id).first()
        if not user_game:
            return jsonify({'error': 'Game not in library'}), 404

        db.session.delete(user_game)
        db.session.commit()

        return jsonify({'message': 'Game removed from library'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/library/<int:game_id>', methods=['PATCH'])
@jwt_required()
def update_library_game(game_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        user_game = UserGame.query.filter_by(user_id=user_id, game_id=game_id).first()
        if not user_game:
            return jsonify({'error': 'Game not in library'}), 404

        # Update fields
        if 'is_installed' in data:
            user_game.is_installed = data['is_installed']
            if data['is_installed']:
                user_game.installed_at = datetime.utcnow()

        if 'install_path' in data:
            user_game.install_path = data['install_path']

        if 'executable_path' in data:
            user_game.executable_path = data['executable_path']

        if 'playtime_minutes' in data:
            user_game.playtime_minutes = data['playtime_minutes']

        if 'last_played' in data:
            user_game.last_played = datetime.utcnow()

        if 'is_favorite' in data:
            user_game.is_favorite = data['is_favorite']

        if 'download_progress' in data:
            user_game.download_progress = data['download_progress']

        if 'is_downloading' in data:
            user_game.is_downloading = data['is_downloading']

        db.session.commit()

        return jsonify(user_game.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get stats
        total_games = UserGame.query.filter_by(user_id=user_id).count()
        total_playtime = db.session.query(db.func.sum(UserGame.playtime_minutes)).filter_by(user_id=user_id).scalar() or 0

        profile = user.to_dict(include_email=True)
        profile['stats'] = {
            'total_games': total_games,
            'total_playtime_hours': round(total_playtime / 60, 1)
        }

        return jsonify(profile), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    try:
        user_id = int(get_jwt_identity())
        user = User.query.get(user_id)
        data = request.get_json()

        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Update fields
        if 'display_name' in data:
            user.display_name = data['display_name']

        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']

        db.session.commit()

        return jsonify(user.to_dict(include_email=True)), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@users_bp.route('/search', methods=['GET'])
@jwt_required()
def search_users():
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify([]), 200

        users = User.query.filter(
            (User.username.ilike(f'%{query}%')) | (User.display_name.ilike(f'%{query}%'))
        ).limit(20).all()

        return jsonify([user.to_dict() for user in users]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
