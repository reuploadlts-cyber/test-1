#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    try:
        print("Testing imports...")
        
        # Test basic imports
        from src.logger_setup import setup_logging, get_logger
        print("✅ Logger setup imported successfully")
        
        from src.config import Config
        print("✅ Config imported successfully")
        
        from src.storage import Storage, SMSMessage
        print("✅ Storage imported successfully")
        
        from src.monitor import IVASMSMonitor
        print("✅ Monitor imported successfully")
        
        from src.bot import OTPForwarderBot
        print("✅ Bot imported successfully")
        
        from src.main import main
        print("✅ Main imported successfully")
        
        print("\n🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
