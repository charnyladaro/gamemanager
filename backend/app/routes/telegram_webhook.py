"""
Telegram Webhook Handler for GameManager Bot
Handles incoming updates from Telegram including button callbacks
"""

from flask import Blueprint, request, jsonify, current_app
from app.models.user import User, db
from app.models.game import Game
from app.models.payment import Payment
from app.models.user_game import UserGame
from app.services.telegram_notifier import get_telegram_notifier
from datetime import datetime
import logging
import hmac
import hashlib

logger = logging.getLogger(__name__)

telegram_webhook_bp = Blueprint('telegram_webhook', __name__, url_prefix='/api/telegram')


@telegram_webhook_bp.route('/webhook', methods=['POST'])
def telegram_webhook():
    """
    Webhook endpoint for receiving Telegram updates.
    Telegram will send updates to this endpoint when configured.
    """
    try:
        update = request.get_json()

        if not update:
            return jsonify({'error': 'No update data'}), 400

        logger.info(f"Received Telegram update: {update}")

        # Handle callback queries (button clicks)
        if 'callback_query' in update:
            return handle_callback_query(update['callback_query'])

        # Handle regular messages (for future expansion)
        if 'message' in update:
            return handle_message(update['message'])

        return jsonify({'ok': True}), 200

    except Exception as e:
        logger.error(f"Error processing Telegram webhook: {e}")
        return jsonify({'error': str(e)}), 500


def handle_callback_query(callback_query):
    """
    Handle callback queries from inline keyboard buttons

    Args:
        callback_query: The callback query object from Telegram

    Returns:
        JSON response
    """
    try:
        callback_data = callback_query.get('data', '')
        callback_id = callback_query.get('id')
        message = callback_query.get('message', {})
        chat_id = message.get('chat', {}).get('id')
        message_id = message.get('message_id')
        user = callback_query.get('from', {})

        logger.info(f"Processing callback: {callback_data}")

        notifier = get_telegram_notifier()

        # Verify this is from the admin chat
        admin_chat_id = current_app.config.get('TELEGRAM_ADMIN_CHAT_ID')
        if str(chat_id) != str(admin_chat_id):
            notifier.answer_callback_query(
                callback_id,
                "⚠️ Unauthorized. Only admin can perform this action.",
                show_alert=True
            )
            return jsonify({'ok': False, 'error': 'Unauthorized'}), 403

        # Parse callback data (format: "verify_123" or "reject_123")
        if '_' not in callback_data:
            notifier.answer_callback_query(callback_id, "Invalid action", show_alert=True)
            return jsonify({'ok': False, 'error': 'Invalid callback data'}), 400

        action, payment_id = callback_data.split('_', 1)
        payment_id = int(payment_id)

        # Get payment from database
        payment = Payment.query.get(payment_id)
        if not payment:
            notifier.answer_callback_query(
                callback_id,
                "❌ Payment not found in database",
                show_alert=True
            )
            return jsonify({'ok': False, 'error': 'Payment not found'}), 404

        # Check if payment is still pending
        if payment.status != 'pending_verification':
            status_text = payment.status.replace('_', ' ').title()
            notifier.answer_callback_query(
                callback_id,
                f"⚠️ Payment already processed (Status: {status_text})",
                show_alert=True
            )
            return jsonify({'ok': False, 'error': 'Payment already processed'}), 400

        # Process the action
        if action == 'verify':
            return process_verify_action(payment, callback_id, chat_id, message_id, notifier)
        elif action == 'reject':
            return process_reject_action(payment, callback_id, chat_id, message_id, notifier)
        else:
            notifier.answer_callback_query(callback_id, "Unknown action", show_alert=True)
            return jsonify({'ok': False, 'error': 'Unknown action'}), 400

    except Exception as e:
        logger.error(f"Error handling callback query: {e}")
        return jsonify({'error': str(e)}), 500


