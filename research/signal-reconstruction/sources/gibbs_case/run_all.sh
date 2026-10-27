#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python gibbs_packet_case.py --manifest
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Gibbs_Case_Study.tex
pdflatex -interaction=nonstopmode -halt-on-error Projector_Resolved_Gibbs_Case_Study.tex
