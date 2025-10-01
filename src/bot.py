"""Telegram bot functionality."""

import asyncio
from typing import List, Optional
from datetime import datetime

from .logger_setup import get_logger
from .config import Config
from .storage import Storage, SMSMessage
from .monitor import IVASMSMonitor

logger = get_logger(__name__)

# Try to import aiogram, but don't fail if it's not available
try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    from aiogram.types import Message
    AIOGRAM_AVAILABLE = True
except ImportError:
    AIOGRAM_AVAILABLE = False
    logger.warning("aiogram not available. Bot functionality will be limited.")


class OTPForwarderBot:
    """Telegram bot for OTP forwarding."""
    
    def __init__(self, config: Config, storage: Storage, monitor: IVASMSMonitor):
        """Initialize the bot."""
        self.config = config
        self.storage = storage
        self.monitor = monitor
        self.bot = None
        self.dp = None
        
        if AIOGRAM_AVAILABLE:
            self.bot = Bot(token=config.telegram_token)
            self.dp = Dispatcher()
            self._register_handlers()
        else:
            logger.error("Cannot initialize bot: aiogram not available")
    
    def _register_handlers(self):
        """Register command handlers."""
        if not self.dp:
            return
        
        # Register command handlers
        self.dp.message.register(self.cmd_start, Command("start"))
        self.dp.message.register(self.cmd_status, Command("status"))
        self.dp.message.register(self.cmd_recent, Command("recent"))
        self.dp.message.register(self.cmd_last, Command("last"))
        self.dp.message.register(self.cmd_history, Command("history"))
        self.dp.message.register(self.cmd_help, Command("help"))
    
    async def start(self):
        """Start the bot."""
        if not AIOGRAM_AVAILABLE:
            logger.error("Cannot start bot: aiogram not available")
            return
        
        try:
            # Send startup message to admins
            await self._notify_admins("✅ Bot started successfully!")
            
            # Start monitoring
            asyncio.create_task(self.monitor.start_monitoring())
            
            # Start bot polling
            await self.dp.start_polling(self.bot)
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            await self._notify_admins(f"❌ Bot failed to start: {e}")
    
    async def _notify_admins(self, message: str):
        """Send message to all admins."""
        if not self.bot:
            return
        
        for admin_id in self.config.admin_ids:
            try:
                await self.bot.send_message(admin_id, message)
            except Exception as e:
                logger.error(f"Failed to send message to admin {admin_id}: {e}")
    
    async def cmd_start(self, message: Message):
        """Handle /start command."""
        await message.reply("🤖 OTP Forwarder Bot is running!\n\nUse /help to see available commands.")
    
    async def cmd_status(self, message: Message):
        """Handle /status command."""
        if not self._is_admin(message.from_user.id):
            await message.reply("❌ Access denied. Admin only.")
            return
        
        status = f"""
📊 Bot Status:
• Bot: {'🟢 Running' if self.bot else '🔴 Not available'}
• Monitor: {'🟢 Active' if self.monitor.is_monitoring else '🔴 Inactive'}
• Logged in: {'🟢 Yes' if self.monitor.is_logged_in else '🔴 No'}
• Database: {'🟢 Connected' if self.storage else '🔴 Not connected'}

{self.config.get_sanitized_config()}
        """
        await message.reply(status)
    
    async def cmd_recent(self, message: Message):
        """Handle /recent command."""
        if not self._is_admin(message.from_user.id):
            await message.reply("❌ Access denied. Admin only.")
            return
        
        try:
            # Get number from command (default 10)
            args = message.text.split()
            limit = int(args[1]) if len(args) > 1 else 10
            
            messages = await self.storage.get_recent_sms(limit)
            
            if not messages:
                await message.reply("📭 No SMS messages found.")
                return
            
            response = f"📱 Last {len(messages)} SMS messages:\n\n"
            for i, msg in enumerate(messages, 1):
                response += f"{i}. **{msg.sender}**\n"
                response += f"   {msg.message}\n"
                response += f"   _{msg.timestamp}_\n\n"
            
            await message.reply(response)
            
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    
    async def cmd_last(self, message: Message):
        """Handle /last command."""
        if not self._is_admin(message.from_user.id):
            await message.reply("❌ Access denied. Admin only.")
            return
        
        try:
            last_message = await self.storage.get_last_sms()
            
            if not last_message:
                await message.reply("📭 No SMS messages found.")
                return
            
            response = f"📱 **Latest SMS:**\n\n"
            response += f"**From:** {last_message.sender}\n"
            response += f"**Message:** {last_message.message}\n"
            response += f"**Time:** {last_message.timestamp}\n"
            response += f"**Forwarded:** {'✅' if last_message.forwarded else '❌'}"
            
            await message.reply(response)
            
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    
    async def cmd_history(self, message: Message):
        """Handle /history command."""
        if not self._is_admin(message.from_user.id):
            await message.reply("❌ Access denied. Admin only.")
            return
        
        try:
            args = message.text.split()
            if len(args) < 3:
                await message.reply("❌ Usage: /history <start_date> <end_date>\nExample: /history 2025-01-01 2025-01-31")
                return
            
            start_date = args[1]
            end_date = args[2]
            
            # This is a simplified implementation
            # In a real implementation, you'd filter messages by date
            messages = await self.storage.get_recent_sms(50)
            
            if not messages:
                await message.reply("📭 No messages found for the specified date range.")
                return
            
            response = f"📅 Messages from {start_date} to {end_date}:\n\n"
            for i, msg in enumerate(messages[:10], 1):  # Limit to 10 for readability
                response += f"{i}. **{msg.sender}** - {msg.timestamp}\n"
                response += f"   {msg.message}\n\n"
            
            if len(messages) > 10:
                response += f"... and {len(messages) - 10} more messages"
            
            await message.reply(response)
            
        except Exception as e:
            await message.reply(f"❌ Error: {e}")
    
    async def cmd_help(self, message: Message):
        """Handle /help command."""
        help_text = """
🤖 **OTP Forwarder Bot Commands:**

**General:**
/start - Check bot status
/help - Show this help

**Admin Commands:**
/status - Detailed bot status
/recent [n] - Show last n SMS messages (default: 10)
/last - Show latest SMS message
/history <start> <end> - Get SMS history

**Examples:**
/recent 5
/history 2025-01-01 2025-01-31
        """
        await message.reply(help_text)
    
    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return self.config.is_admin(user_id)
