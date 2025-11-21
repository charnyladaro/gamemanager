from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import db
from app.models.game_request import GameRequest

game_requests_bp = Blueprint('game_requests', __name__, url_prefix='/api/game-requests')

@game_requests_bp.route('', methods=['GET'])
@jwt_required()
def get_game_requests():
    try:
        user_id = int(get_jwt_identity())

        # Get all game requests from this user
        requests = GameRequest.query.filter_by(user_id=user_id).order_by(GameRequest.created_at.desc()).all()

        return jsonify([req.to_dict() for req in requests]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_requests_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_game_requests():
    try:
        # Get all game requests (for admin view)
        status_filter = request.args.get('status')

        query = GameRequest.query
        if status_filter:
            query = query.filter_by(status=status_filter)

        requests = query.order_by(GameRequest.created_at.desc()).all()

        return jsonify([req.to_dict() for req in requests]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@game_requests_bp.route('', methods=['POST'])
@jwt_required()
def create_game_request():
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        if not data.get('game_title'):
            return jsonify({'error': 'Game title is required'}), 400

        game_request = GameRequest(
            user_id=user_id,
            game_title=data['game_title'],
            description=data.get('description')
        )

        db.session.add(game_request)
        db.session.commit()

        return jsonify(game_request.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_requests_bp.route('/<int:request_id>', methods=['PATCH'])
@jwt_required()
def update_game_request(request_id):
    try:
        user_id = int(get_jwt_identity())
        data = request.get_json()

        game_request = GameRequest.query.get(request_id)
        if not game_request:
            return jsonify({'error': 'Game request not found'}), 404

        # Users can only edit their own requests
        # Admin check would go here in a real app
        if game_request.user_id != user_id:
            # Allow if admin (you'd need to add admin role check)
            pass

        # Update fields
        if 'status' in data:
            game_request.status = data['status']

        if 'admin_notes' in data:
            game_request.admin_notes = data['admin_notes']

        db.session.commit()

        return jsonify(game_request.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@game_requests_bp.route('/<int:request_id>', methods=['DELETE'])
@jwt_required()
def delete_game_request(request_id):
    try:
        user_id = int(get_jwt_identity())

        game_request = GameRequest.query.get(request_id)
        if not game_request:
            return jsonify({'error': 'Game request not found'}), 404

        # Users can only delete their own requests
        if game_request.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        db.session.delete(game_request)
        db.session.commit()

        return jsonify({'message': 'Game request deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
