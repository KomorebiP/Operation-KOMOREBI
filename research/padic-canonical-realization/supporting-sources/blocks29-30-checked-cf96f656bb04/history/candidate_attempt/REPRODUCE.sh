#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
: "${KOMOREBI_LEAN_RUNTIME:?Set this to the extracted pinned portable runtime directory}"
export PATH="$KOMOREBI_LEAN_RUNTIME/toolchain/bin:$PATH"
export PYTHONDONTWRITEBYTECODE=1
python verification/prepare_offline.py "$KOMOREBI_LEAN_RUNTIME"
for name in PrimePowerIdeals PrimePowerIdealValuation CoordinateIdealClosure IdealMaskAutomaton CyclicIdealCoordinates CyclicMaskAutomaton IdealClosureExamples; do
  lake build "KomorebiPadic.$name"
done
lake build
lake env lean -DwarningAsError=true verification/AllAxioms29_30.lean
lake env lean -DwarningAsError=true verification/IdealCyclicExamples.lean
python verification/audit_ideal_cyclic.py
for name in FalseControl PlaceholderControl OverclaimControl; do
  if lake env lean -DwarningAsError=true "verification/$name.lean"; then
    echo "Invalid control unexpectedly accepted: $name" >&2
    exit 1
  fi
done
echo 'Execution completed. Inspect all control diagnostics and axiom coverage before promotion.'
