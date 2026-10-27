#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
command -v latexmk >/dev/null || { echo 'latexmk is required.' >&2; exit 1; }
mkdir -p build
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build Machine_Societies_v1.0.0.tex
printf '\nBuilt: %s/build/Machine_Societies_v1.0.0.pdf\n' "$PWD"
