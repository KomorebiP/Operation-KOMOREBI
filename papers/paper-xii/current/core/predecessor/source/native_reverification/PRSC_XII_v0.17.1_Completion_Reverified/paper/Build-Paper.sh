#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "$0")"
NAME=Paper_XII_Revised_Formalization_Complete_v0.17.0
pdflatex -interaction=nonstopmode -halt-on-error "$NAME.tex"
if command -v bibtex >/dev/null 2>&1; then bibtex "$NAME"
elif command -v bibtex.original >/dev/null 2>&1; then bibtex.original "$NAME"
else echo 'BibTeX unavailable; using the supplied matching .bbl file.'; test -s "$NAME.bbl"
fi
pdflatex -interaction=nonstopmode -halt-on-error "$NAME.tex"
pdflatex -interaction=nonstopmode -halt-on-error "$NAME.tex"
