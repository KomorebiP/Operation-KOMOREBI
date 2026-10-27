#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$ROOT/src"
cd "$ROOT"
"$PYTHON" -c "import rrct; assert rrct.__version__ == '0.44.0.dev1'; print('RRCT', rrct.__version__)"
"$PYTHON" -m pytest -q -p no:cacheprovider tests/test_v044_transformational_self_continuity.py
TEMP="$(mktemp -d)"
trap 'rm -rf "$TEMP"' EXIT
VERIFY_ARGS=(--output "$TEMP/V0_44_RELEASE_VERIFICATION.json" --skip-replay)
STATUS='V044_RELEASE_VERIFIED'
if [[ "${1:-}" == '--full-replay' ]]; then
    VERIFY_ARGS=(--output "$TEMP/V0_44_RELEASE_VERIFICATION.json")
    STATUS='V044_RELEASE_VERIFIED_WITH_FRESH_REPLAY'
fi
"$PYTHON" validation/verify_v044_release.py "${VERIFY_ARGS[@]}"
"$PYTHON" validation/verify_v044_build_manifest.py
printf '%s\n' "$STATUS"
