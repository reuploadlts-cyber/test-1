"""IVASMS monitoring functionality."""

import asyncio
import time
from typing import List, Optional
from datetime import datetime

from .logger_setup import get_logger
from .storage import Storage, SMSMessage

logger = get_logger(__name__)

# Try to import playwright, but don't fail if it's not available
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logger.warning("Playwright not available. Monitor functionality will be limited.")


class IVASMSMonitor:
    """Monitor for IVASMS.com OTP messages."""
    
    def __init__(self, storage: Storage):
        """Initialize the monitor."""
        self.storage = storage
        self.browser = None
        self.context = None
        self.page = None
        self.is_logged_in = False
        self.is_monitoring = False
        
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not available. Cannot start monitor.")
    
    async def start(self) -> bool:
        """Start the monitor and login to IVASMS."""
        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Cannot start monitor: Playwright not available")
            return False
        
        try:
            # Initialize Playwright
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            # Set timeout
            self.page.set_default_timeout(30000)
            
            # Login to IVASMS
            if await self._login():
                self.is_logged_in = True
                logger.info("Successfully logged in to IVASMS")
                return True
            else:
                logger.error("Failed to login to IVASMS")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start monitor: {e}")
            return False
    
    async def _login(self) -> bool:
        """Login to IVASMS.com."""
        try:
            # Navigate to login page
            await self.page.goto("https://www.ivasms.com/login")
            
            # Fill login form (simplified - you'll need to implement actual selectors)
            await self.page.fill('input[name="email"]', "your_email@domain.com")
            await self.page.fill('input[name="password"]', "your_password")
            
            # Click login button
            await self.page.click('button[type="submit"]')
            
            # Wait for navigation
            await self.page.wait_for_load_state('networkidle')
            
            # Handle popup if present
            await self._handle_popup()
            
            # Navigate to SMS statistics
            await self.page.goto("https://www.ivasms.com/portal/sms/received")
            
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    async def _handle_popup(self) -> bool:
        """Handle login popup."""
        try:
            # Look for popup elements
            popup_selectors = [
                'button:has-text("Next")',
                'button:has-text("Done")',
                '.popup button',
                '.modal button'
            ]
            
            for selector in popup_selectors:
                try:
                    element = self.page.locator(selector)
                    if await element.count() > 0:
                        await element.click()
                        await asyncio.sleep(1)
                except:
                    continue
            
            return True
            
        except Exception as e:
            logger.warning(f"Popup handling failed: {e}")
            return True  # Continue anyway
    
    async def start_monitoring(self) -> None:
        """Start monitoring for new SMS messages."""
        if not self.is_logged_in:
            logger.error("Cannot start monitoring: Not logged in")
            return
        
        self.is_monitoring = True
        logger.info("Started monitoring for new SMS messages")
        
        while self.is_monitoring:
            try:
                # Scrape current messages
                messages = await self._scrape_messages()
                
                # Process new messages
                for message in messages:
                    await self._process_message(message)
                
                # Wait before next check
                await asyncio.sleep(8)  # Poll every 8 seconds
                
            except Exception as e:
                logger.error(f"Error during monitoring: {e}")
                await asyncio.sleep(5)  # Wait before retry
    
    async def _scrape_messages(self) -> List[SMSMessage]:
        """Scrape SMS messages from the page."""
        try:
            # Wait for message list to load
            await self.page.wait_for_selector('.message-list, table tbody', timeout=10000)
            
            # Get message rows
            rows = await self.page.locator('tr.sms-row, .sms-item').all()
            
            messages = []
            for row in rows:
                try:
                    # Extract message data (simplified)
                    sender = await row.locator('.sender, .phone').text_content() or "Unknown"
                    message = await row.locator('.body, .message').text_content() or ""
                    timestamp = await row.locator('.time, .date').text_content() or ""
                    
                    # Create message ID from content
                    message_id = f"{sender}_{timestamp}_{hash(message)}"
                    
                    sms = SMSMessage(
                        id=message_id,
                        sender=sender,
                        message=message,
                        timestamp=timestamp,
                        received_at=datetime.now().isoformat()
                    )
                    
                    messages.append(sms)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse message row: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            logger.error(f"Failed to scrape messages: {e}")
            return []
    
    async def _process_message(self, message: SMSMessage) -> None:
        """Process a new SMS message."""
        try:
            # Check if message already exists
            existing = await self.storage.get_last_sms()
            if existing and existing.id == message.id:
                return  # Already processed
            
            # Save message
            await self.storage.save_sms(message)
            logger.info(f"New SMS received: {message.sender} - {message.message[:50]}...")
            
        except Exception as e:
            logger.error(f"Failed to process message: {e}")
    
    async def stop_monitoring(self) -> None:
        """Stop monitoring."""
        self.is_monitoring = False
        logger.info("Stopped monitoring")
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        try:
            if self.is_monitoring:
                await self.stop_monitoring()
            
            if self.context:
                await self.context.close()
            
            if self.browser:
                await self.browser.close()
            
            logger.info("Monitor cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
