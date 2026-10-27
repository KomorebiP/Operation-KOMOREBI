#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="$ROOT/experiment"
export PYTHONDONTWRITEBYTECODE=1
python "$ROOT/experiment/osl_emergence_pilot.py" verify --root "$ROOT"
rm -f "$ROOT"/checkpoints/*.pt
rm -f "$ROOT"/results/PILOT_ANALYSIS.json "$ROOT"/results/PILOT_METRICS.csv "$ROOT"/results/DATASET_MANIFEST.json
python "$ROOT/experiment/osl_emergence_pilot.py" run --root "$ROOT"
python "$ROOT/experiment/osl_emergence_pilot.py" recheck --root "$ROOT"
python "$ROOT/experiment/postoutcome_controls.py"
python "$ROOT/experiment/postoutcome_geometry_audit.py"
python "$ROOT/experiment/postoutcome_intervention_sweep.py"
python "$ROOT/experiment/build_release.py"
python -m pytest -q -p no:cacheprovider "$ROOT/tests"
python "$ROOT/experiment/build_manifest.py"
