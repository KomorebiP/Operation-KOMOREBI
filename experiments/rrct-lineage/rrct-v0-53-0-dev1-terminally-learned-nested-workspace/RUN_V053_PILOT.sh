#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export PYTHONDONTWRITEBYTECODE=1
python -m pytest -q -p no:cacheprovider tests/test_v053.py
python validation/verify_package.py
