#!/usr/bin/env bash
# Bump the project version using bump-my-version
#
# Usage:
#   scripts/bump.sh           # show current version and possible bumps
#   scripts/bump.sh patch     # 0.8.0 → 0.8.1
#   scripts/bump.sh minor     # 0.8.0 → 0.9.0
#   scripts/bump.sh major     # 0.8.0 → 1.0.0
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "No .venv found. Run scripts/venv-create.sh first."
    exit 1
fi

source "${VENV_DIR}/bin/activate"
cd "$PROJECT_DIR"

PART="${1:-}"
if [ -z "$PART" ]; then
    echo "Current version:"
    bump-my-version show current_version 2>/dev/null
    echo ""
    bump-my-version show-bump 2>/dev/null
    echo ""
    echo "Usage: scripts/bump.sh <patch|minor|major>"
else
    bump-my-version bump "$PART" --verbose
fi
