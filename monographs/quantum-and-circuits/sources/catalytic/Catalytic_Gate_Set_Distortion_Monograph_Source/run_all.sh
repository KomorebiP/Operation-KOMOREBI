#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERIFY="$ROOT/verification"
mkdir -p "$VERIFY"

printf '[1/8] Python tests\n'
(
  cd "$ROOT/code"
  PYTHONPATH=. python -m pytest -q
)

printf '[2/8] Small exact Python atlas\n'
(
  cd "$ROOT/code"
  PYTHONPATH=. python scripts/run_atlas.py --output "$VERIFY/atlas_small.json"
)
cmp "$VERIFY/atlas_small.json" "$ROOT/results/atlas_small.json"

printf '[3/8] OpenQASM witness export\n'
(
  cd "$ROOT/code"
  PYTHONPATH=. python scripts/export_qasm_examples.py
)

printf '[4/8] Compile optimized Clifford verifier\n'
g++ -O3 -std=c++20 "$ROOT/code/scripts/clifford_census.cpp" -o "$VERIFY/clifford_census"

printf '[5/8] Exact three-qubit Clifford censuses\n'
"$VERIFY/clifford_census" --n 3 --metric total --output "$VERIFY/clifford_n3_total.json"
"$VERIFY/clifford_census" --n 3 --metric total --swap --output "$VERIFY/clifford_n3_total_swap.json"
"$VERIFY/clifford_census" --n 3 --metric entangling --output "$VERIFY/clifford_n3_entangling.json"
cmp "$VERIFY/clifford_n3_total.json" "$ROOT/results/clifford_n3_total.json"
cmp "$VERIFY/clifford_n3_total_swap.json" "$ROOT/results/clifford_n3_total_swap.json"
cmp "$VERIFY/clifford_n3_entangling.json" "$ROOT/results/clifford_n3_entangling.json"

printf '[6/8] Regenerate vector figures\n'
PYTHONPATH="$ROOT/code" python "$ROOT/code/scripts/make_monograph_figures.py"

printf '[7/8] Build monograph\n'
(
  cd "$ROOT"
  latexmk -pdf -interaction=nonstopmode -halt-on-error \
    -outdir=build Catalytic_Gate_Set_Distortion_Monograph.tex
)

printf '[8/8] PDF checks\n'
PDF="$ROOT/build/Catalytic_Gate_Set_Distortion_Monograph.pdf"
if command -v qpdf >/dev/null 2>&1; then
  qpdf --check "$PDF"
fi
if [[ -x /home/oai/skills/pdfs/scripts/pdf_preflight.py ]] || [[ -f /home/oai/skills/pdfs/scripts/pdf_preflight.py ]]; then
  python /home/oai/skills/pdfs/scripts/pdf_preflight.py "$PDF"
fi

if [[ "${RUN_CORE_SUPPLEMENT:-0}" == "1" ]]; then
  printf '[optional] Complete unitriangular-core supplement\n'
  (cd "$ROOT/core_extract/supplement" && bash ./run_all.sh)
fi

printf 'All requested checks passed.\n'
