"""Configuration management for the OTP Forwarder Bot."""

import os
import yaml
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration manager for the bot."""
    
    def __init__(self):
        """Initialize configuration."""
        self._load_config_file()
        self._load_env_vars()
    
    def _load_config_file(self):
        """Load configuration from config.yaml."""
        try:
            with open('config.yaml', 'r') as f:
                self.config = yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError("config.yaml not found. Please create it from config.yaml.example")
    
    def _load_env_vars(self):
        """Load sensitive configuration from environment variables."""
        self.telegram_token = os.getenv('TELEGRAM_TOKEN')
        if not self.telegram_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")
        
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        self.admin_ids = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
        if not self.admin_ids:
            raise ValueError("At least one ADMIN_ID is required")
        
        self.ivasms_email = os.getenv('IVASMS_EMAIL')
        self.ivasms_password = os.getenv('IVASMS_PASSWORD')
        if not self.ivasms_email or not self.ivasms_password:
            raise ValueError("IVASMS_EMAIL and IVASMS_PASSWORD are required")
        
        self.poll_interval = int(os.getenv('POLL_INTERVAL', '8'))
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def site_config(self) -> Dict[str, str]:
        """Get site configuration."""
        return self.config.get('site', {})
    
    @property
    def playwright_config(self) -> Dict[str, Any]:
        """Get Playwright configuration."""
        return self.config.get('playwright', {})
    
    @property
    def telegram_config(self) -> Dict[str, Any]:
        """Get Telegram configuration."""
        return self.config.get('telegram', {})
    
    @property
    def selectors(self) -> Dict[str, Any]:
        """Get CSS selectors configuration."""
        return self.config.get('selectors', {})
    
    @property
    def storage_config(self) -> Dict[str, Any]:
        """Get storage configuration."""
        return self.config.get('storage', {})
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in self.admin_ids
    
    def get_sanitized_config(self) -> str:
        """Get configuration without sensitive data."""
        return f"""
Bot Configuration:
- ADMIN_IDS: {self.admin_ids}
- POLL_INTERVAL: {self.poll_interval}s
- HEADLESS: {self.headless}
- LOG_LEVEL: {self.log_level}
- SITE_URL: {self.site_config.get('base_url', 'Not configured')}
- PLAYWRIGHT_TIMEOUT: {self.playwright_config.get('timeout_ms', 'Not configured')}ms
- PLAYWRIGHT_RETRIES: {self.playwright_config.get('retries', 'Not configured')}
"""
