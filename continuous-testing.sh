#!/usr/bin/env bash

# re-run all tests if any .py files change in the project
while true; do
    fd -e py | entr -rdc python -m pytest .
    sleep 1
done
