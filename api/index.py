"""
Main API entry point for Vercel deployment
"""
import sys
import os
from pathlib import Path

# Add the parent directory to path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))
sys.path.insert(0, str(parent_dir / "src"))

from src.api_server import app

# Export the app for Vercel
handler = app
