#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
command -v latexmk >/dev/null || { printf '%s\n' 'latexmk is required.' >&2; exit 1; }
command -v python3 >/dev/null || { printf '%s\n' 'Python 3 is required.' >&2; exit 1; }
mkdir -p build
python3 code/run_validation.py --out-dir build/validation_rerun
python3 code/verify_computation.py build/validation_rerun/computation_manifest.json
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build Machine_Understanding_v1.0.0.tex
cp -- build/Machine_Understanding_v1.0.0.pdf Machine_Understanding_v1.0.0.pdf
printf '%s\n' 'Rebuilt Machine_Understanding_v1.0.0.pdf. Fresh computation receipts are in build/validation_rerun/.'
