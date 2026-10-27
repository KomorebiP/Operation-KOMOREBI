#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mode="${1:-normal}"
main="Komorebi_Stratified_Universality_Foundations_v1.16.0_Block16.tex"
standalone_dir="../standalone"
standalone_main="Holonomy_Twisted_Lane_Transport_and_Orbit_Descent.tex"

if [[ "$mode" == "--full" ]]; then
  python verify_block03_periodic_atlas.py
  python verify_block04_rational_mask_atlas.py
  python verify_block05_regular_atlas.py
  python verify_block06_integral_tower.py
  python verify_block07_product_multiplicative.py
  python verify_block08_local_polyphase.py
  python verify_block09_holonomic.py
  python verify_block10_algebraic.py
  python generate_figures.py
  python generate_block06_integral_figures.py
  python generate_block07_product_figures.py
  python generate_block08_local_figures.py
  python generate_block09_holonomic_figures.py
  python generate_block10_algebraic_figures.py
elif [[ "$mode" == "--audit-only" ]]; then
  python verify_prior_regression_records.py
  python verify_recent_regression_records.py
elif [[ "$mode" == "normal" ]]; then
  python verify_prior_regression_records.py
else
  echo "usage: ./Build.sh [--full|--audit-only]" >&2
  exit 2
fi

if [[ "$mode" != "--audit-only" ]]; then
  python verify_block11_nonlinear_tree.py
  python verify_block12_galois_tannakian.py
  python verify_block13_bridge_synthesis.py
  python verify_block13_global_invariants.py
  python assemble_block13_outputs.py
  python generate_block11_nonlinear_figures.py
  python generate_block12_galois_figures.py
  python generate_block13_global_figures.py
fi

python verify_block15_lane_transport.py
python verify_block16_holonomy_lane_transport.py
python generate_latex_components.py
python prepare_block14_publication.py
python generate_block14_publication_figure.py

latexmk -C "$main" >/dev/null 2>&1 || true
latexmk -silent -pdf -interaction=nonstopmode -halt-on-error -file-line-error "$main"
python verify_block16_publication_audit.py
latexmk -silent -pdf -interaction=nonstopmode -halt-on-error -file-line-error "$main"
python verify_block16_publication_audit.py

(
  cd "$standalone_dir"
  latexmk -C "$standalone_main" >/dev/null 2>&1 || true
  latexmk -silent -pdf -interaction=nonstopmode -halt-on-error -file-line-error "$standalone_main"
)
