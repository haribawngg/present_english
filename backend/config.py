"""Filesystem paths and server limits, independent of request handling."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FRONTEND_DIST = ROOT / "frontend" / "dist"
DEFAULT_MODEL_DIR = ROOT / "artifacts"
MAX_CONTENT_LENGTH = 3_000_000
