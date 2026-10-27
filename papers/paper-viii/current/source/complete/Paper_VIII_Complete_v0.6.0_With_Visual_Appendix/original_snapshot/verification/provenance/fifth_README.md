# PRSC VIII — Checked Fifth Block v0.5.0

**Author: Komorebi P.**

## Status

**55 of 56 named manuscript-proved items covered. One remains: theorem 5.6, small-core optimal recompression. Four classical inputs are tracked separately.**

This release adds **66 theorem declarations in seven modules**. The cumulative corpus has **313 declarations in 30 modules**, comprising 294 Paper VIII declarations and 19 in the unchanged reused Paper VII quantum-packet foundation. The 36 construction audits are separate from the theorem count. Supporting lemmas are included; these are not 313 independent mathematical discoveries.

All 30 modules passed a fresh cumulative Lean build with warnings treated as errors. Every theorem and construction audit matched the inventory. Both deliberately invalid controls were rejected. The 17 existing verifier tests and 12 new release-contract tests passed.

## New work

| Module | Manuscript items | Added theorem declarations |
|---|---|---:|
| GraphSchedules | 6.6 and 10.3: constructed levels, actual longest paths, pointwise earliest schedule and optimal depth | 17 |
| TriangularSolve | 6.5: actual forward substitution, uniqueness, independent stage evaluator and completion at optimal depth | 7 |
| InverseSupport | 6.7: actual reachable submodule, finite-dimensional inverse invariance and matrix-inverse support | 9 |
| SchurSupport | 6.8: rectangular block expansion and hidden-route support certificate | 4 |
| BandedCount | 4.1: actual band-address cardinality, scalar storage and declared operation-event counts | 9 |
| DiscoveryCertificate | 9.2: arbitrary orthogonal projectors, exact Frobenius residual and Euclidean operator-norm bound | 8 |
| BlockJacobi | 7.4 and 7.6: actual inverse square root, condition-number bound and classical-CG factor substitution | 12 |

Read `notes/Paper_VIII_Fifth_Lean_Block_Supplement.pdf` for the new proofs and conventions. The original manuscript and all four earlier supplements are preserved. The machine-readable crosswalk is `verification/coverage_ledger.json`; its readable counterpart is `notes/COVERAGE_LEDGER.md`. All 23 upstream proof sources remain byte-identical.

## Reproduction

Use the separately supplied Linux x86-64/WSL portable **Lean 4.34.0-rc2** kit with Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The large runtime is not duplicated in this source archive. Python 3.10 or later is required. Run these commands from the extracted release root:

```bash
python3 scripts/verify_integrity.py
python3 scripts/test_verifier.py
python3 scripts/test_fifth_release.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out verification/recheck --timeout 240
python3 scripts/run_fifth_regressions.py
```

The final command also needs NumPy. Its exact tests use standard-library rational arithmetic; the numerical tests are explicitly separated. It saves results to a newly timestamped directory. An explicit `--out /path/to/SUMMARY.json` is supported; replacing an existing report requires `--overwrite`.

The Lean verifier accepts `--max-checks 2 --resume` with the same output directory when a host imposes short orchestration limits. A partial checkpoint is not a pass. It uses one Lean worker, checks toolchain/dependency pins, and does not weaken kernel checking. No compiled local interfaces are included in this archive; they are regenerated in a fresh output directory. Mathlib's supplied cache is reused rather than independently rebuilt.

To rebuild the mathematical supplement with a TeX installation, run `pdflatex` twice on `notes/Paper_VIII_Fifth_Lean_Block_Supplement.tex` from a temporary output directory. The original manuscript is not rewritten by this supplement.

## Current evidence

