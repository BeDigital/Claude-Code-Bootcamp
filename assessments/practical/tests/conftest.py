"""conftest.py — put service/ on sys.path so tests can import bookmarks_api."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "service"))
