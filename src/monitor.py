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
    
    def __init__(self, storage: Storage, config=None):
        """Initialize the monitor."""
        self.storage = storage
        self.config = config
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
            # Use the passed config
            if not self.config:
                logger.error("No config provided to monitor")
                return False
            
            logger.info("Navigating to IVASMS login page...")
            await self.page.goto("https://www.ivasms.com/login")
            
            # Wait for page to load
            await self.page.wait_for_load_state('domcontentloaded')
            
            # Try multiple possible selectors for email field
            email_selectors = [
                'input[name="email"]',
                'input[type="email"]',
                'input[id="email"]',
                'input[placeholder*="email" i]',
                'input[placeholder*="Email" i]'
            ]
            
            email_filled = False
            for selector in email_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.fill(selector, config.ivasms_email)
                        logger.info(f"Email filled using selector: {selector}")
                        email_filled = True
                        break
                except Exception as e:
                    logger.debug(f"Email selector {selector} failed: {e}")
                    continue
            
            if not email_filled:
                logger.error("Could not find email input field")
                return False
            
            # Try multiple possible selectors for password field
            password_selectors = [
                'input[name="password"]',
                'input[type="password"]',
                'input[id="password"]',
                'input[placeholder*="password" i]',
                'input[placeholder*="Password" i]'
            ]
            
            password_filled = False
            for selector in password_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.fill(selector, config.ivasms_password)
                        logger.info(f"Password filled using selector: {selector}")
                        password_filled = True
                        break
                except Exception as e:
                    logger.debug(f"Password selector {selector} failed: {e}")
                    continue
            
            if not password_filled:
                logger.error("Could not find password input field")
                return False
            
            # Try multiple possible selectors for login button
            login_button_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Login")',
                'button:has-text("Log in")',
                'button:has-text("Sign in")',
                '.login-button',
                '#login-button',
                'button[class*="login"]',
                'button[class*="submit"]'
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                try:
                    if await self.page.locator(selector).count() > 0:
                        await self.page.click(selector)
                        logger.info(f"Login button clicked using selector: {selector}")
                        login_clicked = True
                        break
                except Exception as e:
                    logger.debug(f"Login button selector {selector} failed: {e}")
                    continue
            
            if not login_clicked:
                logger.error("Could not find login button")
                return False
            
            # Wait for navigation or response
            logger.info("Waiting for login response...")
            try:
                # Wait for either navigation or error message
                await self.page.wait_for_load_state('networkidle', timeout=10000)
            except Exception as e:
                logger.warning(f"Navigation timeout: {e}")
            
            # Check if login was successful by looking for indicators
            current_url = self.page.url
            logger.info(f"Current URL after login: {current_url}")
            
            # Check for common success indicators
            success_indicators = [
                'dashboard',
                'portal',
                'account',
                'profile',
                'home'
            ]
            
            login_successful = any(indicator in current_url.lower() for indicator in success_indicators)
            
            if not login_successful:
                # Check for error messages
                error_selectors = [
                    '.error',
                    '.alert-danger',
                    '.login-error',
                    '[class*="error"]',
                    '[class*="alert"]'
                ]
                
                for selector in error_selectors:
                    try:
                        error_element = self.page.locator(selector)
                        if await error_element.count() > 0:
                            error_text = await error_element.text_content()
                            logger.error(f"Login error detected: {error_text}")
                            return False
                    except:
                        continue
                
                # Take a screenshot for debugging
                try:
                    await self.page.screenshot(path="login_debug.png")
                    logger.info("Screenshot saved as login_debug.png for debugging")
                except:
                    pass
                
                logger.error("Login failed - no success indicators found")
                return False
            
            # Handle popup if present
            await self._handle_popup()
            
            # Navigate to SMS statistics
            logger.info("Navigating to SMS statistics page...")
            await self.page.goto("https://www.ivasms.com/portal/sms/received")
            await self.page.wait_for_load_state('domcontentloaded')
            
            logger.info("Successfully logged in to IVASMS")
            return True
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            # Take a screenshot for debugging
            try:
                await self.page.screenshot(path="login_error.png")
                logger.info("Error screenshot saved as login_error.png")
            except:
                pass
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
