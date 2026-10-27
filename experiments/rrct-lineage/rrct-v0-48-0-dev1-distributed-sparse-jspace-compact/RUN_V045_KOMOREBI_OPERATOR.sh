#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONPATH="$ROOT/src"
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON_BIN" validation/verify_v045_release.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v045_komorebi_operator_self_model.py
