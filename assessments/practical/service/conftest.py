"""conftest.py — put service/ on sys.path for test collection."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
