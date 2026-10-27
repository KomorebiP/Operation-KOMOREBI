PAPER IV — CURRENT MONOGRAPH VERIFICATION
Edition: 8 October 2026. Actual run timestamps are recorded in each report.

Start with MONOGRAPH_VERIFICATION.json. The monograph_traditional_report.json,
monograph_visual_report.json and monograph_lean_report.json record final PDF
hashes, preservation, typography and formal/static scope. The full package
build replay is MONOGRAPH_PACKAGED_BUILD.json.

monograph_checks/COMPUTATIONAL_REVIEW.json contains fresh replay of five
bounded inherited suites, with raw output and validated computation manifests:
1008 exact algebra assertions, 981 CSV rows, 647 original-paper checks,
1246 strengthened checks and 147 visual checks. Five invalid controls were
rejected and four rational cubic brackets certified. These overlapping checks
are not added into a universal mathematical claim. Historical-source hygiene
checks refer to unchanged source snapshots, not a new authoring disclosure.

Current 24-figure regeneration and visual suite records also appear in
editable/visual_guide/checks/. The traditional FIGURE_MODELS.json records
exact models and finite plotting boundaries for the six new Python figures.
The preservation comparator confirms all 95 canonical statements and 68 proof
bodies are byte identical, with all protected formulas and references retained.

No new Lean build, kernel audit, semantic execution or namespace census was
run. lean, lake and elan are absent. September 5 v1.0.0 transcripts retain
their original provenance. Current Lean source/map/contract checks are static.
They do not independently elaborate theorem types. No new external literature
or novelty audit was performed.

The October 5/6 verification run under run/ describes its earlier environment
and narrower finite/static scope. It is historical evidence, not the current
run. Pre-monograph layout and package verdicts are archived in
provenance/pre_monograph_metadata/. source/ and audit/ retain dated records.

Replay source preservation from the package root:
  python3 verification/monograph_checks/compare_preservation.py
Replay the five bounded suites using the documented runner under
monograph_checks/README.txt. Use a separate output directory. Requires the
listed Python dependencies and does not execute Lean.
