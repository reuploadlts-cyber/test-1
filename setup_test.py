#!/usr/bin/env python3
"""Setup script for testing the OTP Forwarder Bot."""

import os
import sys
import subprocess
from pathlib import Path

def setup_test_environment():
    """Set up test environment."""
    
    print("Setting up test environment...")
    
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Create .env file for testing
    env_content = """# Test Environment Variables
TELEGRAM_TOKEN=test_token
ADMIN_IDS=123456789
IVASMS_EMAIL=test@example.com
IVASMS_PASSWORD=test_password
POLL_INTERVAL=8
HEADLESS=true
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///test_bot_data.db
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env file for testing")
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencies installed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    
    # Run basic tests
    print("Running basic tests...")
    try:
        result = subprocess.run([sys.executable, 'test_runner.py'], check=True)
        print("✅ Tests passed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Tests failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_test_environment()
    if success:
        print("\n🎉 Setup completed successfully!")
        print("You can now run: python run.py")
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        sys.exit(1)
