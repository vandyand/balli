#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
basilisp test tests/test_user_suite.lpy
