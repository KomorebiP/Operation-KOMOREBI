Paper I machine-native release companion — 15 October 2026

Current mathematical record interface
  formal/coverage/COVERAGE_108.json at the release root.
  Appendix A reproduces all 108 current manuscript statements and 69 source
  proofs, with current locators, hashes, and formal correspondence scopes.

Preserved executable runtime
  source/machine_v1.0.1/ at the release root.
  Its entrypoint and tests retain their exact documented interface scope.
  Earlier runtime source, historical Lean maps, and receipts retain their
  original identity. They are not certificates for changed source statements.

Build the current companion from editable/machine/
  python3 build_companion.py

This writes the PDF in editable/machine/. To update both distributed PDF
copies from the release root, use:
  python3 scripts/build_pdfs.py --component machine

The builder reads the current coverage inventory, regenerates the current
catalog and guide status tables through scripts/build_release_companion_data.py,
and runs pdflatex three times. It does not execute Lean or reclassify coverage.
The release companion evidence JSON is used by default. Use --metadata to
select another explicitly recorded verification summary. The TeX source and generated tables are
sufficient for a direct render without regenerating data:

  pdflatex -interaction=nonstopmode -halt-on-error Paper_I_Machine_Native_Final.tex
  pdflatex -interaction=nonstopmode -halt-on-error Paper_I_Machine_Native_Final.tex
  pdflatex -interaction=nonstopmode -halt-on-error Paper_I_Machine_Native_Final.tex

Historical generation
  build_historical_companion.py is the preserved earlier v1.0.1 generator.
  Run it only in a separate historical working copy: it writes the historical
  TeX and would overwrite the release edition. It is retained for provenance.

Runtime scope
  Six exact finite actions and two operation-profile gates. The gate reads
  direct action_required_operations; it does not validate target hypotheses,
  transitive closure, or returned boundary guards. The PDF states this scope.

Current verification
  See formal/evidence/ and the release verification record. Typesetting and
  source-to-catalog identity checks are distinct from compiler acceptance,
  logical kernel replay, mathematical correspondence, and Python fixtures.
