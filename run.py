#!/usr/bin/env python3
"""Entry point for running the OTP Forwarder Bot."""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the main function
from src.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
