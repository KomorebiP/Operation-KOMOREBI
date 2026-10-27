#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname "${BASH_SOURCE[0]}")/.."
python3 tests/test_block03.py
python3 tests/test_recurrence_grammar.py
python3 tests/plot_block03.py
if [[ ${KOMOREBI_LEAN_KIT:-} != '' ]]; then
  for f in FiniteObservation FilterBudget WittCarryExample; do
    bash "$KOMOREBI_LEAN_KIT/run.sh" check "proofs/$f.lean"
  done
  if bash "$KOMOREBI_LEAN_KIT/run.sh" check proofs/Block03Negative.lean >/dev/null 2>&1; then
    echo 'FAILED: negative control unexpectedly accepted' >&2
    exit 1
  fi
  echo 'PASS: Lean theorems and negative control'
else
  echo 'Lean replay skipped. Set KOMOREBI_LEAN_KIT to the unpacked portable runtime.'
fi
