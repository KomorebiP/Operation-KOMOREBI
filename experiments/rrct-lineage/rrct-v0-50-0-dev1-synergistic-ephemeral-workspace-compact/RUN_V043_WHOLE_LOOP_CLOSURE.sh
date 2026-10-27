#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python}"
export PYTHONPATH="$ROOT/src${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONDONTWRITEBYTECODE=1
VERIFY_OUT="${TMPDIR:-/tmp}/rrct_v043_release_verification_$$.json"
"$PYTHON_BIN" -c "import rrct; assert rrct.__version__ == '0.43.0.dev1'; print('RRCT', rrct.__version__)"
"$PYTHON_BIN" -m pytest -q -p no:cacheprovider tests/test_v043_whole_loop_causal_closure.py
"$PYTHON_BIN" validation/verify_v043_release.py --output "$VERIFY_OUT"
"$PYTHON_BIN" validation/verify_v043_build_manifest.py
rm -f "$VERIFY_OUT" "$VERIFY_OUT.sha256"
printf '%s\n' 'V043_WHOLE_LOOP_CAUSAL_CLOSURE_VERIFIED'
printf '%s\n' "$ROOT/V0_43_BLOCK_SUMMARY.md"
