#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_BIN="${PYTHON:-python}"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
"$PYTHON_BIN" validation/verify_v049_build_manifest.py
"$PYTHON_BIN" validation/verify_v049_results.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v049_instrumented_transformer_dyad.py
printf '%s\n' 'V049_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED'
