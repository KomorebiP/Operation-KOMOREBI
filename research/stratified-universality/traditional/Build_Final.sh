#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python generate_final_concordance.py
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error -file-line-error Stratified_Universality_Traditional.tex > "final_edition_validation/build_pass_${pass}.txt"
done
python verify_final_publication.py
