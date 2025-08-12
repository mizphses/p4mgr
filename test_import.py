#!/usr/bin/env python3
"""Test imports for debugging systemd service issues."""

import sys
print(f"Python version: {sys.version}")
print(f"Python path: {sys.executable}")

try:
    from p4mgrcore.config import Config
    print("✓ Config import successful")
except Exception as e:
    print(f"✗ Config import failed: {e}")

try:
    from p4mgrcore.rgbmatrix import RGBMatrix, RGBMatrixOptions
    print("✓ RGBMatrix import successful")
except Exception as e:
    print(f"✗ RGBMatrix import failed: {e}")

try:
    from p4mgrcore.input_handler import InputHandler
    print("✓ InputHandler import successful")
except Exception as e:
    print(f"✗ InputHandler import failed: {e}")

try:
    from p4mgrcore.main import P4MgrApp
    print("✓ P4MgrApp import successful")
except Exception as e:
    print(f"✗ P4MgrApp import failed: {e}")