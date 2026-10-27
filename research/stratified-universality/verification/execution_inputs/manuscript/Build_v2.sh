#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

main="Komorebi_Stratified_Universality_Formal_Foundations_v2.0.0.tex"
mode="${1:-full}"

case "$mode" in
  full|validate-only|compile-only) ;;
  *)
    echo "usage: ./Build_v2.sh [full|validate-only|compile-only]" >&2
    exit 2
    ;;
esac

if [[ "$mode" != "compile-only" ]]; then
  python make_concordance_v04.py
  python verify_block15_lane_transport.py
  python verify_block16_holonomy_lane_transport.py
  python verify_block17_semantic_extension.py
  python generate_latex_components.py
  python generate_block17_figures.py
fi

if [[ "$mode" != "validate-only" ]]; then
  rm -f "${main%.tex}.aux" "${main%.tex}.log" "${main%.tex}.out" "${main%.tex}.toc"
  for _ in 1 2 3; do
    pdflatex -interaction=nonstopmode -halt-on-error -file-line-error "$main" >/dev/null
  done
  python verify_formal_foundations_v2_publication.py
  # The audit emits the journal-facing audit table and synchronized count macros.
  for _ in 1 2; do
    pdflatex -interaction=nonstopmode -halt-on-error -file-line-error "$main" >/dev/null
  done
  python verify_formal_foundations_v2_publication.py
else
  python verify_formal_foundations_v2_publication.py
fi
