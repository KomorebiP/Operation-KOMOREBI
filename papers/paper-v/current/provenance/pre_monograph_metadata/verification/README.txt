PAPER V FINAL EDITION: CURRENT COMPUTATIONAL EVIDENCE
Edition date: October 5, 2026 (America/Chicago)
Execution date: October 6, 2026 UTC

Outcome: AVAILABLE_SUBSET_PASS. The full historical release gate was not rerun.

Freshly reproduced, using the original unmodified checker scripts in temporary
copies of the recovered release:

1. The optimized static source verifier passed. It validated the 20-result core
   contract, 225 explicit theorem targets, 23 proof modules, 25 Lean files,
   source hashes, pinned configuration, imports and axiom-audit target coverage.
   Static source checks do not compile Lean or certify the English manuscript.
2. All 20 exact-model tests passed with 305,933 counted assertions, using exact
   rational arithmetic and an explicit representation of Q(sqrt(2)).
3. All 16 verifier tests passed, including positive and negative static controls,
   rejection under optimized Python, and subprocess failure/timeout handling.
   Their positive path is a static path, not a successful Lean compiler run.
4. The original companion numerical runner reproduced all 52 floating metrics
   exactly as stored in the historical numerical JSON. The accepted comparison
   tolerance was rtol=1e-10, atol=1e-12. All 18 PDF/PNG figure pairs were generated
   after deleting the copied output directories, preventing reuse of old files.
5. The Annals extension checker passed 11,052 checks in 13 groups. These are a
   mixture of exact finite indexing/source checks and floating numerical checks.
   They are not 11,052 exact arithmetic assertions or separate theorems.
6. Both recovered ZIP checksums and CRCs passed. Their complete extracted file
   sets and bytes match: 493 complete-release files and 105 Annals files.
   The Annals ZIP has 123 entries because 18 entries are directories.
   All five inherited checksum manifests passed. All 598 recovered files
   were unchanged between the beginning and end of this run.

These counts measure different things. They must not be added together as a
theorem total or advertised as a universal proof.

Inherited evidence, not freshly rerun:

- Lean v4.34.0-rc2 build/axiom audit of the core's 225 targets and 827 namespace
  declarations. The original raw transcript and sentinel are preserved.
- The 33 current companion pytest tests and 27 historical Annals-package tests.
- The visual appendix's 181 exact SymPy checks and seven invalid controls.
- The generation of the 24 editable TikZ visual plates.
- The combined VERIFY_PAPER.py release gate.

Lean/lake, pytest and SymPy were unavailable. No installation was attempted and
no replacement library, synthetic compiler result or substitute pytest collector
was used. NumPy 2.3.5, SciPy 1.17.0 and Matplotlib 3.10.8 were available.

The 20-result Lean correspondence applies to the reviewed complete-release core.
It does not extend automatically to the 63-proof Annals extension incorporated
in the final traditional volume.

Evidence files:

- run/CURRENT_VERIFICATION.json: calibrated fresh/inherited/unrun status.
- run/manifest.json: bounded-run version 2 provenance with 601 pinned input
  artifacts, input hashes before/after, logs, result hashes and resource limits.
- COMPUTATION_CONTRACT.json: original execution contract and finite ranges.
- ADDITIONAL_RUN_METADATA.json: explicit seed metadata for the figure generator
  discovered in the pinned source during the post-run review.
- IMPLEMENTATION_REVIEW.txt: interpretation, checks and remaining limitations.
- run/*_results.json and run/*_tests.log: exact-suite results and raw logs.
- run/numerical/: freshly generated data, tables and 18 figure pairs.
- run/annals_verification.log: all thirteen Annals group results.
- run/ORIGINAL_SOURCE_HASHES.json: all 598 immutable recovered source files.

Portable reproduction, from the final package root:

python3 -B verification/scripts/verify_available.py --source source --downloads downloads --out verification/reproduced

Use a fresh output directory. The script copies source files to a temporary
directory, runs only the scoped checks, and saves all results to the chosen
output directory. Exact suites use the Python standard library. NumPy, SciPy
and Matplotlib enable the numerical replay. No network access is required.

The original published instructions remain in the immutable source trees for
machines with the complete pinned Lean/Python environment. This portable subset
runner is not a substitute for the original complete release command.
