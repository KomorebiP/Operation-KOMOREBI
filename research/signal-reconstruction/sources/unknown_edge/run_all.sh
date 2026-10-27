#!/usr/bin/env bash
set -euo pipefail
python universal_unknown_edge_recovery.py --out .
pdflatex -interaction=nonstopmode -halt-on-error Universal_Unknown_Edge_Recovery.tex
pdflatex -interaction=nonstopmode -halt-on-error Universal_Unknown_Edge_Recovery.tex
