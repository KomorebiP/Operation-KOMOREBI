#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT${PYTHONPATH:+:$PYTHONPATH}"
"$PYTHON_BIN" VERIFY_PACKAGE.py
"$PYTHON_BIN" run_pilot.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_nested_workspace_pilot.py
