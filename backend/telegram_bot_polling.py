"""
Telegram Bot Polling Service
This script runs a polling service to receive Telegram updates
Use this for local development or when webhooks are not available
"""

import os
import sys
import time
import requests
import logging
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.routes.telegram_webhook import handle_callback_query, handle_message

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramBotPoller:
    """Polls Telegram for updates and processes them"""

    def __init__(self, bot_token):
        self.bot_token = bot_token
        self.api_url = f"https://api.telegram.org/bot{bot_token}"
        self.offset = 0
        self.app = create_app()

    def get_updates(self, timeout=30):
        """
        Get updates from Telegram using long polling

        Args:
            timeout: Long polling timeout in seconds

        Returns:
            List of updates
        """
        try:
            url = f"{self.api_url}/getUpdates"
            params = {
                'offset': self.offset,
                'timeout': timeout,
                'allowed_updates': ['message', 'callback_query']
            }

            response = requests.get(url, params=params, timeout=timeout + 5)
            response.raise_for_status()

            result = response.json()
            if result.get('ok'):
                return result.get('result', [])
            else:
                logger.error(f"Failed to get updates: {result}")
                return []

        except requests.exceptions.Timeout:
            # This is normal for long polling
            return []
        except Exception as e:
            logger.error(f"Error getting updates: {e}")
            return []

    def process_update(self, update):
        """
        Process a single update

        Args:
            update: Update object from Telegram
        """
        try:
            # Update offset to mark this update as processed
            self.offset = update['update_id'] + 1

            with self.app.app_context():
                # Handle callback queries (button clicks)
                if 'callback_query' in update:
                    logger.info(f"Processing callback query: {update['callback_query'].get('data')}")
                    handle_callback_query(update['callback_query'])

                # Handle regular messages
                elif 'message' in update:
                    logger.info(f"Processing message: {update['message'].get('text', '')}")
                    handle_message(update['message'])

        except Exception as e:
            logger.error(f"Error processing update {update.get('update_id')}: {e}")

    def start_polling(self):
        """
        Start the polling loop
        """
        logger.info("=" * 60)
        logger.info("🤖 Telegram Bot Polling Service Started")
        logger.info("=" * 60)
        logger.info("Listening for Telegram updates...")
        logger.info("Press Ctrl+C to stop")
        logger.info("")

        try:
            while True:
                # Get updates from Telegram
                updates = self.get_updates()

                # Process each update
                for update in updates:
                    self.process_update(update)

                # Small delay to prevent CPU overuse
                if not updates:
                    time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\n")
            logger.info("=" * 60)
            logger.info("🛑 Stopping Telegram Bot Polling Service...")
            logger.info("=" * 60)
        except Exception as e:
            logger.error(f"Fatal error in polling loop: {e}")


def main():
    """Main entry point"""
    # Get bot token from environment
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')

    if not bot_token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
        print("\nPlease add your bot token to the .env file:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        sys.exit(1)

    # Check admin chat ID is configured
    admin_chat_id = os.environ.get('TELEGRAM_ADMIN_CHAT_ID')
    if not admin_chat_id:
        print("⚠️  WARNING: TELEGRAM_ADMIN_CHAT_ID not found in .env file")
        print("Button actions will not work until you configure the admin chat ID")
        print("\nRun 'python get_telegram_chat_id.py' to get your chat ID")
        print("")

    # Create and start the poller
    poller = TelegramBotPoller(bot_token)
    poller.start_polling()


if __name__ == '__main__':
    main()