- **Cumulative kernel build:** `verification/fifth_final/SUMMARY.json` and its per-module logs. All 313 theorem audits and 36 construction audits match. Allowed dependencies are `propext`, `Classical.choice`, and `Quot.sound`, or subsets thereof. Both false-equality and admitted-proof controls are rejected.
- **Independent baseline:** `verification/fifth_baseline/SUMMARY.json` records a fresh check of the prior 23 modules and 247 declarations before the new work. The corresponding prior verifier/inventory are preserved in `verification/prior_block4_metadata/`.
- **Regression infrastructure:** `verification/fifth_verifier_regressions.log` (17 passed) and `verification/fifth_release_regressions.log` (12 passed).
- **Finite mirrors:** `verification/fifth_examples/SUMMARY.json`, explicitly not executions of the compiled Lean definitions. Exact cases: 820 band counts, 200 DAG/staged solves, 60 inverse-support, 50 Schur-support, and 72 non-coordinate projector systems. Within the DAG cases, 125 also enumerate all possible schedules on at most four vertices. Eight cyclic graphs are rejected. There are 64 additional complex numerical projector cases and 120 positive-matrix normalization/factor cases.
- **Preservation and provenance:** `verification/fifth_preservation.json`, `verification/provenance.json`, and the input archive SHA-256. The existing recovery log is retained as `verification/fifth_runtime_recovery.log`.
- **Development record:** `verification/development_fifth/` and `verification/fifth_development_summary.json`. Ten of seventeen captured development checks failed before correction; seven accepted drafts correspond to the seven modules. Failed drafts remain inactive. The later clean cumulative build is the current verification result.

Prior reports under `verification/fourth_final/`, `verification/final/`, and `verification/prior/` are historical, not current. The coverage ledger's cumulative fourth-block total was correct, but its `newly_checked_items` and `new_theorem_declarations` fields had stale older-increment data. These fields are corrected in this release and tested. The old metadata is retained rather than silently destroyed.

## Formal scope

**Scheduling.** Acyclicity is the input; levels are constructed by well-founded recursion from strict ancestor-cardinality decrease. The schedule is pointwise earliest, and a longest path attains its makespan. Empty graphs have zero stages. Unit task duration, positive integer stage labels and unlimited concurrency are the model. This does not solve weighted or resource-constrained scheduling or certify GPU execution.

**Triangular solve.** The actual block action, recursive solution and independent stage evaluator are defined in dependent block spaces, allowing unequal dimensions. Diagonal blocks are genuine invertible linear maps. The proof does not assume a solution or the desired solve equation. Exact arithmetic is used, not a floating-point solve model.

**Inverse/Schur support.** The reachable subspace is defined from actual nonzero packet blocks. Finite-dimensional invariance gives inverse invariance. Reachability includes zero-length paths; Schur elimination requires an invertible hidden block. Support is only included in the permitted route graph: cancellation may remove a permitted edge.

**Banded count.** The actual finite address set is counted under `w < p`. To substitute the manuscript's `p = n/b`, positive `b` and exact divisibility are required. Storage and arithmetic are cardinalities of declared scalar-address and multiply/accumulate event types. They are not instrumented instruction traces.

**Discovery residual.** Orthogonal projectors may be non-coordinate and complex. Frobenius and Euclidean operator norms are instantiated separately. The certificate evaluates a supplied packet decomposition, not an algorithm that discovers useful or optimal projectors.

**Jacobi and CG.** The normalization uses the actual inverse of the positive matrix square root. Both `D` and `D+K` are positive definite on a nonempty finite complex space. The condition number is `||B||_2 ||B^{-1}||_2`. Item 7.6 proves the factor comparison and propagation of an explicit classical energy-error estimate. It does not prove the CG algorithm theorem (classical input 7.5). The source does not add that theorem as a project axiom.

## Remaining work and boundaries

**Theorem 5.6 remains:** derive and verify small-core optimal recompression, with the compact-factor construction and spectral/Frobenius approximation statement. The four external inputs remain independently tracked: Eckart–Young–Mirsky (5.5), CG convergence (7.5), floating-point matrix product model (8.2), and simultaneous spectral decomposition (9.1).

This block did not rerun the original numerical experiment corpus, CPU/GPU benchmarks, earlier compiler execution suites, or Papers I–VII in full. It did not independently rebuild or recheck imported Mathlib proofs. Historical performance observations are not presented as newly measured results. Manuscript-to-formal correspondence is a recorded mathematical review, not an automated semantic-equivalence theorem.
