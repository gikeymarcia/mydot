#!/usr/bin/env bash
# Run the test suite
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "No .venv found. Run scripts/venv-create.sh first."
    exit 1
fi

"${VENV_DIR}/bin/python" -m pytest "${PROJECT_DIR}/tests" -v "$@"
