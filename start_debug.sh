#!/usr/bin/env bash
set -euo pipefail

# Start PlayLingo GUI with debug logging enabled
if [ -f .venv/bin/activate ]; then
  # activate venv if present
  # shellcheck disable=SC1091
  . .venv/bin/activate
fi

export PLAYLINGO_DEBUG=1
python -m playlingo.gui
