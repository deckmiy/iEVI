#!/usr/bin/env python3
"""
Adaptive Piston Algorithm - Pressure Analysis Tool
Command-line interface for pressure data analysis and clogging detection.

This is the main entry point for the adaptive piston algorithm.
"""

import sys
import os

# Ensure src is in Python path and treat it as a package
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

# Now import from src.cli.main
try:
    from src.cli.main import main
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory.")
    sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())