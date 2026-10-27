#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/reference"
export SOURCE_DATE_EPOCH=1787616000
export FORCE_SOURCE_DATE=1
export TZ=UTC

"$PYTHON_BIN" verify_release.py
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests
"$PYTHON_BIN" reference/verify_sources.py
make rebuild
"$PYTHON_BIN" reference/generate_pdf_preflight.py >/tmp/osl_v05_clean_preflight.json
"$PYTHON_BIN" verify_release.py

if [[ "${FULL_REPLAY:-0}" == "1" ]]; then
  PYTHON="$PYTHON_BIN" "$ROOT/RUN_OSL_CORE.sh"
  make metadata
  "$PYTHON_BIN" verify_release.py
  printf '%s\n' 'OPERATOR_SYMBOLIC_AI_V05_FULL_REPLAY_VERIFIED'
else
  printf '%s\n' 'OPERATOR_SYMBOLIC_AI_V05_RELEASE_VERIFIED'
fi
