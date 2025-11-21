"""
Utility script to get your Telegram chat ID for bot notifications.

Instructions:
1. Open Telegram and find your bot (search for the bot name)
2. Send ANY message to the bot (like "Hi" or "/start")
3. Run this script: python get_telegram_chat_id.py
4. Copy the chat_id shown and update it in your .env file
"""

import os
import sys
import asyncio
from dotenv import load_dotenv
from telegram import Bot

# Fix encoding issues on Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

async def get_chat_ids():
    """Fetch recent updates from the bot to find chat IDs"""

    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')

    if not bot_token:
        print("❌ ERROR: TELEGRAM_BOT_TOKEN not found in .env file")
        print("\nPlease add your bot token to the .env file:")
        print("TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return

    try:
        bot = Bot(token=bot_token)

        print("🤖 Fetching updates from Telegram bot...")
        print("-" * 60)

        # Get bot info
        bot_info = await bot.get_me()
        print(f"✓ Connected to bot: @{bot_info.username}")
        print()

        # Get recent updates
        updates = await bot.get_updates()

        if not updates:
            print("⚠️  No messages found!")
            print()
            print("To get your chat ID:")
            print(f"1. Open Telegram and search for @{bot_info.username}")
            print("2. Start a conversation and send ANY message (e.g., 'Hi' or '/start')")
            print("3. Run this script again")
            return

        # Extract unique chat IDs from updates
        chat_ids = {}
        for update in updates:
            if update.message:
                chat_id = update.message.chat.id
                chat_type = update.message.chat.type
                chat_name = (
                    update.message.chat.username or
                    update.message.chat.first_name or
                    update.message.chat.title or
                    "Unknown"
                )

                chat_ids[chat_id] = {
                    'type': chat_type,
                    'name': chat_name
                }

        if not chat_ids:
            print("⚠️  No chat messages found in recent updates")
            return

        print("✓ Found the following chats:")
        print()

        for chat_id, info in chat_ids.items():
            print(f"  Chat ID: {chat_id}")
            print(f"  Type:    {info['type']}")
            print(f"  Name:    {info['name']}")
            print()

        print("-" * 60)
        print("\n📝 To enable Telegram notifications:")
        print("\n1. Copy your chat ID from above")
        print("2. Update your .env file with:")
        print(f"\n   TELEGRAM_ADMIN_CHAT_ID=your_chat_id_here")
        print("\n3. Restart your Flask server")

        # Test sending a message to each chat
        print("\n" + "-" * 60)
        print("🧪 Testing message delivery to each chat...\n")

        for chat_id in chat_ids.keys():
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text="✅ <b>Test Successful!</b>\n\nYour GameManager bot is configured correctly!",
                    parse_mode='HTML'
                )
                print(f"✓ Successfully sent test message to chat {chat_id}")
            except Exception as e:
                print(f"✗ Failed to send message to chat {chat_id}: {e}")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        print("\nPlease check:")
        print("1. Your TELEGRAM_BOT_TOKEN is correct")
        print("2. You have internet connection")
        print("3. The bot token is valid and not revoked")

if __name__ == '__main__':
    asyncio.run(get_chat_ids())
