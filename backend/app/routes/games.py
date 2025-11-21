from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.models.user import db
from app.models.game import Game
from app.models.user_game import UserGame
import os
from datetime import datetime

games_bp = Blueprint('games', __name__, url_prefix='/api/games')

ALLOWED_EXTENSIONS = {'exe', 'msi', 'zip', 'rar', '7z'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename, allowed_set):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_set

@games_bp.route('', methods=['GET'])
@jwt_required()
def get_games():
    try:
        # Get search query parameter
        search = request.args.get('search', '').strip()

        # Build query
        query = Game.query.filter_by(is_available=True)

        # Apply search filter if provided
        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                db.or_(
                    Game.title.ilike(search_filter),
                    Game.developer.ilike(search_filter),
                    Game.publisher.ilike(search_filter),
                    Game.genre.ilike(search_filter)
                )
            )

        games = query.all()
        return jsonify([game.to_dict() for game in games]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('/<int:game_id>', methods=['GET'])
@jwt_required()
def get_game(game_id):
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404
        return jsonify(game.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('', methods=['POST'])
@jwt_required()
def create_game():
    try:
        from config import Config

        data = request.form
        title = data.get('title')

        if not title:
            return jsonify({'error': 'Title is required'}), 400

        # Create game entry
        game = Game(
            title=title,
            description=data.get('description'),
            publisher=data.get('publisher'),
            developer=data.get('developer'),
            genre=data.get('genre'),
            version=data.get('version')
        )

        # Handle release date
        if data.get('release_date'):
            try:
                game.release_date = datetime.strptime(data['release_date'], '%Y-%m-%d').date()
            except:
                pass

        # Handle file upload
        if 'game_file' in request.files:
            file = request.files['game_file']
            if file and allowed_file(file.filename, ALLOWED_EXTENSIONS):
                filename = secure_filename(file.filename)
                # Create unique filename
                unique_filename = f"{datetime.utcnow().timestamp()}_{filename}"
                filepath = os.path.join(Config.GAMES_FOLDER, unique_filename)
                file.save(filepath)
                game.file_path = unique_filename
                game.file_size = os.path.getsize(filepath)

        # Handle cover image
        if 'cover_image' in request.files:
            file = request.files['cover_image']
            if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.utcnow().timestamp()}_{filename}"
                filepath = os.path.join(Config.COVERS_FOLDER, unique_filename)
                file.save(filepath)
                game.cover_image = unique_filename

        # Handle banner image
        if 'banner_image' in request.files:
            file = request.files['banner_image']
            if file and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
                filename = secure_filename(file.filename)
                unique_filename = f"{datetime.utcnow().timestamp()}_{filename}"
                filepath = os.path.join(Config.COVERS_FOLDER, unique_filename)
                file.save(filepath)
                game.banner_image = unique_filename

        db.session.add(game)
        db.session.commit()

        return jsonify(game.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@games_bp.route('/<int:game_id>/download', methods=['GET'])
@jwt_required()
def download_game(game_id):
    try:
        from config import Config

        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        if not game.file_path:
            return jsonify({'error': 'Game file not available'}), 404

        filepath = os.path.join(Config.GAMES_FOLDER, game.file_path)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Game file not found on server'}), 404

        # Increment download count
        game.download_count += 1
        db.session.commit()

        return send_file(filepath, as_attachment=True, download_name=game.file_path)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('/<int:game_id>/cover', methods=['GET'])
def get_cover(game_id):
    try:
        from config import Config

        game = Game.query.get(game_id)
        if not game or not game.cover_image:
            return jsonify({'error': 'Cover image not found'}), 404

        filepath = os.path.join(Config.COVERS_FOLDER, game.cover_image)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Cover image file not found'}), 404

        return send_file(filepath)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@games_bp.route('/<int:game_id>', methods=['DELETE'])
@jwt_required()
def delete_game(game_id):
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        db.session.delete(game)
        db.session.commit()

        return jsonify({'message': 'Game deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
