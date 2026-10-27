#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONPATH="$ROOT/src"
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON_BIN" validation/verify_v048_build_manifest.py
"$PYTHON_BIN" validation/verify_v048_release.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v048_distributed_sparse_jspace.py
printf '%s\n' 'V048_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED'
