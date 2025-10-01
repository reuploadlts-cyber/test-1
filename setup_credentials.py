#!/usr/bin/env python3
"""Setup script for configuring IVASMS credentials."""

import os
import sys
from pathlib import Path

def setup_credentials():
    """Interactive setup for IVASMS credentials."""
    print("🔐 IVASMS Credentials Setup")
    print("=" * 40)
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file found")
        overwrite = input("Do you want to update existing credentials? (y/N): ").lower()
        if overwrite != 'y':
            print("Setup cancelled.")
            return
    else:
        print("📝 Creating new .env file...")
    
    # Get credentials from user
    print("\nPlease enter your IVASMS credentials:")
    
    telegram_token = input("Telegram Bot Token: ").strip()
    if not telegram_token:
        print("❌ Telegram token is required!")
        return
    
    admin_ids = input("Admin Telegram User IDs (comma-separated): ").strip()
    if not admin_ids:
        print("❌ Admin IDs are required!")
        return
    
    ivasms_email = input("IVASMS Email: ").strip()
    if not ivasms_email:
        print("❌ IVASMS email is required!")
        return
    
    ivasms_password = input("IVASMS Password: ").strip()
    if not ivasms_password:
        print("❌ IVASMS password is required!")
        return
    
    # Optional settings
    poll_interval = input("Poll Interval (seconds, default 8): ").strip() or "8"
    headless = input("Run in headless mode? (Y/n): ").strip().lower()
    headless = "true" if headless != "n" else "false"
    
    # Create .env file
    env_content = f"""# Telegram Bot Configuration
TELEGRAM_TOKEN={telegram_token}
ADMIN_IDS={admin_ids}

# IVASMS.com Credentials
IVASMS_EMAIL={ivasms_email}
IVASMS_PASSWORD={ivasms_password}

# Bot Configuration
POLL_INTERVAL={poll_interval}
HEADLESS={headless}
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=sqlite:///bot_data.db
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        
        print("\n✅ Credentials saved to .env file!")
        print("\n📋 Next steps:")
        print("1. Test the bot: python test_imports.py")
        print("2. Run the bot: python run.py")
        print("3. Test in Telegram: Send /start to your bot")
        
    except Exception as e:
        print(f"❌ Error saving credentials: {e}")

def test_login():
    """Test the login functionality."""
    print("\n🧪 Testing IVASMS Login...")
    print("This will attempt to login to IVASMS.com with your credentials.")
    print("Note: This will open a browser window for testing.")
    
    confirm = input("Continue? (y/N): ").lower()
    if confirm != 'y':
        print("Login test cancelled.")
        return
    
    try:
        # Import and test
        from src.config import Config
        from src.storage import Storage
        from src.monitor import IVASMSMonitor
        import asyncio
        
        # Load config
        config = Config()
        storage = Storage()
        await storage.initialize()
        
        # Create monitor
        monitor = IVASMSMonitor(storage, config)
        
        # Test login
        print("Attempting login...")
        success = await monitor.start()
        
        if success:
            print("✅ Login successful!")
            await monitor.cleanup()
        else:
            print("❌ Login failed. Check the logs for details.")
            await monitor.cleanup()
            
    except Exception as e:
        print(f"❌ Error during login test: {e}")

if __name__ == "__main__":
    print("🚀 OTP Forwarder Bot Setup")
    print("=" * 30)
    
    while True:
        print("\nChoose an option:")
        print("1. Setup credentials")
        print("2. Test login")
        print("3. Exit")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == "1":
            setup_credentials()
        elif choice == "2":
            test_login()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
