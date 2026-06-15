import sys
from pathlib import Path

# Add backend directory to Python path so that backend imports work inside tests
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
