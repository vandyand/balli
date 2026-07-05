#!/usr/bin/env bash
# Run the balli test suite. Extra args are passed through to basilisp test.
set -euo pipefail
cd "$(dirname "$0")/.."
exec basilisp test --include-path . -- "$@"
