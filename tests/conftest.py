"""Test conftest to make `src` packages importable during tests."""
import os
import sys

# Add the src directory to sys.path so 'example' package is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
