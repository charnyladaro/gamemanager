"""
Telegram Notification Service for GameManager
Sends real-time payment notifications to admin via Telegram bot
"""

import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """Service class for sending Telegram notifications"""

    def __init__(self):
        self.bot_token = None
        self.chat_id = None
        self.api_url = None
        self._initialize()

    def _initialize(self):
        """Initialize the Telegram bot with credentials from config"""
        try:
            self.bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
            self.chat_id = current_app.config.get('TELEGRAM_ADMIN_CHAT_ID')

            if not self.bot_token or not self.chat_id:
                logger.warning("Telegram bot credentials not configured. Notifications disabled.")
                return

            # Set up Telegram API URL
            self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")
            self.bot_token = None

    def _send_message(self, message, inline_keyboard=None):
        """
        Internal method to send a message via Telegram

        Args:
            message (str): Message text to send
            inline_keyboard (list): Optional inline keyboard buttons

        Returns:
            bool: True if sent successfully, False otherwise
        """
        if not self.bot_token or not self.chat_id or not self.api_url:
            logger.warning("Telegram bot not initialized. Skipping notification.")
            return False

        try:
            # Use Telegram HTTP API directly (synchronous)
            url = f"{self.api_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }

            # Add inline keyboard if provided
            if inline_keyboard:
                payload['reply_markup'] = {
                    'inline_keyboard': inline_keyboard
                }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                logger.info("Telegram notification sent successfully")
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                print(f"Telegram API error: {error_msg}")
                logger.error(f"Telegram API error: {error_msg}")

                # Provide helpful error messages
                if "chat not found" in error_msg.lower():
                    logger.error("Hint: Make sure you have started a conversation with your bot and the chat_id is correct.")
                    logger.error(f"Current chat_id: {self.chat_id}")
                    logger.error("Run 'python get_telegram_chat_id.py' to find your correct chat_id")

                return False

        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            print(f"Failed to send Telegram notification: {error_msg}")
            logger.error(f"Failed to send Telegram notification: {error_msg}")
            return False
        except Exception as e:
            error_msg = str(e)
            print(f"Failed to send Telegram notification: {error_msg}")
            logger.error(f"Failed to send Telegram notification: {error_msg}")
            return False

    def send_new_payment_notification(self, payment_data):
        """
        Send notification when a new payment is received with action buttons

        Args:
            payment_data (dict): Payment information including:
                - id: Payment ID
                - game_title: Game name
                - amount: Payment amount
                - username: User who made payment
                - reference_number: GCash reference number
                - status: Payment status

        Returns:
            bool: True if sent successfully
        """
        try:
            reference = payment_data.get('reference_number', 'N/A')
            payment_id = payment_data.get('id', 'N/A')

            message = f"""
💳 <b>NEW PAYMENT FOR VERIFICATION</b>

🎮 <b>Game:</b> {payment_data.get('game_title', 'N/A')}
💰 <b>Amount:</b> ₱{payment_data.get('amount', 0):.2f}
👤 <b>User:</b> {payment_data.get('username', 'N/A')}
🆔 <b>Payment ID:</b> #{payment_id}
📱 <b>GCash Ref:</b> <code>{reference}</code>
📝 <b>Status:</b> Pending Verification

👇 <i>Click a button below to take action:</i>
"""

            # Create inline keyboard with verify and reject buttons
            inline_keyboard = [
                [
                    {
                        'text': '✅ Verify Payment',
                        'callback_data': f'verify_{payment_id}'
                    },
                    {
                        'text': '❌ Reject Payment',
                        'callback_data': f'reject_{payment_id}'
                    }
                ]
            ]

            return self._send_message(message.strip(), inline_keyboard=inline_keyboard)

        except Exception as e:
            logger.error(f"Error formatting new payment notification: {e}")
            return False

    def send_payment_approved_notification(self, payment_data):
        """
        Send confirmation when payment is approved

        Args:
            payment_data (dict): Payment information

        Returns:
            bool: True if sent successfully
        """
        try:
            message = f"""
✅ <b>PAYMENT APPROVED</b>

Payment <b>#{payment_data.get('id', 'N/A')}</b> has been approved.
Game added to <b>{payment_data.get('username', 'user')}</b>'s library.

🎮 <b>Game:</b> {payment_data.get('game_title', 'N/A')}
💰 <b>Amount:</b> ₱{payment_data.get('amount', 0):.2f}
"""
            return self._send_message(message.strip())

        except Exception as e:
            logger.error(f"Error formatting approval notification: {e}")
            return False

    def send_payment_rejected_notification(self, payment_data):
        """
        Send notification when payment is rejected

        Args:
            payment_data (dict): Payment information

        Returns:
            bool: True if sent successfully
        """
        try:
            message = f"""
❌ <b>PAYMENT REJECTED</b>

Payment <b>#{payment_data.get('id', 'N/A')}</b> has been rejected.

🎮 <b>Game:</b> {payment_data.get('game_title', 'N/A')}
💰 <b>Amount:</b> ₱{payment_data.get('amount', 0):.2f}
👤 <b>User:</b> {payment_data.get('username', 'N/A')}
"""
            return self._send_message(message.strip())

        except Exception as e:
            logger.error(f"Error formatting rejection notification: {e}")
            return False

    def edit_message(self, chat_id, message_id, new_text, inline_keyboard=None):
        """
        Edit an existing Telegram message

        Args:
            chat_id: The chat ID where the message was sent
            message_id: The message ID to edit
            new_text (str): New message text
            inline_keyboard (list): Optional new inline keyboard

        Returns:
            bool: True if edited successfully
        """
        if not self.bot_token or not self.api_url:
            logger.warning("Telegram bot not initialized. Cannot edit message.")
            return False

        try:
            url = f"{self.api_url}/editMessageText"
            payload = {
                'chat_id': chat_id,
                'message_id': message_id,
                'text': new_text,
                'parse_mode': 'HTML'
            }

            if inline_keyboard:
                payload['reply_markup'] = {
                    'inline_keyboard': inline_keyboard
                }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                logger.info("Telegram message edited successfully")
                return True
            else:
                error_msg = result.get('description', 'Unknown error')
                logger.error(f"Failed to edit Telegram message: {error_msg}")
                return False

        except Exception as e:
            logger.error(f"Error editing Telegram message: {e}")
            return False

    def answer_callback_query(self, callback_query_id, text, show_alert=False):
        """
        Answer a callback query from an inline button

        Args:
            callback_query_id: The callback query ID
            text (str): Text to show to user
            show_alert (bool): Show as alert instead of notification

        Returns:
            bool: True if answered successfully
        """
        if not self.bot_token or not self.api_url:
            logger.warning("Telegram bot not initialized. Cannot answer callback.")
            return False

        try:
            url = f"{self.api_url}/answerCallbackQuery"
            payload = {
                'callback_query_id': callback_query_id,
                'text': text,
                'show_alert': show_alert
            }

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()
            return result.get('ok', False)

        except Exception as e:
            logger.error(f"Error answering callback query: {e}")
            return False

    def test_connection(self):
        """
        Test the Telegram bot connection

        Returns:
            bool: True if connection is successful
        """
        try:
            test_message = "🤖 <b>GameManager Bot Test</b>\n\nTelegram notifications are working correctly!"
            return self._send_message(test_message)
        except Exception as e:
            logger.error(f"Telegram bot test failed: {e}")
            return False


# Singleton instance
_notifier_instance = None


def get_telegram_notifier():
    """
    Get or create the Telegram notifier singleton instance

    Returns:
        TelegramNotifier: The notifier instance
    """
    global _notifier_instance
    if _notifier_instance is None:
        _notifier_instance = TelegramNotifier()
    return _notifier_instance
