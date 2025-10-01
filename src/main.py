#!/usr/bin/env python3
"""Main entry point for the OTP Forwarder Bot."""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now use absolute imports
from src.logger_setup import setup_logging, get_logger
from src.config import Config
from src.storage import Storage
from src.monitor import IVASMSMonitor
from src.bot import OTPForwarderBot

logger = get_logger(__name__)


async def main():
    """Main application entry point."""
    try:
        # Setup logging
        setup_logging()
        logger.info("Starting OTP Forwarder Bot...")
        
        # Load configuration
        config = Config()
        logger.info(f"Configuration loaded successfully")
        
        # Initialize storage
        storage = Storage()
        await storage.initialize()
        logger.info("Storage initialized successfully")
        
        # Initialize monitor
        monitor = IVASMSMonitor(storage)
        logger.info("Monitor initialized successfully")
        
        # Initialize bot
        bot = OTPForwarderBot(config, storage, monitor)
        logger.info("Bot initialized successfully")
        
        # Start the bot
        await bot.start()
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        if 'monitor' in locals():
            await monitor.cleanup()
        if 'storage' in locals():
            await storage.close()
        logger.info("Bot shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
