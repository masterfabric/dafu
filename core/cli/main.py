#!/usr/bin/env python3
"""
DAFU CLI Main Entry Point
Enterprise Fraud Detection & Analytics Platform
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from core.cli.dafu import main

if __name__ == "__main__":
    main()
