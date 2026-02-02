#!/usr/bin/env bash
set -euo pipefail

# Install PlayLingo into a local virtualenv and optionally create system launchers

if [ ! -d ".venv" ]; then
  echo "Creating virtualenv..."
  python -m venv .venv
fi

# shellcheck disable=SC1091
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .

echo "Installed playlingo into .venv (editable)."

LAUNCHER_DIR=/usr/local/bin

echo "Creating launchers in ${LAUNCHER_DIR} (requires sudo)..."

TMP_DIR=$(mktemp -d)
# Use absolute project root so launchers work when copied to /usr/local/bin
PROJECT_ROOT="$(pwd)"
cat >"${TMP_DIR}/playlingo" <<SH
#!/usr/bin/env bash
VENV="${PROJECT_ROOT}/.venv"
if [ -x "$VENV/bin/python" ]; then
  exec "$VENV/bin/python" -m playlingo.cli "$@"
else
  exec python -m playlingo.cli "$@"
fi
SH

cat >"${TMP_DIR}/playlingo-gui" <<SH
#!/usr/bin/env bash
VENV="${PROJECT_ROOT}/.venv"
if [ -x "$VENV/bin/python" ]; then
  exec "$VENV/bin/python" -m playlingo.gui "$@"
else
  exec python -m playlingo.gui "$@"
fi
SH

chmod +x "${TMP_DIR}/playlingo" "${TMP_DIR}/playlingo-gui"

if [ -w "${LAUNCHER_DIR}" ]; then
  cp "${TMP_DIR}/playlingo" "${LAUNCHER_DIR}/playlingo"
  cp "${TMP_DIR}/playlingo-gui" "${LAUNCHER_DIR}/playlingo-gui"
  echo "Launchers installed to ${LAUNCHER_DIR}. Use 'playlingo' and 'playlingo-gui'."
else
  echo "Requesting sudo to install launchers to ${LAUNCHER_DIR}..."
  sudo cp "${TMP_DIR}/playlingo" "${LAUNCHER_DIR}/playlingo"
  sudo cp "${TMP_DIR}/playlingo-gui" "${LAUNCHER_DIR}/playlingo-gui"
  sudo chmod +x "${LAUNCHER_DIR}/playlingo" "${LAUNCHER_DIR}/playlingo-gui"
  echo "Launchers installed to ${LAUNCHER_DIR}. Use 'playlingo' and 'playlingo-gui'."
fi

rm -rf "${TMP_DIR}"

echo "Done."
