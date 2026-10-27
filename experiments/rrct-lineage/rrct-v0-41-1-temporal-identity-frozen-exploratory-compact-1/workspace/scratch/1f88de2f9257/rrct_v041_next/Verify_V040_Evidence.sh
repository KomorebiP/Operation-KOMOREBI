#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
PYTHON_BIN="${1:-python}"
export PYTHONPATH="$ROOT/src:$ROOT"
"$PYTHON_BIN" -m pytest -q \
  "$ROOT/tests/test_v036_unified_causal_loop.py" \
  "$ROOT/tests/test_v037_post_change_closure.py" \
  "$ROOT/tests/test_v038_access_generalization.py" \
  "$ROOT/tests/test_v039_autonomous_self_diagnosis.py" \
  "$ROOT/tests/test_v040_robust_reflexive_diagnosis.py"
if [[ -d "$ROOT/validation/v0.40_robust_reflexive_diagnosis_campaign" ]]; then
  "$PYTHON_BIN" "$ROOT/validation/audit_v040_campaign.py" --project-root "$ROOT"
else
  echo "Raw campaign rows are absent. Source tests passed; full evidence audit was skipped."
fi
