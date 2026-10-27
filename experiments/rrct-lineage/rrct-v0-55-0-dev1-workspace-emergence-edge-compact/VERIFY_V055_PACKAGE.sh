#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
python validation/verify_build_manifest.py
python validation/verify_preoutcome.py
python validation/verify_overcomplete_freeze.py
python validation/verify_release.py
python -m pytest -q -p no:cacheprovider tests/test_v055_edge.py
printf '%s\n' 'V055_PACKAGE_VERIFIED'
