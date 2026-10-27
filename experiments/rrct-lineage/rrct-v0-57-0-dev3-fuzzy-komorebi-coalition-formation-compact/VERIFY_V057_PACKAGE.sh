#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
"$PYTHON_BIN" validation/verify_build_manifest.py
"$PYTHON_BIN" validation/verify_release.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v057.py
printf '%s\n' 'V057_PACKAGE_VERIFIED'
