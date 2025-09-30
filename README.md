# OTP Forwarder Bot for IVASMS

A Telegram bot that automatically monitors IVASMS.com for new OTP SMS messages and forwards them to admin Telegram chats.

## Features

- 🔐 **Automatic Login**: Logs into IVASMS.com with stored credentials
- 📱 **SMS Monitoring**: Continuously watches for new OTP messages
- 📨 **Telegram Integration**: Forwards new messages to admin chats
- 📊 **History Fetching**: Retrieve historical SMS messages by date range
- 🛡️ **Admin Controls**: Secure admin-only commands for bot management
- 🔄 **Auto-restart**: Handles failures and restarts automatically
- 📝 **Comprehensive Logging**: Detailed logs for debugging and monitoring
- 🐳 **Docker Support**: Ready for GitHub Codespaces and containerized deployment

## Quick Start

### Prerequisites

- Python 3.11+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- IVASMS.com account credentials

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# TELEGRAM_TOKEN=your_telegram_bot_token_here
# ADMIN_IDS=123456789,987654321
# IVASMS_EMAIL=your_email@domain.com
# IVASMS_PASSWORD=your_password_here
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
playwright install --with-deps
```

### 3. Run the Bot

```bash
python run.py
```

## GitHub Codespaces

1. Fork this repository
2. Open in Codespaces
3. Add secrets: `TELEGRAM_TOKEN`, `IVASMS_EMAIL`, `IVASMS_PASSWORD`
4. Run: `python run.py`

## Docker

```bash
# Build and run
docker build -t otp-forwarder-bot .
docker run -d --name otp-bot --env-file .env otp-forwarder-bot
```

## Telegram Commands

- `/start` - Show bot status
- `/status` - Detailed status (admin)
- `/recent [n]` - Show last n SMS messages (admin)
- `/history <start> <end>` - Get SMS history (admin)
- `/help` - Show all commands

## Configuration

The bot uses `config.yaml` for non-sensitive configuration and `.env` for credentials.

## Testing

```bash
pytest tests/
```

## License

MIT License - see LICENSE file for details.

## Disclaimer

This bot is for educational and personal use only. Ensure you have permission to scrape the target website and comply with their terms of service.