def process_verify_action(payment, callback_id, chat_id, message_id, notifier):
    """
    Process payment verification action

    Args:
        payment: Payment object
        callback_id: Telegram callback query ID
        chat_id: Telegram chat ID
        message_id: Telegram message ID
        notifier: TelegramNotifier instance

    Returns:
        JSON response
    """
    try:
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

        # Get user and game info for notification
        payment_user = User.query.get(payment.user_id)
        game = Game.query.get(payment.game_id)

        # Answer the callback query
        notifier.answer_callback_query(
            callback_id,
            "✅ Payment verified successfully!",
            show_alert=False
        )

        # Edit the original message to show it's been verified
        updated_message = f"""
✅ <b>PAYMENT VERIFIED</b>

🎮 <b>Game:</b> {game.title if game else 'N/A'}
💰 <b>Amount:</b> ₱{payment.amount:.2f}
👤 <b>User:</b> {payment_user.username if payment_user else 'Unknown'}
🆔 <b>Payment ID:</b> #{payment.id}
📱 <b>GCash Ref:</b> <code>{payment.gcash_reference_number}</code>
✅ <b>Status:</b> Completed

<i>Game has been added to user's library</i>
"""

        notifier.edit_message(
            chat_id,
            message_id,
            updated_message.strip()
        )

        logger.info(f"Payment {payment.id} verified successfully via Telegram")

        return jsonify({'ok': True, 'action': 'verified'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing verify action: {e}")
        notifier.answer_callback_query(
            callback_id,
            f"❌ Error: {str(e)}",
            show_alert=True
        )
        return jsonify({'error': str(e)}), 500


def process_reject_action(payment, callback_id, chat_id, message_id, notifier):
    """
    Process payment rejection action

    Args:
        payment: Payment object
        callback_id: Telegram callback query ID
        chat_id: Telegram chat ID
        message_id: Telegram message ID
        notifier: TelegramNotifier instance

    Returns:
        JSON response
    """
    try:
        # Mark payment as failed
        payment.status = 'failed'
        db.session.commit()

        # Get user and game info for notification
        payment_user = User.query.get(payment.user_id)
        game = Game.query.get(payment.game_id)

        # Answer the callback query
        notifier.answer_callback_query(
            callback_id,
            "❌ Payment rejected",
            show_alert=False
        )

        # Edit the original message to show it's been rejected
        updated_message = f"""
❌ <b>PAYMENT REJECTED</b>

🎮 <b>Game:</b> {game.title if game else 'N/A'}
💰 <b>Amount:</b> ₱{payment.amount:.2f}
👤 <b>User:</b> {payment_user.username if payment_user else 'Unknown'}
🆔 <b>Payment ID:</b> #{payment.id}
📱 <b>GCash Ref:</b> <code>{payment.gcash_reference_number}</code>
❌ <b>Status:</b> Rejected

<i>Payment has been rejected and user has been notified</i>
"""

        notifier.edit_message(
            chat_id,
            message_id,
            updated_message.strip()
        )

        logger.info(f"Payment {payment.id} rejected via Telegram")

        return jsonify({'ok': True, 'action': 'rejected'}), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error processing reject action: {e}")
        notifier.answer_callback_query(
            callback_id,
            f"❌ Error: {str(e)}",
            show_alert=True
        )
        return jsonify({'error': str(e)}), 500


def handle_message(message):
    """
    Handle regular text messages (for future expansion)

    Args:
        message: The message object from Telegram

    Returns:
        JSON response
    """
    # For now, just acknowledge the message
    # This can be expanded to handle commands like /start, /help, etc.
    logger.info(f"Received message: {message.get('text', '')}")
    return jsonify({'ok': True}), 200


@telegram_webhook_bp.route('/set-webhook', methods=['POST'])
def set_webhook():
    """
    Helper endpoint to set the Telegram webhook URL.
    Call this once to configure your bot to send updates to this server.

    Example: POST /api/telegram/set-webhook
    Body: {"url": "https://yourdomain.com/api/telegram/webhook"}
    """
    try:
        data = request.get_json()
        webhook_url = data.get('url')

        if not webhook_url:
            return jsonify({'error': 'webhook url is required'}), 400

        bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return jsonify({'error': 'Telegram bot token not configured'}), 500

        # Set webhook via Telegram API
        import requests
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/setWebhook"

        response = requests.post(telegram_api_url, json={'url': webhook_url})
        result = response.json()

        if result.get('ok'):
            return jsonify({
                'message': 'Webhook set successfully',
                'webhook_url': webhook_url,
                'result': result
            }), 200
        else:
            return jsonify({
                'error': 'Failed to set webhook',
                'details': result
            }), 400

    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500


@telegram_webhook_bp.route('/webhook-info', methods=['GET'])
def get_webhook_info():
    """
    Get current webhook configuration from Telegram
    """
    try:
        bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
        if not bot_token:
            return jsonify({'error': 'Telegram bot token not configured'}), 500

        import requests
        telegram_api_url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"

        response = requests.get(telegram_api_url)
        result = response.json()

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({'error': str(e)}), 500
