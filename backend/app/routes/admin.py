"""
Admin-only API routes for GameManager.
Requires admin authentication for all endpoints.
"""

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, db
from app.models.game import Game
from app.models.user_game import UserGame
from app.models.game_request import GameRequest
from app.models.friendship import Friendship
from app.middleware.admin_required import admin_required
from werkzeug.utils import secure_filename
from datetime import datetime
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# =============================================================================
# STATISTICS & DASHBOARD
# =============================================================================

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_statistics():
    """Get overall system statistics for admin dashboard."""
    try:
        # User statistics
        total_users = User.query.count()
        online_users = User.query.filter_by(is_online=True).count()
        admin_users = User.query.filter_by(is_admin=True).count()

        # Game statistics
        total_games = Game.query.count()
        available_games = Game.query.filter_by(is_available=True).count()
        total_downloads = db.session.query(db.func.sum(Game.download_count)).scalar() or 0

        # User engagement
        total_game_libraries = UserGame.query.count()
        total_installs = UserGame.query.filter_by(is_installed=True).count()
        total_playtime = db.session.query(db.func.sum(UserGame.playtime_minutes)).scalar() or 0

        # Social statistics
        total_friendships = Friendship.query.filter_by(status='accepted').count()
        pending_requests = Friendship.query.filter_by(status='pending').count()

        # Game requests
        total_game_requests = GameRequest.query.count()
        pending_game_requests = GameRequest.query.filter_by(status='pending').count()

        # Recent activity
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        recent_games = Game.query.order_by(Game.created_at.desc()).limit(5).all()

        return jsonify({
            'users': {
                'total': total_users,
                'online': online_users,
                'admins': admin_users
            },
            'games': {
                'total': total_games,
                'available': available_games,
                'total_downloads': total_downloads
            },
            'engagement': {
                'total_libraries': total_game_libraries,
                'total_installs': total_installs,
                'total_playtime_hours': round(total_playtime / 60, 2)
            },
            'social': {
                'total_friendships': total_friendships,
                'pending_requests': pending_requests
            },
            'game_requests': {
                'total': total_game_requests,
                'pending': pending_game_requests
            },
            'recent_users': [user.to_dict() for user in recent_users],
            'recent_games': [game.to_dict() for game in recent_games]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# USER MANAGEMENT
# =============================================================================

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_all_users():
    """Get all users with detailed information."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)

        query = User.query

        # Search filter
        if search:
            query = query.filter(
                (User.username.ilike(f'%{search}%')) |
                (User.email.ilike(f'%{search}%')) |
                (User.display_name.ilike(f'%{search}%'))
            )

        # Pagination
        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        users_data = []
        for user in pagination.items:
            user_dict = user.to_dict(include_email=True, include_admin=True)
            # Add additional stats
            user_dict['game_count'] = UserGame.query.filter_by(user_id=user.id).count()
            user_dict['friend_count'] = Friendship.query.filter(
                ((Friendship.user_id == user.id) | (Friendship.friend_id == user.id)),
                Friendship.status == 'accepted'
            ).count()
            users_data.append(user_dict)

        return jsonify({
            'users': users_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@admin_required
def get_user_detail(user_id):
    """Get detailed information about a specific user."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user_dict = user.to_dict(include_email=True, include_admin=True)

        # Get user's games
        user_games = UserGame.query.filter_by(user_id=user_id).all()
        games_data = []
        for ug in user_games:
            game_data = ug.game.to_dict()
            game_data['playtime_minutes'] = ug.playtime_minutes
            game_data['is_installed'] = ug.is_installed
            game_data['last_played'] = ug.last_played.isoformat() if ug.last_played else None
            games_data.append(game_data)

        # Get friends
        friendships = Friendship.query.filter(
            ((Friendship.user_id == user_id) | (Friendship.friend_id == user_id)),
            Friendship.status == 'accepted'
        ).all()

        friends_data = []
        for friendship in friendships:
            friend = friendship.friend if friendship.user_id == user_id else friendship.user
            friends_data.append(friend.to_dict())

        # Get game requests
        game_requests = GameRequest.query.filter_by(user_id=user_id).all()
        requests_data = [req.to_dict() for req in game_requests]

        user_dict['games'] = games_data
        user_dict['friends'] = friends_data
        user_dict['game_requests'] = requests_data

        return jsonify(user_dict), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_user(user_id):
    """Update user information."""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.get_json()

        # Update allowed fields
        if 'username' in data:
            # Check if username already exists
            existing = User.query.filter_by(username=data['username']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Username already exists'}), 400
            user.username = data['username']

        if 'email' in data:
            # Check if email already exists
            existing = User.query.filter_by(email=data['email']).first()
            if existing and existing.id != user_id:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']

        if 'display_name' in data:
            user.display_name = data['display_name']

        if 'is_admin' in data:
            user.is_admin = data['is_admin']

        if 'password' in data and data['password']:
            user.set_password(data['password'])

        db.session.commit()

        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict(include_email=True, include_admin=True)
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_user(user_id):
    """Delete a user (cannot delete yourself)."""
    try:
        current_user_id = get_jwt_identity()

        if current_user_id == user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        username = user.username
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'message': f'User {username} deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/users', methods=['POST'])
@jwt_required()
@admin_required
def create_user():
    """Create a new user."""
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400

        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400

        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            display_name=data.get('display_name', data['username']),
            is_admin=data.get('is_admin', False)
        )
        user.set_password(data['password'])

        db.session.add(user)
        db.session.commit()

        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict(include_email=True, include_admin=True)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# GAME MANAGEMENT
# =============================================================================

@admin_bp.route('/games', methods=['GET'])
@jwt_required()
@admin_required
def get_all_games_admin():
    """Get all games with admin details."""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)

        query = Game.query

        # Search filter
        if search:
            query = query.filter(
                (Game.title.ilike(f'%{search}%')) |
                (Game.description.ilike(f'%{search}%')) |
                (Game.developer.ilike(f'%{search}%')) |
                (Game.publisher.ilike(f'%{search}%'))
            )

        # Pagination
        pagination = query.order_by(Game.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        games_data = []
        for game in pagination.items:
            game_dict = game.to_dict()
            # Add additional stats
            game_dict['user_count'] = UserGame.query.filter_by(game_id=game.id).count()
            game_dict['install_count'] = UserGame.query.filter_by(
                game_id=game.id, is_installed=True
            ).count()
            games_data.append(game_dict)

        return jsonify({
            'games': games_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/games/<int:game_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_game(game_id):
    """Update game information."""
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        data = request.get_json()

        # Update allowed fields
        updatable_fields = [
            'title', 'description', 'publisher', 'developer',
            'genre', 'version', 'is_available', 'price'
        ]

        for field in updatable_fields:
            if field in data:
                setattr(game, field, data[field])

        if 'release_date' in data:
            try:
                game.release_date = datetime.fromisoformat(data['release_date']).date()
            except:
                pass

        game.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Game updated successfully',
            'game': game.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/games/<int:game_id>/toggle-availability', methods=['POST'])
@jwt_required()
@admin_required
def toggle_game_availability(game_id):
    """Toggle game availability."""
    try:
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        game.is_available = not game.is_available
        game.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': f'Game {"enabled" if game.is_available else "disabled"} successfully',
            'game': game.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# GAME REQUEST MANAGEMENT
# =============================================================================

@admin_bp.route('/game-requests', methods=['GET'])
@jwt_required()
@admin_required
def get_all_game_requests():
    """Get all game requests with user information."""
    try:
        status_filter = request.args.get('status', None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        query = GameRequest.query

        if status_filter:
            query = query.filter_by(status=status_filter)

        pagination = query.order_by(GameRequest.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        requests_data = []
        for req in pagination.items:
            req_dict = req.to_dict()
            req_dict['user'] = req.user.to_dict()
            requests_data.append(req_dict)

        return jsonify({
            'requests': requests_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/game-requests/<int:request_id>', methods=['PATCH'])
@jwt_required()
@admin_required
def update_game_request(request_id):
    """Update game request status and admin notes."""
    try:
        game_request = GameRequest.query.get(request_id)
        if not game_request:
            return jsonify({'error': 'Game request not found'}), 404

        data = request.get_json()

        if 'status' in data:
            game_request.status = data['status']

        if 'admin_notes' in data:
            game_request.admin_notes = data['admin_notes']

        game_request.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'message': 'Game request updated successfully',
            'request': game_request.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# =============================================================================
# SYSTEM LOGS & ACTIVITY
# =============================================================================

@admin_bp.route('/activity', methods=['GET'])
@jwt_required()
@admin_required
def get_recent_activity():
    """Get recent system activity."""
    try:
        limit = request.args.get('limit', 50, type=int)

        # Recent user registrations
        recent_users = User.query.order_by(User.created_at.desc()).limit(limit).all()

        # Recent game additions
        recent_games = Game.query.order_by(Game.created_at.desc()).limit(limit).all()

        # Recent game requests
        recent_requests = GameRequest.query.order_by(GameRequest.created_at.desc()).limit(limit).all()

        activity = {
            'recent_users': [
                {
                    'type': 'user_registration',
                    'user': user.to_dict(),
                    'timestamp': user.created_at.isoformat()
                }
                for user in recent_users
            ],
            'recent_games': [
                {
                    'type': 'game_added',
                    'game': game.to_dict(),
                    'timestamp': game.created_at.isoformat()
                }
                for game in recent_games
            ],
            'recent_requests': [
                {
                    'type': 'game_request',
                    'request': req.to_dict(),
                    'user': req.user.to_dict(),
                    'timestamp': req.created_at.isoformat()
                }
                for req in recent_requests
            ]
        }

        return jsonify(activity), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# FILE MANAGEMENT
# =============================================================================

@admin_bp.route('/files/cleanup', methods=['POST'])
@jwt_required()
@admin_required
def cleanup_orphaned_files():
    """Remove files that are no longer referenced in the database."""
    try:
        from pathlib import Path

        uploads_dir = Path(__file__).parent.parent.parent / 'uploads'
        games_dir = uploads_dir / 'games'
        covers_dir = uploads_dir / 'covers'

        removed_files = []

        # Clean up game files
        if games_dir.exists():
            for file in games_dir.iterdir():
                if file.is_file():
                    # Check if file is referenced in database
                    game = Game.query.filter(Game.file_path.contains(file.name)).first()
                    if not game:
                        file.unlink()
                        removed_files.append(f'games/{file.name}')

        # Clean up cover images
        if covers_dir.exists():
            for file in covers_dir.iterdir():
                if file.is_file():
                    # Check if file is referenced in database
                    game = Game.query.filter(
                        (Game.cover_image.contains(file.name)) |
                        (Game.banner_image.contains(file.name))
                    ).first()
                    if not game:
                        file.unlink()
                        removed_files.append(f'covers/{file.name}')

        return jsonify({
            'message': f'Cleanup completed. Removed {len(removed_files)} orphaned files.',
            'removed_files': removed_files
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# =============================================================================
# SCANNED GAMES MANAGEMENT
# =============================================================================

@admin_bp.route('/scanned-games', methods=['GET'])
@jwt_required()
@admin_required
def get_scanned_games():
    """Get all scanned games with pagination and search."""
    try:
        from app.models.scanned_game import ScannedGame
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '', type=str)
        status_filter = request.args.get('status', None)  # 'pending' or 'processed'

        query = ScannedGame.query

        # Search filter
        if search:
            query = query.filter(
                (ScannedGame.filename.ilike(f'%{search}%')) |
                (ScannedGame.suggested_title.ilike(f'%{search}%'))
            )

        # Status filter
        if status_filter == 'pending':
            query = query.filter_by(is_processed=False)
        elif status_filter == 'processed':
            query = query.filter_by(is_processed=True)

        # Pagination
        pagination = query.order_by(ScannedGame.detected_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'scanned_games': [sg.to_dict() for sg in pagination.items],
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/scanned-games/scan', methods=['POST'])
@jwt_required()
@admin_required
def scan_games_folder():
    """Trigger manual scan of scanned_games folder."""
    try:
        from app.services.scanner import GameScanner
        
        new_count = GameScanner.scan_folder()
        removed_count = GameScanner.sync_scanned_games()
        
        return jsonify({
            'message': 'Scan completed successfully',
            'new_files': new_count,
            'removed_entries': removed_count
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/scanned-games/<int:scanned_game_id>/add-to-library', methods=['POST'])
@jwt_required()
@admin_required
def add_scanned_game_to_library(scanned_game_id):
    """Add scanned game to library with optional metadata."""
    try:
        from app.services.scanner import GameScanner
        
        data = request.get_json() or {}
        
        # Move file and create game entry
        game = GameScanner.move_to_library(scanned_game_id, data)
        
        return jsonify({
            'message': 'Game added to library successfully',
            'game': game.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/scanned-games/<int:scanned_game_id>/title', methods=['PUT'])
@jwt_required()
@admin_required
def update_scanned_game_title(scanned_game_id):
    """Update suggested title for scanned game."""
    try:
        from app.models.scanned_game import ScannedGame
        
        scanned_game = ScannedGame.query.get(scanned_game_id)
        if not scanned_game:
            return jsonify({'error': 'Scanned game not found'}), 404
        
        data = request.get_json()
        if 'title' not in data:
            return jsonify({'error': 'Title is required'}), 400
        
        scanned_game.suggested_title = data['title']
        db.session.commit()
        
        return jsonify({
            'message': 'Title updated successfully',
            'scanned_game': scanned_game.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/scanned-games/<int:scanned_game_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_scanned_game(scanned_game_id):
    """Delete scanned game entry and optionally remove file."""
    try:
        from app.models.scanned_game import ScannedGame
        from config import Config

        scanned_game = ScannedGame.query.get(scanned_game_id)
        if not scanned_game:
            return jsonify({'error': 'Scanned game not found'}), 404

        if scanned_game.is_processed:
            return jsonify({'error': 'Cannot delete processed game'}), 400

        data = request.get_json() or {}
        remove_file = data.get('remove_file', False)

        # Optionally remove file
        if remove_file:
            filepath = os.path.join(Config.SCAN_FOLDER, scanned_game.file_path)
            if os.path.exists(filepath):
                os.remove(filepath)

        filename = scanned_game.filename
        db.session.delete(scanned_game)
        db.session.commit()

        return jsonify({
            'message': f'Scanned game "{filename}" deleted successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/scanned-games/<int:scanned_game_id>/fetch-cover', methods=['POST'])
@jwt_required()
@admin_required
def fetch_scanned_game_cover(scanned_game_id):
    """Fetch cover image for a scanned game from RAWG API."""
    try:
        from app.services.scanner import GameScanner

        result = GameScanner.fetch_and_save_cover(scanned_game_id)

        if 'error' in result:
            return jsonify(result), 404

        return jsonify({
            'message': 'Cover image fetched successfully',
            'cover_image': result['cover_image']
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/scanned-games/fetch-all-covers', methods=['POST'])
@jwt_required()
@admin_required
def fetch_all_scanned_covers():
    """Fetch cover images for all pending scanned games."""
    try:
        from app.models.scanned_game import ScannedGame
        from app.services.scanner import GameScanner

        # Get all unprocessed games without covers
        scanned_games = ScannedGame.query.filter_by(
            is_processed=False
        ).filter(
            (ScannedGame.cover_image == None) | (ScannedGame.cover_image == '')
        ).all()

        success_count = 0
        failed_count = 0

        for scanned_game in scanned_games:
            result = GameScanner.fetch_and_save_cover(scanned_game.id)
            if 'error' in result:
                failed_count += 1
            else:
                success_count += 1

        return jsonify({
            'message': f'Fetched {success_count} covers successfully',
            'success_count': success_count,
            'failed_count': failed_count,
            'total': len(scanned_games)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/covers/<path:filename>', methods=['GET'])
def get_cover_image(filename):
    """Serve cover images."""
    try:
        from flask import send_file
        from config import Config

        filepath = os.path.join(Config.COVERS_FOLDER, filename)
        if not os.path.exists(filepath):
            return jsonify({'error': 'Cover image not found'}), 404

        return send_file(filepath)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
