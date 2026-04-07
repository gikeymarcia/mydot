#!/usr/bin/env bash
# Create a fresh development virtual environment
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"

if [ -d "$VENV_DIR" ]; then
    echo "Removing existing venv at ${VENV_DIR}"
    rm -rf "$VENV_DIR"
fi

echo "Creating virtual environment at ${VENV_DIR}"
python3 -m venv "$VENV_DIR"

echo "Installing development dependencies"
"${VENV_DIR}/bin/pip" install --upgrade pip
"${VENV_DIR}/bin/pip" install -r "${PROJECT_DIR}/requirements_dev.txt"

echo ""
echo "Done. Activate with:"
echo "  source ${VENV_DIR}/bin/activate"
