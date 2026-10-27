#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"
export SOURCE_DATE_EPOCH=1788307200
export PYTHONHASHSEED=0
export TZ=UTC
PYTHONPATH=src python examples/run_certificates.py
PYTHONPATH=src python -m pytest -q
latexmk -pdf -interaction=nonstopmode -halt-on-error Hypergraph_Lumpability_Bayesian_Refinement.tex
python tools/audit_manuscript.py
