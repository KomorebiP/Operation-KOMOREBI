#!/usr/bin/env bash
set -euo pipefail
python projector_generated_special_functions_v.py
python -m pytest -q
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_V.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_V.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Generated_Special_Functions_V.tex
