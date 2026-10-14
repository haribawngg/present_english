"""Compatibility entry point; application setup lives in backend.app."""
from backend.app import create_app

__all__ = ["create_app"]
