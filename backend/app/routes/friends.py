from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import db, User
from app.models.friendship import Friendship
from sqlalchemy import or_, and_

friends_bp = Blueprint('friends', __name__, url_prefix='/api/friends')

@friends_bp.route('', methods=['GET'])
@jwt_required()
def get_friends():
    try:
        user_id = int(get_jwt_identity())

        # Get accepted friendships
        friendships = Friendship.query.filter(
            and_(
                or_(Friendship.user_id == user_id, Friendship.friend_id == user_id),
                Friendship.status == 'accepted'
            )
        ).all()

        friends_list = []
        for friendship in friendships:
            # Get the friend (the other person in the friendship)
            friend = friendship.friend if friendship.user_id == user_id else friendship.user
            friends_list.append(friend.to_dict())

        return jsonify(friends_list), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_friend_requests():
    try:
        user_id = int(get_jwt_identity())

        # Get pending friend requests sent to this user
        requests = Friendship.query.filter_by(
            friend_id=user_id,
            status='pending'
        ).all()

        return jsonify([req.to_dict() for req in requests]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/requests/sent', methods=['GET'])
@jwt_required()
def get_sent_requests():
    try:
        user_id = int(get_jwt_identity())

        # Get pending friend requests sent by this user
        requests = Friendship.query.filter_by(
            user_id=user_id,
            status='pending'
        ).all()

        return jsonify([req.to_dict() for req in requests]), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/add/<int:friend_id>', methods=['POST'])
@jwt_required()
def send_friend_request(friend_id):
    try:
        user_id = int(get_jwt_identity())

        if user_id == friend_id:
            return jsonify({'error': 'Cannot add yourself as friend'}), 400

        # Check if friend exists
        friend = User.query.get(friend_id)
        if not friend:
            return jsonify({'error': 'User not found'}), 404

        # Check if friendship already exists
        existing = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == user_id)
            )
        ).first()

        if existing:
            return jsonify({'error': 'Friend request already exists'}), 400

        # Create friendship request
        friendship = Friendship(user_id=user_id, friend_id=friend_id)
        db.session.add(friendship)
        db.session.commit()

        return jsonify(friendship.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/requests/<int:request_id>/accept', methods=['POST'])
@jwt_required()
def accept_friend_request(request_id):
    try:
        user_id = int(get_jwt_identity())

        friendship = Friendship.query.get(request_id)
        if not friendship:
            return jsonify({'error': 'Friend request not found'}), 404

        if friendship.friend_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        friendship.status = 'accepted'
        db.session.commit()

        return jsonify(friendship.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/requests/<int:request_id>/reject', methods=['POST'])
@jwt_required()
def reject_friend_request(request_id):
    try:
        user_id = int(get_jwt_identity())

        friendship = Friendship.query.get(request_id)
        if not friendship:
            return jsonify({'error': 'Friend request not found'}), 404

        if friendship.friend_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        friendship.status = 'rejected'
        db.session.commit()

        return jsonify(friendship.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@friends_bp.route('/<int:friend_id>', methods=['DELETE'])
@jwt_required()
def remove_friend(friend_id):
    try:
        user_id = int(get_jwt_identity())

        friendship = Friendship.query.filter(
            or_(
                and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                and_(Friendship.user_id == friend_id, Friendship.friend_id == user_id)
            )
        ).first()

        if not friendship:
            return jsonify({'error': 'Friendship not found'}), 404

        db.session.delete(friendship)
        db.session.commit()

        return jsonify({'message': 'Friend removed successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
