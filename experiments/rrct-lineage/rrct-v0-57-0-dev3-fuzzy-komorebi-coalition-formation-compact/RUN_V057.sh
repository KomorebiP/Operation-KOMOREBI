#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
"$PYTHON_BIN" "$ROOT/validation/verify_preoutcome.py"
"$PYTHON_BIN" "$ROOT/validation/run_holdout.py"
"$PYTHON_BIN" "$ROOT/validation/analyze_holdout.py"
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider "$ROOT/tests/test_v057.py"
