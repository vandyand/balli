#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
basilisp run scripts/compile_check.lpy
scripts/test.sh
rm -rf dist
python3 -m build
python3 -m twine check dist/*
python3 scripts/generate_api_docs.py
mkdocs build --strict
git diff --check
