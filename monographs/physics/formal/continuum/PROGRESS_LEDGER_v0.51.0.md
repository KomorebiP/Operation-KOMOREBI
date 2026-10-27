# Komorebi Physics progress ledger

Version: **0.51.0**. Checkpoint: **PHYS-CENT-51**.
Accepted gate finished: **2026-10-26T15:23:13.796108+00:00**.
Predecessor: the checked strong-generator frontier `v0.50.0-g1`, layered over
the preserved Block 49 source archive.

## Completed and accepted

- Four new mathematical modules, with 74 named theorems, 15 definitions and
  11 abbreviations. The actual gate audited 162 compiled constants
  owned by those modules, including generated helpers.
- Bounded self-adjoint centered operators for nonzero real spacing, exact
  modal difference norms, and two-sided full graph-domain convergence.
- Genuine continuum and centered resolvents for every nonreal parameter,
  actual domain and inverse laws, resolvent error bounds and strong limits.
- Third-order-moment generator and propagator rates with coefficient `1/6`,
  all real times and explicit compact-time hypotheses.
- Physical torus transport of operators, resolvents, convergence and rates.
- The unchanged generator source and all 912 recorded inherited Lean inputs
  retain their exact predecessor bytes.

## Fresh verification

The passing [receipt](verification/block51/current/receipt.json) is bound by
SHA-256 `f530e4bb0c55204fe3d7d55c9cf71c60781f5db949541bfc9b3c649241799d11`. It records 26 local compilation
targets, 64 commands, and 21 controls:
8 positive, 12 elaboration rejection,
and 1 axiom-policy rejection. Five root modules received
actual kernel replay in the imported pinned environment. The audit covers
209 environment constants across those roots, including the
preserved generator module's 47 constants. Its 37 named
theorems and 2 definitions are not newly added results.

The [independent source review](verification/block51/provenance/FROZEN_SOURCE_REVIEW.json)
examined the exact frozen source. Agreement is review evidence, not a substitute
for the compiler and kernel records. The external proof cache is pinned and
reused, not rebuilt from source. This is not a second proof assistant or a
fresh audit of the entire historical corpus.

## Failures and corrections

1. The first predecessor build used an unsupported Lake `-j` option and
   failed before compilation. [Record](verification/block51/provenance/verification/baseline/attempt01/launch.json)
   and [log](verification/block51/provenance/verification/baseline/attempt01/build.log).
2. The next predecessor build failed when the filesystem filled during
   runtime restoration. It was not counted as a pass. Removing reproducible
   downloaded archives freed space and the next build completed.
   [Failure](verification/block51/provenance/verification/baseline/attempt02_disk_full/FAILURE.json)
   and [successful build log](verification/block51/provenance/verification/baseline/attempt03/build.log).
3. The original optional all-files runtime check failed on mutable dependency
   Git-index bytes. A complete scan found nine such differences and no other
   declared-row mismatch. The strict all-files failure remains recorded.
   The accepted gate explicitly excludes those mutable indexes while checking
   compiler, source and cache bytes at both endpoints.
   [Recovery record](verification/block51/provenance/runtime_recovery_receipt.json).
4. The first integrated centered gate stopped before executing compiler
   commands because the runner wrongly required a build directory for the
   unused source-only `Cli` dependency. The runner was corrected to record
   such directories and verify each actual direct external import against the
   pinned cache. [Failed receipt](verification/block51/provenance/verification/centered_run01/receipt.json).
5. Early proof/control drafts contained elaboration, coercion, namespace,
   arithmetic simplification and strict-lint errors. Corrected sources passed
   their later checks. The delivered development evidence preserves those
   attempts separately from the accepted fresh run.

## Remaining obligations

The abstract unbounded spectral-calculus API linkage remains outside this
certificate. Actual finite spatial grids require sampling, interpolation,
Nyquist and aliasing comparisons. Interacting gauge dynamics, the wider
historical evidence audit, whole-book specialist review, and the unresolved
cosmological production/state/matching problems remain separate work.

## Exact restart point

Read [CONTINUE_HERE.md](CONTINUE_HERE.md), the [proof guide](docs/BLOCK_51_PROOF_GUIDE.md),
and the four modules listed in the scoped inventory. Replay the current gate
before edits. Preserve the actual domain witnesses, all-nonreal parameter
scope, both-sided punctured limits, third-order summability, `abs(t)` and
`T ≥ 0`. Do not turn the auxiliary zero-spacing bounded map into the unbounded
continuum operator by notation alone.
