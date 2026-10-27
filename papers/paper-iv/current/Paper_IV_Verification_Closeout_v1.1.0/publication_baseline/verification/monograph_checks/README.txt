Paper IV fresh verification records, 8 October 2026 America/Chicago

COMPUTATIONAL_REVIEW.json and .txt summarize five successful inherited runs.
PRESERVATION_REVIEW.json and .txt compare the current traditional source with
the authoritative proofread source. Run compare_preservation.py again after
an editorial change, because its recorded final source hash is a snapshot.

Results
  Exact rational algebra: 1008 assertions
  Original CSV coefficient tables: 981 rows
  Original-paper suite: 647 checks
  Strengthened suite: 1246 checks
  Visual appendix: 147 checks, five false controls rejected and four certified
  rational cubic root brackets

The contracts give bounds. table_bounds.json lists every CSV parameter group.
Each runs/*/manifest.json records the actual argv, resources, execution time,
input hashes before and after execution, output hashes and exit status. The
five manifests passed the installed computation-audit validator with --root.

These runs inspect historical sources and historical PDFs unchanged. Some
inherited hygiene tests intentionally require their original AI disclosure.
They do not apply that requirement to the new monograph. run_inherited.py
redirects only the expected result write, leaving historical outputs intact.
No mathematical implementation is changed by the adapter.

Basic reproduction from the release root
  python audit/algebra_exact_checks.py
  python verification/monograph_checks/compare_preservation.py

To reproduce another inherited script without overwriting historical evidence,
create a fresh output directory and use the adapter with three arguments:
  python verification/monograph_checks/run_inherited.py SCRIPT OLD_RESULT NEW_RESULT

SCRIPT and OLD_RESULT are listed in jobs.json. NEW_RESULT must be inside your
fresh output directory. The adapter is independent of the Mathbox tool. The
optional Mathbox run_experiment.py supplied the recorded bounded execution and
v2 manifests for this edition.

Tested runtime: Python 3.12.14, SymPy 1.14.0 and mpmath 1.3.0. pandas is needed
by the historical table verifier. pdftotext is needed by the two historical
source/PDF hygiene suites. Exact algebra uses only the Python standard library.

lean, lake and elan were absent. No fresh Lean build occurred. Historical
formal evidence is retained separately. Finite assertions and sampled numerical
checks do not replace the manuscript's universal proofs or establish novelty.
