#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/reference"
"$PYTHON_BIN" reference/generate_v03_evidence.py >/tmp/osl_v03_certificate_index.json
"$PYTHON_BIN" reference/verify_osl_core_v03.py --output V03_UNIFIED_VERIFICATION.json >/tmp/osl_v03_unified.json
"$PYTHON_BIN" reference/generate_test_report.py >/tmp/osl_v03_test_report.json
"$PYTHON_BIN" reference/verify_sources.py
printf '%s\n' 'OSL_CORE_0_3_FINITE_METATHEORY_PASS'
