#!/usr/bin/env python3
"""Simple test runner for the OTP Forwarder Bot."""

import os
import sys
import subprocess
from pathlib import Path

def run_tests():
    """Run tests with proper environment setup."""
    
    # Set up environment variables
    env = os.environ.copy()
    env.update({
        'TELEGRAM_TOKEN': 'test_token',
        'ADMIN_IDS': '123456789',
        'IVASMS_EMAIL': 'test@example.com',
        'IVASMS_PASSWORD': 'test_password',
        'POLL_INTERVAL': '8',
        'HEADLESS': 'true',
        'LOG_LEVEL': 'INFO'
    })
    
    # Run pytest
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--disable-warnings',
        '--timeout=60',
        '--maxfail=5'
    ]
    
    print("Running tests with command:", ' '.join(cmd))
    print("Environment variables set for testing")
    
    try:
        result = subprocess.run(cmd, env=env, cwd=Path(__file__).parent)
        return result.returncode
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
