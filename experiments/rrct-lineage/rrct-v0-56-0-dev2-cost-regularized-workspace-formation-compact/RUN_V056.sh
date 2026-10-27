#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; PYTHON_BIN="${PYTHON:-python}"
"$PYTHON_BIN" "$ROOT/validation/verify_freeze.py"
PYTHONPATH="$ROOT/src" "$PYTHON_BIN" -m pytest -q -p no:cacheprovider "$ROOT/tests/test_v056.py"
