@echo off
REM Run test suite with debug logging enabled (Windows)
set PLAYLINGO_DEBUG=1
pytest -q
