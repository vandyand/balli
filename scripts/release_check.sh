#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
basilisp run scripts/compile_check.lpy
scripts/test.sh
python3 -m build --wheel
python3 scripts/generate_api_docs.py
mkdocs build --strict
git diff --check
