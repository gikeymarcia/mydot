#!/usr/bin/env bash
# Build source distribution and wheel, optionally upload
#
# Usage:
#   scripts/build.sh          # build only, check with twine
#   scripts/build.sh test     # build + upload to test.pypi.org
#   scripts/build.sh pypi     # build + upload to pypi.org
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_DIR="${PROJECT_DIR}/.venv"

if [ ! -d "$VENV_DIR" ]; then
    echo "No .venv found. Run scripts/venv-create.sh first."
    exit 1
fi

source "${VENV_DIR}/bin/activate"

# Clean old builds
rm -rf "${PROJECT_DIR}/build" "${PROJECT_DIR}/dist"

echo "Building source distribution and wheel"
python3 "${PROJECT_DIR}/setup.py" sdist bdist_wheel

echo ""
echo "Build contents:"
tar tzf dist/*tar.gz

echo ""
echo "Twine check:"
twine check dist/*

TARGET="${1:-}"
if [ -z "$TARGET" ]; then
    echo ""
    echo "Build ready. To upload, run:"
    echo "  scripts/build.sh test   # upload to test.pypi.org"
    echo "  scripts/build.sh pypi   # upload to pypi.org"
elif [ "$TARGET" == "test" ]; then
    echo ""
    echo "Uploading to test.pypi.org"
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
elif [ "$TARGET" == "pypi" ]; then
    echo ""
    echo "Uploading to pypi.org"
    twine upload dist/*
else
    echo "Unknown target: $TARGET (use 'test' or 'pypi')"
    exit 1
fi
