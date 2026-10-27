# Paper VIII fifth-block report

**Author: Komorebi P.**  
**Release: v0.5.0, September 6, 2026**

## Result

Nine additional manuscript-proved items are covered by newly checked Lean sources. The register advances from 46/56 to **55/56**. The release adds **66 theorem declarations** and has **313 declarations in 30 modules**. This includes 19 declarations in the unchanged reused foundation from Paper VII and 294 Paper VIII declarations. Supporting lemmas are counted, not independent mathematical discoveries. Construction audit targets (36) are a separate census.

The completed items are 4.1, 6.5, 6.6, 6.7, 6.8, 7.4, 7.6, 9.2 and 10.3. The seven new modules construct the band-address counts, actual level schedule and triangular solve, reachable subspaces and inverse/Schur support, non-coordinate projector residual identities, and the actual inverse-square-root condition bound with the CG factor comparison.

## Fresh checks

The prior 23-module corpus was first rebuilt and accepted independently. The final cumulative run compiled all 30 active modules in a fresh output directory under Lean 4.34.0-rc2 with pinned Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All compiler exit codes were zero with warnings treated as errors. Every axiom audit matched the declaration inventory and used only propext, Classical.choice and Quot.sound, or a subset. Both invalid-proof controls were rejected.

All 17 existing verifier tests and 12 additional release-contract tests passed. All 23 upstream proof sources and all original manuscript assets remain byte-identical. The final eight-page supplement compiled without warnings or overfull/underfull boxes; all pages were rendered and reviewed.

The exact independent regression mirrors passed 820 band cases, 200 DAG/staged solve cases, 60 inverse support cases, 50 Schur cases and 72 non-coordinate projector cases. There were 125 exhaustive schedule searches among the DAG cases, eight cyclic-graph rejections, 390 absent inverse-route checks, 97 absent Schur-route checks, and a cancellation control. Numerical checks were separated: 64 complex projector cases and 120 positive-matrix normalization and factor cases. No regression mirror is reported as execution of the compiled Lean definitions.

## Failures and corrections retained

Ten of seventeen captured development runs failed before correction. Seven accepted development drafts were followed by the independent successful cumulative run. The failed source snapshots and diagnostics remain in verification/development_fifth; they are not active proofs.

Two stale increment fields in the inherited fourth-block coverage ledger were corrected. Its cumulative 46/56 count was correct, but the list of newly checked items and increment size still described an older block. The original metadata is preserved and the new release tests cross-check current counts and targets.

Formal conventions made explicit include empty-graph depth zero, reflexive reachability, positive/divisible block-width substitution, nonempty spaces for the condition-number convention, and the distinction between Frobenius and Euclidean operator norms. The supplied projector certificate is not autonomous discovery. Unit-task/unlimited-concurrency scheduling is not weighted or hardware-constrained scheduling.

## What remains

**Manuscript theorem 5.6, small-core optimal recompression, remains unformalized.** Four classical inputs remain separately tracked: Eckart–Young–Mirsky, preconditioned CG convergence, the floating-point product model and simultaneous spectral decomposition. The new item 7.6 proof propagates an explicit classical error estimate; it does not reprove the CG algorithm theorem or add it as a project axiom.

The original numerical experiment corpus, GPU measurements, earlier compiler execution suites and Papers I–VII in full were not rerun. Mathlib's pinned cache was reused, not independently rebuilt. Prose-to-formal correspondence remains a mathematical review rather than an automated semantic-equivalence theorem.

## Evidence paths

Current kernel report: verification/fifth_final/SUMMARY.json.  
Finite mirrors: verification/fifth_examples/SUMMARY.json.  
Preservation: verification/fifth_preservation.json.  
Development history: verification/fifth_development_summary.json.  
Coverage: verification/coverage_ledger.json and notes/COVERAGE_LEDGER.md.  
Proof explanations: notes/Paper_VIII_Fifth_Lean_Block_Supplement.pdf.
