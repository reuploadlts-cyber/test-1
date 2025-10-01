#!/usr/bin/env python3
"""Startup script for the OTP Forwarder Bot."""

import sys
import os
from pathlib import Path

def setup_environment():
    """Set up the environment for running the bot."""
    # Add the project root to Python path
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    # Set up environment variables if not already set
    if not os.getenv('TELEGRAM_TOKEN'):
        print("⚠️  TELEGRAM_TOKEN not set. Please set it in your environment or .env file")
        return False
    
    if not os.getenv('ADMIN_IDS'):
        print("⚠️  ADMIN_IDS not set. Please set it in your environment or .env file")
        return False
    
    if not os.getenv('IVASMS_EMAIL'):
        print("⚠️  IVASMS_EMAIL not set. Please set it in your environment or .env file")
        return False
    
    if not os.getenv('IVASMS_PASSWORD'):
        print("⚠️  IVASMS_PASSWORD not set. Please set it in your environment or .env file")
        return False
    
    return True

def main():
    """Main startup function."""
    print("🚀 Starting OTP Forwarder Bot...")
    
    # Setup environment
    if not setup_environment():
        print("❌ Environment setup failed. Please check your configuration.")
        sys.exit(1)
    
    # Test imports
    try:
        from src.main import main as bot_main
        import asyncio
        
        print("✅ All imports successful")
        print("🤖 Starting bot...")
        
        # Run the bot
        asyncio.run(bot_main())
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please make sure all dependencies are installed:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
