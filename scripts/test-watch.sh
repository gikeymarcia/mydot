#!/usr/bin/env bash
# Continuous test runner — re-runs pytest on file changes (requires entr)
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "No .venv found. Run scripts/venv-create.sh first."
    exit 1
fi

if ! command -v entr &>/dev/null; then
    echo "entr is required: sudo apt install entr"
    exit 1
fi

echo "Watching for changes... (Ctrl+C to stop)"
"${VENV_DIR}/bin/python" -m pytest "${PROJECT_DIR}/tests" -v "$@"
while true; do
    find "$PROJECT_DIR" -name "*.py" | entr -rndp \
        "${VENV_DIR}/bin/python" -m pytest "${PROJECT_DIR}/tests" -v "$@"
    sleep 0.5
done
