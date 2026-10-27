#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p audit publication
python3 checks/verify_sources.py
python3 checks/build_concordance.py
python3 checks/static_integration.py
python3 checks/exact_examples.py
python3 checks/revision_exact.py
python3 checks/expansion_exact.py
python3 checks/deepening_exact.py
python3 checks/regularization_exact.py
python3 checks/inexact_certificates_exact.py
python3 checks/verify_focused_evidence.py
python3 checks/verify_written_extensions.py
python3 examples/protected_repair.py --demo > examples/three_preservation_problems.json
python3 examples/approximation_models.py > examples/approximation_models_demo.json
python3 examples/budgeted_repair.py > examples/budgeted_repair_demo.json
python3 examples/inexact_repair_certificate.py > examples/inexact_repair_demo.json
python3 checks/build_figures.py
python3 checks/build_expansion_figures.py
python3 checks/build_deepening_figures.py
python3 checks/build_regularization_figures.py
python3 checks/build_certificate_figures.py
python3 evidence/moving_v032/scripts/run_exact_audit.py --output-dir audit/publication_fresh_finite
python3 checks/edition_stats.py
python3 checks/build_lean_guide.py
pushd source >/dev/null
for name in Komorebi_Space_Monograph Komorebi_Space_Visual_Guide Komorebi_Space_Lean_Guide; do
  for pass in 1 2 3; do
    if ! pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../publication "${name}.tex" > "../audit/${name}_final${pass}.stdout" 2>&1; then
      tail -60 "../audit/${name}_final${pass}.stdout"
      exit 1
    fi
  done
done
popd >/dev/null
python3 checks/publication_preflight.py
python3 checks/hash_manifest.py
printf '\nPublication build and mechanical checks passed. Existing accepted formal evidence was checked; Lean was not rerun by this command.\n'
