"""
Payment API routes for GameManager.
Handles GCash payment integration and transaction management.
"""

from flask import Blueprint, jsonify, request, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User, db
from app.models.game import Game
from app.models.user_game import UserGame
from app.models.payment import Payment
from datetime import datetime
from app.services.telegram_notifier import get_telegram_notifier

payments_bp = Blueprint('payments', __name__, url_prefix='/api/payments')

# =============================================================================
# PAYMENT INITIATION & PROCESSING
# =============================================================================

@payments_bp.route('/create', methods=['POST'])
@jwt_required()
def create_payment():
    """
    Create a payment for a game purchase.
    This initiates a GCash payment transaction.
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        if 'game_id' not in data:
            return jsonify({'error': 'game_id is required'}), 400

        game_id = data['game_id']

        # Get game
        game = Game.query.get(game_id)
        if not game:
            return jsonify({'error': 'Game not found'}), 404

        if not game.is_available:
            return jsonify({'error': 'Game is not available for purchase'}), 400

        # Check if user already owns the game
        existing_user_game = UserGame.query.filter_by(
            user_id=current_user_id,
            game_id=game_id
        ).first()

        if existing_user_game:
            return jsonify({'error': 'You already own this game'}), 400

        # Check if game is free
        if game.price <= 0:
            # Automatically add to library for free games
            user_game = UserGame(
                user_id=current_user_id,
                game_id=game_id
            )
            db.session.add(user_game)
            db.session.commit()

            return jsonify({
                'message': 'Free game added to your library',
                'game': game.to_dict()
            }), 200

        # Create payment record
        payment = Payment(
            user_id=current_user_id,
            game_id=game_id,
            amount=game.price,
            payment_method='gcash',
            status='pending'
        )

        db.session.add(payment)
        db.session.commit()

        # In production, this would integrate with GCash API
        # For now, return payment details for manual processing
        return jsonify({
            'message': 'Payment initiated',
            'payment': payment.to_dict(),
            'instructions': {
                'method': 'GCash',
                'amount': game.price,
                'payment_id': payment.id,
                'note': 'Please send payment via GCash and provide the reference number'
            }
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/<int:payment_id>/qrcode', methods=['GET'])
@jwt_required(optional=True)
def get_payment_qrcode(payment_id):
    """
    Serve the static GCash QR code for payment.
    Returns the merchant's pre-made GCash QR code image.
    """
    try:
        # Get payment
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Verify ownership (if authenticated)
        current_user_id = get_jwt_identity()
        if current_user_id and payment.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        # Serve the static QR code image
        import os
        qr_code_path = os.path.join(current_app.config['BASE_DIR'], 'static', 'gcash_qr.jpg')

        if not os.path.exists(qr_code_path):
            return jsonify({'error': 'QR code image not found'}), 404

        return send_file(qr_code_path, mimetype='image/jpeg')

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/<int:payment_id>/confirm', methods=['POST'])
@jwt_required()
def confirm_payment(payment_id):
    """
    Confirm payment with GCash reference number.
    User submits their GCash transaction reference after payment.
    """
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()

        # Get payment
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Verify ownership - ensure both IDs are the same type (int)
        if int(payment.user_id) != int(current_user_id):
            print(f"Authorization failed: payment.user_id={payment.user_id} ({type(payment.user_id)}), current_user_id={current_user_id} ({type(current_user_id)})")
            return jsonify({'error': 'Unauthorized'}), 403

        # Check if already completed
        if payment.status == 'completed':
            return jsonify({'error': 'Payment already completed'}), 400

        # Validate reference number
        if 'reference_number' not in data:
            return jsonify({'error': 'GCash reference number is required'}), 400

        # Update payment with reference number
        payment.gcash_reference_number = data['reference_number']
        payment.gcash_transaction_id = data.get('transaction_id', '')
        payment.status = 'pending_verification'  # Waiting for admin verification

        db.session.commit()

        # Send Telegram notification to admin when reference code is submitted
        try:
            user = User.query.get(current_user_id)
            game = Game.query.get(payment.game_id)
            notifier = get_telegram_notifier()
            if notifier and notifier.bot_token:
                notifier.send_new_payment_notification({
                    'id': payment.id,
                    'game_title': game.title if game else 'N/A',
                    'amount': payment.amount,
                    'username': user.username if user else 'Unknown',
                    'reference_number': payment.gcash_reference_number,
                    'status': payment.status
                })
            else:
                print("Telegram bot not configured, skipping notification")
        except Exception as e:
            # Don't fail the payment if notification fails
            print(f"Failed to send Telegram notification: {e}")
            pass

        return jsonify({
            'message': 'Payment submitted for verification',
            'payment': payment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/<int:payment_id>/verify', methods=['POST'])
@jwt_required()
def verify_payment(payment_id):
    """
    Admin endpoint to verify and approve payment.
    This is called by admins after confirming GCash payment receipt.
    """
    try:
        from app.middleware.admin_required import admin_required

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403

        # Get payment
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Check if already completed
        if payment.status == 'completed':
            return jsonify({'error': 'Payment already verified'}), 400

        # Mark payment as completed
        payment.status = 'completed'
        payment.completed_at = datetime.utcnow()

        # Add game to user's library
        user_game = UserGame(
            user_id=payment.user_id,
            game_id=payment.game_id
        )

        db.session.add(user_game)
        db.session.commit()

        # Send Telegram notification for approval (non-blocking)
        try:
            payment_user = User.query.get(payment.user_id)
            notifier = get_telegram_notifier()
            if notifier and notifier.bot_token:
                notifier.send_payment_approved_notification({
                    'id': payment.id,
                    'game_title': payment.game.title if payment.game else 'N/A',
                    'amount': payment.amount,
                    'username': payment_user.username if payment_user else 'Unknown'
                })
            else:
                print("Telegram bot not configured, skipping notification")
        except Exception as e:
            # Don't fail the request if notification fails
            print(f"Failed to send Telegram approval notification: {e}")
            pass

        return jsonify({
            'message': 'Payment verified and game added to user library',
            'payment': payment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/<int:payment_id>/reject', methods=['POST'])
@jwt_required()
def reject_payment(payment_id):
    """
    Admin endpoint to reject a payment.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403

        data = request.get_json()

        # Get payment
        payment = Payment.query.get(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        # Mark payment as failed
        payment.status = 'failed'

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Database error while rejecting payment: {e}")
            return jsonify({'error': 'Failed to update payment status'}), 500

        # Send Telegram notification for rejection (non-blocking)
        try:
            payment_user = User.query.get(payment.user_id)
            notifier = get_telegram_notifier()
            if notifier and notifier.bot_token:
                notifier.send_payment_rejected_notification({
                    'id': payment.id,
                    'game_title': payment.game.title if payment.game else 'N/A',
                    'amount': payment.amount,
                    'username': payment_user.username if payment_user else 'Unknown'
                })
            else:
                print("Telegram bot not configured, skipping notification")
        except Exception as e:
            # Don't fail the request if notification fails
            print(f"Failed to send Telegram rejection notification: {e}")
            pass

        return jsonify({
            'message': 'Payment rejected',
            'payment': payment.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# PAYMENT HISTORY & MANAGEMENT
# =============================================================================

@payments_bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get payment history for the current user."""
    try:
        current_user_id = get_jwt_identity()

        payments = Payment.query.filter_by(user_id=current_user_id).order_by(
            Payment.created_at.desc()
        ).all()

        return jsonify({
            'payments': [payment.to_dict() for payment in payments]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/all', methods=['GET'])
@jwt_required()
def get_all_payments():
    """Admin endpoint to get all payments with filtering."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403

        # Get filters
        status = request.args.get('status', None)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)

        query = Payment.query

        # Filter by status
        if status:
            query = query.filter_by(status=status)

        # Pagination
        pagination = query.order_by(Payment.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        payments_data = []
        for payment in pagination.items:
            payment_dict = payment.to_dict()
            payment_dict['user'] = payment.user.to_dict()
            payments_data.append(payment_dict)

        return jsonify({
            'payments': payments_data,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_payment_stats():
    """Admin endpoint to get payment statistics."""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403

        # Total revenue
        total_revenue = db.session.query(
            db.func.sum(Payment.amount)
        ).filter_by(status='completed').scalar() or 0

        # Payment counts by status
        total_payments = Payment.query.count()
        completed_payments = Payment.query.filter_by(status='completed').count()
        pending_payments = Payment.query.filter_by(status='pending_verification').count()
        failed_payments = Payment.query.filter_by(status='failed').count()

        # Top selling games
        top_games = db.session.query(
            Game.id,
            Game.title,
            Game.price,
            db.func.count(Payment.id).label('sales_count'),
            db.func.sum(Payment.amount).label('revenue')
        ).join(
            Payment, Game.id == Payment.game_id
        ).filter(
            Payment.status == 'completed'
        ).group_by(
            Game.id
        ).order_by(
            db.func.count(Payment.id).desc()
        ).limit(10).all()

        top_games_data = [
            {
                'game_id': game.id,
                'title': game.title,
                'price': game.price,
                'sales_count': game.sales_count,
                'revenue': game.revenue
            }
            for game in top_games
        ]

        return jsonify({
            'total_revenue': total_revenue,
            'payment_counts': {
                'total': total_payments,
                'completed': completed_payments,
                'pending': pending_payments,
                'failed': failed_payments
            },
            'top_games': top_games_data
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@payments_bp.route('/test-telegram', methods=['POST'])
@jwt_required()
def test_telegram_connection():
    """
    Admin endpoint to test Telegram bot connection.
    Sends a test message to verify the configuration.
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403

        notifier = get_telegram_notifier()

        if not notifier.bot_token or not notifier.chat_id:
            return jsonify({
                'error': 'Telegram bot not configured',
                'details': 'Please check TELEGRAM_BOT_TOKEN and TELEGRAM_ADMIN_CHAT_ID in your .env file'
            }), 400

        success = notifier.test_connection()

        if success:
            return jsonify({
                'message': 'Telegram connection successful! Check your Telegram for the test message.',
                'bot_configured': True
            }), 200
        else:
            return jsonify({
                'error': 'Failed to send test message',
                'details': 'Chat not found. Make sure you have started a conversation with your bot and the chat_id is correct.'
            }), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
