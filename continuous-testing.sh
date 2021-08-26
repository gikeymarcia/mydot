#!/usr/bin/env bash
# shellcheck disable=SC2086

# re-run all tests if any .py files change in the project
while true; do
    fd -e py | entr -rdc python -m pytest -vv .
    sleep 1
done
