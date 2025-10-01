"""Logging setup for the OTP Forwarder Bot."""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging(log_level: str = None, log_file: str = "logs/bot.log"):
    """Set up logging configuration."""
    # Create logs directory if it doesn't exist
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Get log level from environment or use default
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level, logging.INFO))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Set specific logger levels
    logging.getLogger('asyncio').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('playwright').setLevel(logging.WARNING)
    
    logger.info(f"Logging initialized with level: {log_level}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)
