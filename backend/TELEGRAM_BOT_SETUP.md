# Telegram Bot Setup Guide - Payment Verification

This guide explains how to set up and use the Telegram bot with interactive buttons for verifying/rejecting payments directly from Telegram.

## Features

✅ **Interactive Buttons** - Verify or reject payments with a single click
✅ **Real-time Notifications** - Get instant alerts when users submit payments
✅ **Automatic Updates** - Payment status updates in database and user library
✅ **Message Editing** - Original notification updates to show action taken
✅ **Admin-only Access** - Only the configured admin can use action buttons

---

## Quick Start

### 1. Configure Environment Variables

Make sure your `.env` file has the following:

```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ADMIN_CHAT_ID=your_chat_id_here
```

To get these values:
- **Bot Token**: Create a bot with [@BotFather](https://t.me/botfather) on Telegram
- **Chat ID**: Run `python get_telegram_chat_id.py` to find your chat ID

### 2. Start the Polling Service

The polling service listens for button clicks from Telegram.

```bash
cd backend
python telegram_bot_polling.py
```

You should see:
```
🤖 Telegram Bot Polling Service Started
Listening for Telegram updates...
```

**Important**: Keep this running in a separate terminal while your Flask app is running.

### 3. Test the Integration

1. Start your Flask server: `python run.py`
2. Start the polling service: `python telegram_bot_polling.py`
3. Submit a test payment from your frontend
4. Check Telegram - you should receive a notification with buttons

---

## How It Works

### When a User Submits Payment:

1. User submits GCash reference number via frontend
2. Admin receives Telegram notification with:
   - Payment details (game, amount, user, reference number)
   - Two buttons: **✅ Verify Payment** | **❌ Reject Payment**

### When Admin Clicks a Button:

**Verify Payment:**
- Payment status → `completed`
- Game added to user's library
- Original message updates to show "PAYMENT VERIFIED"
- Success notification shown in Telegram

**Reject Payment:**
- Payment status → `failed`
- Original message updates to show "PAYMENT REJECTED"
- Rejection notification shown in Telegram

---

## Running in Production

### Option 1: Polling Service (Recommended for Simple Setup)

Run the polling service as a background process:

```bash
# Using screen or tmux
screen -S telegram-bot
python telegram_bot_polling.py

# Or using nohup
nohup python telegram_bot_polling.py > telegram_bot.log 2>&1 &
```

### Option 2: Webhook (Recommended for Production)

For production with a public domain, use webhooks instead of polling:

1. Set your webhook URL:

```bash
curl -X POST http://localhost:5000/api/telegram/set-webhook \
  -H "Content-Type: application/json" \
  -d '{"url": "https://yourdomain.com/api/telegram/webhook"}'
```

2. Verify webhook is set:

```bash
curl http://localhost:5000/api/telegram/webhook-info
```

**Note**: Webhooks require:
- HTTPS (SSL certificate)
- Public domain/IP
- Port 443, 80, 88, or 8443

---

## Troubleshooting

### Bot Not Receiving Updates

1. **Check Bot Token**:
   ```bash
   # Verify token is valid
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   ```

2. **Check Chat ID**:
   ```bash
   # Run this to find your chat ID
   python get_telegram_chat_id.py
   ```

3. **Ensure Polling Service is Running**:
   ```bash
   # You should see this in the terminal
   🤖 Telegram Bot Polling Service Started
   Listening for Telegram updates...
   ```

### Buttons Not Working

1. **Verify Admin Chat ID** - Only the configured admin can use buttons
2. **Check Logs** - Look for errors in the polling service terminal
3. **Payment Status** - Buttons only work for payments with status `pending_verification`

### Message: "Unauthorized. Only admin can perform this action"

This means the chat ID clicking the button doesn't match `TELEGRAM_ADMIN_CHAT_ID` in your `.env` file.

Run `python get_telegram_chat_id.py` and update your `.env` with the correct chat ID.

---

## API Endpoints

### Webhook Endpoint
```
POST /api/telegram/webhook
```
Receives updates from Telegram (used with webhook mode)

### Set Webhook
```
POST /api/telegram/set-webhook
Body: {"url": "https://yourdomain.com/api/telegram/webhook"}
```
Configures Telegram to send updates to your server

### Get Webhook Info
```
GET /api/telegram/webhook-info
```
Returns current webhook configuration

---

## Security Notes

- Only the configured `TELEGRAM_ADMIN_CHAT_ID` can use action buttons
- Webhook endpoint validates it's coming from admin chat
- All payment actions are logged
- Database transactions are rolled back on errors

---

## Example Workflow

```
1. User submits payment with reference: 1234567890
   ↓
2. Admin receives Telegram message:

   💳 NEW PAYMENT FOR VERIFICATION

   🎮 Game: Grand Theft Auto V
   💰 Amount: ₱500.00
   👤 User: john_doe
   🆔 Payment ID: #42
   📱 GCash Ref: 1234567890
   📝 Status: Pending Verification

   👇 Click a button below to take action:

   [✅ Verify Payment] [❌ Reject Payment]

3. Admin clicks "✅ Verify Payment"
   ↓
4. Message updates instantly:

   ✅ PAYMENT VERIFIED

   🎮 Game: Grand Theft Auto V
   💰 Amount: ₱500.00
   👤 User: john_doe
   🆔 Payment ID: #42
   📱 GCash Ref: 1234567890
   ✅ Status: Completed

   Game has been added to user's library

5. User can now see the game in their library
```

---

## Development vs Production

| Feature | Development (Polling) | Production (Webhook) |
|---------|----------------------|---------------------|
| Setup Difficulty | Easy | Moderate |
| Requires Public URL | No | Yes |
| Requires SSL | No | Yes |
| Scalability | Low | High |
| Latency | ~1 second | Instant |
| Server Load | Higher | Lower |

**Recommendation**: Use polling for local development and testing. Use webhooks for production deployment.

---

## Questions?

If you encounter issues:
1. Check the logs in `telegram_bot_polling.py` terminal
2. Verify your `.env` configuration
3. Run `python get_telegram_chat_id.py` to confirm chat ID
4. Test the bot connection via Admin Dashboard

Enjoy automated payment verification! 🎉
