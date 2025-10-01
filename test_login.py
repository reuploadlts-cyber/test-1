#!/usr/bin/env python3
"""Test script for IVASMS login functionality."""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def test_login():
    """Test the IVASMS login functionality."""
    try:
        print("🧪 Testing IVASMS Login...")
        
        # Import required modules
        from src.config import Config
        from src.storage import Storage
        from src.monitor import IVASMSMonitor
        
        # Load configuration
        print("📋 Loading configuration...")
        config = Config()
        print(f"✅ Email: {config.ivasms_email}")
        print(f"✅ Admin IDs: {config.admin_ids}")
        
        # Initialize storage
        print("💾 Initializing storage...")
        storage = Storage()
        await storage.initialize()
        print("✅ Storage initialized")
        
        # Create monitor
        print("🔍 Creating monitor...")
        monitor = IVASMSMonitor(storage, config)
        print("✅ Monitor created")
        
        # Test login
        print("🌐 Testing login to IVASMS.com...")
        print("Note: This will open a browser window")
        
        success = await monitor.start()
        
        if success:
            print("✅ Login successful!")
            print("🎉 IVASMS monitoring is ready!")
            
            # Test navigation to SMS page
            print("📱 Testing SMS page navigation...")
            await monitor.page.goto("https://www.ivasms.com/portal/sms/received")
            await monitor.page.wait_for_load_state('domcontentloaded')
            print("✅ SMS page loaded successfully")
            
        else:
            print("❌ Login failed!")
            print("Check the logs above for error details")
            print("Screenshots may have been saved for debugging")
        
        # Cleanup
        print("🧹 Cleaning up...")
        await monitor.cleanup()
        await storage.close()
        print("✅ Cleanup completed")
        
        return success
        
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 IVASMS Login Test")
    print("=" * 25)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Please run: python setup_credentials.py")
        sys.exit(1)
    
    # Run the test
    success = asyncio.run(test_login())
    
    if success:
        print("\n🎉 All tests passed! Your bot is ready to run.")
        print("Run: python run.py")
    else:
        print("\n❌ Tests failed. Please check your credentials and try again.")
        sys.exit(1)
