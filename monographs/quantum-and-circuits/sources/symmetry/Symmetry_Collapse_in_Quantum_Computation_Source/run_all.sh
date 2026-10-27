#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"
PYTHONPATH=code python3 code/validate.py
PYTHONPATH=code python3 code/validate_exact.py
PYTHONPATH=code python3 code/validate_boundaries.py
python3 code/make_figures.py
latexmk -pdf -interaction=nonstopmode Symmetry_Collapse_in_Quantum_Computation.tex
{
  printf '%s\0' \
    Symmetry_Collapse_in_Quantum_Computation.pdf \
    Symmetry_Collapse_in_Quantum_Computation.tex \
    README.md CLAIM_STATUS.md BUILD_AUDIT.md EXTENSION_NOTES.md run_all.sh
  find chapters code data figures sources -type f -print0
} | sort -z | xargs -0 sha256sum > SHA256SUMS.txt
