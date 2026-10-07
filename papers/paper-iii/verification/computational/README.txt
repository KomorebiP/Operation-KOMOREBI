Paper III: bounded computational verification, 2026-10-05

Fresh checks completed successfully within the available environment:

* Original finite-release VERIFY.sh: all 34 release files present, all 33 listed
  SHA-256 values matched. Static map and saved transcript parity passed for
  41 rows and 143 explicit targets. This command did not execute Lean.
* Original strengthened verification/verify_strengthened.py: 11/11 groups
  passed. These combine exact integer checks, finite examples evaluated with
  floating arithmetic, and checks of the preserved original TeX/Bib sources.
* Original canonical schematic figure generator: all three PNGs regenerated
  byte for byte. This is graphical reproducibility, not three additional tests
  of mathematical theorems.
* The three executed source trees stayed unchanged: 34 finite-release files,
  17 strengthened-source files, and 32 visual-source files. The outer provenance
  record additionally hashes all 18 historical-source files, for 101 preserved
  source files plus the portable runner.

Overall status: PARTIAL, because fresh exact visual execution was unavailable.

The 124 visual checks and four deliberately false controls were NOT rerun.
Their preserved report is dated 2026-09-12. The current visual model and checker
hashes match that report. The 22 shipped TikZ plates were NOT regenerated in
this run. SymPy was absent from both installed interpreters and the old shared
environment was gone. An installation attempt met a 403 proxy failure, and
automatic approval review rejected continuing the installation. The review
cited the earlier Paper II-only scope and external-package execution. No
installation bypass was attempted and no new SymPy execution is claimed.

No new Lean compilation, kernel audit, or mathematical proof is claimed.
The preserved finite-release report/transcript, dated 2026-09-03, records
143 mapped declarations, 88 mapped theorems, 55 mapped constructions, and a
468-declaration namespace audit containing 229 theoremInfo declarations.
The fresh static checker reconciles those historical records with current
source bytes. It does not reproduce the historical kernel run.

Run evidence
------------
run_2026-10-05/results/verification.json contains the scientific result.
run_2026-10-05/manifest.json is the outer v2 execution-provenance record.
Its status 'completed' means the requested available-stage runner exited
successfully; the scientific result still explicitly says PARTIAL.
The manifest validates against all declared source input hashes.

The run took 3.09 seconds. Caps: 300 seconds wall time, 180 seconds CPU per
process, 2 GiB address space per process, one CPU, one cooperative numerical
library thread, and 1 MiB combined outer logs. All three child stderr logs are
empty. Logs and source hashes are included. No repeated broad tests were run.

Portable rerun
--------------
With Python 3.12 or later, NumPy, Matplotlib 3.10.8, and Pillow 12.3.0 installed:

python Run-Computational-Checks.py --finite-root PATH_TO_FINITE_RELEASE \
  --expanded-root PATH_TO_STRENGTHENED_SOURCE --visual-root PATH_TO_VISUAL_SOURCE \
  --output-dir NEW_OUTPUT_DIRECTORY

Add SymPy 1.14.0 in an environment where installing it is authorized to enable
the existing exact visual checks and TikZ regeneration. The runner itself
never installs packages or accesses a network. It records unavailable visual
stages explicitly when SymPy is absent. All commands operate on temporary
copies and preserve original source trees. The output directory must be new.

COMPUTATIONAL_SCOPE.txt records ranges, arithmetic, and interpretation.
computation_contract.json records the original bounded run contract.
bounded_runner_command.json preserves exact execution argv. Its original
absolute workspace paths are provenance, not portable path defaults.

The original .lake and dependency caches are deliberately absent from the
34-file finite release and excluded by its own integrity manifest. No required
release file is missing.
