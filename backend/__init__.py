"""
Backend package initialization
"""

# Add the backend directory to Python path for proper imports
import sys
import os

# Get the backend directory path
backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
