#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONPATH="$ROOT/src"
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON_BIN" validation/verify_v046_release.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v046_jspace_self_indexed_workspace.py
