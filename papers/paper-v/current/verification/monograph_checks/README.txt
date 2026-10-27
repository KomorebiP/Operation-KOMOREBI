CURRENT PAPER V MONOGRAPH CHECKS

Read COMPUTATIONAL_REVIEW.json for the fresh finite evidence and exact limits.
Each runs/<suite>/manifest.json is a bounded v2 record with input/output hashes, command, actual runtime, exit status, resource limits and raw logs. Validate with:
python3 verification/monograph_checks/tools/validate_manifest.py verification/monograph_checks/runs/<suite>/manifest.json --root .

The documented original code is executed unchanged in temporary isolated copies. All 598 source files remain byte-identical to the recovered edition. Current source and guide figures are inspected separately by the editorial/build reports.

A replay output directory must be new. The launcher intentionally refuses to overwrite earlier evidence. To reproduce in a fresh package copy, move the existing runs/<suite> directory aside first, then use:
python3 -B verification/monograph_checks/launch_run.py <suite>
The choices are exact_and_verifier, current_pytest, historical_pytest, numerical_companion and annals_checker. The visual provenance replay uses:
python3 -B verification/monograph_checks/launch_visual_run.py
No launcher installs dependencies or invokes Lean.

For source preservation after edits:
python3 -B verification/monograph_checks/compare_preservation.py
The corrected October5 assembled traditional source is frozen in reference/. It supplies 119 protected numbered records and 83 proof environments. Byte preservation is not a proof-validity audit.

Historical provenance gaps: 17 files named by the recovered delivery manifest are absent, including the earlier verify_available.py runner. The original manifest is preserved in reference/HISTORICAL_DELIVERY_MANIFEST_2026-10-05.json. These bytes were not invented. All current runs are explicitly dated and distinguish exact algebra, numerical tolerance checks, static contract checks and inherited Lean evidence.
