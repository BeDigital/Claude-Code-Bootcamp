"""Add module-04 winner to sys.path so tests import the real notes_api."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[2] / "module-04" / "winner"))
