#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONPATH="$ROOT/src"
export PYTHONDONTWRITEBYTECODE=1
"$PYTHON_BIN" validation/verify_v047_build_manifest.py
"$PYTHON_BIN" validation/verify_v047_release.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v047_distributed_shared_workspace.py
printf '%s\n' 'V047_PACKAGE_AND_SCIENTIFIC_EVIDENCE_VERIFIED'
