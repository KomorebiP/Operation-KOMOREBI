# Large Signal Model formal companion

87/87 complete proposition mappings, 0 partial and 0 unformalized.

This project formalizes the 87 propositions registered in the Large Signal Model monograph. Its statements cover realization and predictive closure, positive probability domains, observable reconstruction, adaptive record laws, conditional concentration, curved certificates and structured learning from dependent observations. Complete means that the registered statement has an explicit Lean correspondence under its stated hypotheses. It does not mean that empirical model assumptions were verified by data.

There are 254 mathematical modules, 4454 explicitly named declarations and 2887 named theorems. The theorem total includes 331 worked-example theorems. Compiler-generated declarations are outside the named-source count. The 183 rejection controls exercise invalid boundary claims and are excluded from the proof import graph.

## Read and check

1. Read `LEAN_GUIDE.md` for the main theorem families and retained assumptions.
2. Read `COVERAGE.md` for the complete proposition correspondence. `COVERAGE.json` binds each target to its exact source hash.
3. Inspect `verification/current/report.json` for the clean cumulative compile, axiom audit, kernel replay and rejection results. `CURRENT_STATUS.json` records delivery acceptance.
4. Restore the pinned portable Lean kit, then run `python3 scripts/verify.py --kit /absolute/path/to/kit --out verification/current`. The project uses the exact compiler and dependency revisions in `lean-toolchain` and `lake-manifest.json`. Exact certificate checks can take several minutes. The default per-stage limit is 900 seconds and can be set with `--timeout`.
5. Run `python3 scripts/check_metadata.py` to check register linkage, source inventories, inherited records and parser failure controls. `python3 scripts/test_source_scan.py` checks the comment-aware Lean lexical guard separately, and `python3 scripts/test_negative_control_classifier.py` checks control-diagnostic classification against captured failure cases.

A source checkpoint and an execution receipt are separate records. The current cumulative report is `verification/current/report.json`. A successful mathematical scope review does not by itself certify compilation.

All registered proposition mappings are complete. No remaining proposition obligation is recorded.

The frozen original manuscript and proof register are in `source/`. `source/FOUNDATIONS_REVIEWED.md` is the exact later mathematical body used by the current correspondence reviews, with its own preserved source hash. This archive is the Lean companion. The finalized monograph has its own publication artifact and its own visual review. Technical release metadata is retained for reproducibility.

## Accepted execution

The delivered execution is PASS: all 254 mathematical modules compile with warnings treated as errors and pass individual kernel replay. The complete root import, exact rational examples, all 4,454 named-declaration axiom checks and all 183 isolated rejection controls pass. The only permitted logical axioms are propext, Classical.choice and Quot.sound.
