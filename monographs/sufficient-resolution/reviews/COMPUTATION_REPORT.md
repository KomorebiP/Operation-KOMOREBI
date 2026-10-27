# Sufficient Resolution final-edition computation review

The v0.16.0 mathematical source was preserved, while the publication copy's
verification runner and metadata were repaired. This review distinguishes
fresh finite computation, current source checks, inherited proof verification,
and the unavailable proof runtime.

## Fresh finite result

All sixteen unchanged companion suites passed. Fifteen report native counters
totaling **40,466 assertions**. The remaining script checks five fixed sanity
groups with six main mathematical `assert` statements. Explicitly reported
rejected controls total **1,073**; additional mathematical obstruction controls
are included in the assertion counters. Counts are overlapping implementation
checks and are not independent discoveries or universal proofs.

| Suite | Native assertions | Reported rejected controls | Principal finite range |
|---|---:|---:|---|
| Approximate bounds | 7,509 | 10 | 30 systems; dimensions 0..4/0..3/0..2; words through length 4 |
| Calibration | 289 | 6 | 72 systems; source 1..3; calibration source..source+2 |
| Continuous approximation | 3,060 | 15 | 32 systems; dimensions 0..3; Taylor order 8 |
| Continuous memory | 2,127 | 15 | 32 systems; visible/hidden dimensions 0..3; Taylor order 8 |
| Discrepancy | 631 | 72 | 75 systems; source/target dimensions 0..4 |
| Discrete memory | 1,307 | Separate explicit cases | 20 systems; evolution depth 9; hidden dimensions 0..3 |
| Fixed examples | Five groups, six main asserts | Included in groups | Delayed return, defects, coherence, two-stage and redundant resolution |
| Generalized discrepancy | 752 | 32 zero-model parameters within assertions | 120 scalar systems; sampled zero-model parameters k/8, k=1..32 |
| Hilbert globalization | 5,729 | 37 | 42 systems; dimensions 0..6; 100 independent PSD comparisons |
| Inexact discrepancy | 783 | 315 | 75 systems; source/target dimensions 0..4 |
| Observable model | 1,657 | 10 | 30 systems; fine dimension 0..6; words through depth 4 |
| Operator uncertainty | 956 | 344 | 75 systems; source/target dimensions 0..4 |
| Quotient metric | 3,065 | 21 | 30 systems; ambient dimension 0..5 |
| Reconstruction | 4,828 | 58 | 49 systems; source/target dimensions 0..6 |
| Regularization limits | 920 | 64 | 100 systems; source/target dimensions 0..4 |
| Tikhonov | 6,853 | 106 | 108 systems; source/target dimensions 0..5; lambda=1/4,1,4 |

Each run has a bounded version-2 manifest, native JSON stdout, normalized
scientific result, exact input/output hashes, UTC start, runtime, environment,
seed and explicit mathematical non-claims. All sixteen manifests passed
schema and live hash validation. Tests ran in isolated copies of script
dependencies and input examples. Inherited example outputs were not copied
into these trees as fresh evidence. An initial successful baseline was
superseded after finalizing driver source accounting; only final runs count in
the current summary.

## What the checks mean

Arithmetic is exact rational over known finite matrices. Word orientation and
matrix composition are preserved. Zero-dimensional and rank-deficient cases,
delayed hidden return, prepared versus arbitrary hidden state, incomplete
certificates, noncommuting words, malformed inputs, wrong norms, inadequate
allowances, search caps and nonspanning calibration are represented by the
stated suites. Resource exhaustion rejects rather than issuing a success
certificate in the tested selectors.

Several checks use an orthogonal implementation route: sparse observable
closure is compared with all-word observation tables and separate forward
elimination; hidden-memory integrals are compared through independently
expanded monomial antiderivatives; Hilbert PSD checking is compared with all
principal minors in dimensions 0..4; pseudoinverses use 49 rank-factorization
comparisons and 16 exact SymPy comparisons; Tikhonov and uncertain/inexact
solves include separate exact SymPy comparisons. Quotient metrics compare
ambient projection with compatible-basis minimization using the actual Gram
matrix. Some other comparisons share matrix helpers, so the complete
implementation is not independently certified.

Approximate finite bounds use the induced infinity norm. Calibration uses
conservative entrywise l1 bounds. Euclidean reconstruction/discrepancy tests use
exact squared norms and PSD checks. These conventions differ where explicitly
stated from generic native operator norms in Lean. Taylor-coefficient checks
do not certify whole exponentials, unbounded generators or infinite-time
limits. Finite schedule examples do not prove convergence limits. Random
matrices with fixed seeds are reproducible rather than exhaustive.

Classification: **bounded outputs reproduced, with selected source contracts
and invariants reviewed; not complete independent implementation validation or
formal verification of Python**. The uniform results rely on the actual Lean
proofs and their displayed hypotheses. No source-bound, operator-error,
calibration-truth or statistical guarantee is inferred from fitting alone.

## Driver and source repair

All 93 production Lean files retain their original SHA-256 hashes. The previous
generic driver explicitly listed only 81 modules while the root imported 93.
The current driver discovers every production module, checks project import
references, rejects cycles, and compiles dependencies before dependents. It
checks the exact Lean commit, records the complete executed source/script/input
closure, audits all registered names, adds current Block 15/16 companions, and
reports completed compilation/replay counts rather than planned work as if it
had passed.

A separate source-only run checked all 93 preservation hashes and all 118
production import edges. Missing-dependency and cycle fixtures were rejected.
The portable shell entrypoint passed syntax checking and rejected a missing
runtime before attempting Lean. This seventeenth version-2 record also passed
schema and hash validation. These checks authenticate the source/driver plan,
not the proof terms.

Original top-level metadata is preserved under `formal/inherited_provenance`.
The old `AUDIT.json` described v0.15.0 and the old runtime metadata retained
Block 13 wording. Current metadata reports the v0.16.0 inventory, current
finite results and explicit absence of fresh Lean verification. Historical
verification records remain associated with their original executed inputs.

## Inherited Lean coverage and unavailable runtime

The final inherited main and separate-tree v0.16.0 records each passed fresh
compilation of 31 project dependency modules plus block root, 52 new-name
transitive axiom audits and 31 same-kernel replays. The source match covers 69
executed inputs and predecessor preservation covers 87 files. False equality
and placeholder proofs were rejected. A deliberately introduced custom axiom
compiled and was then detected by the allowlist. The allowed axioms are
`propext`, `Classical.choice`, and `Quot.sound`. Imported pinned Mathlib compiled
artifacts were reused. These were neither full fresh 93-module runs nor an
independently implemented proof kernel.

No matching Lean runtime was available in the known workspace paths or PATH.
The five compact runtime pieces were resolved, but the first piece's canonical
materialization failed with HTTP 502. An independently prepared retry, bounded
at 60 seconds, also failed with HTTP 502. The remaining pieces cannot restore
the runtime without the first and were not downloaded. **No fresh Lean
compilation, transitive axiom audit or kernel replay was performed**. This is a
retrieval/environment limitation, not a failed mathematical proof.

The required environment is Lean 4.34.0-rc2 at commit
`6a10ac8c22beadecabdbb0919c2b50214762f91d`, Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`, and the pinned imported dependencies.
Portable commands are supplied in `formal/PORTABLE_REPLAY.md`; the runtime is
not included. Finite replay used Python 3.12.14 and private SymPy 1.14.0/mpmath
1.3.0 dependencies already restored from cached wheels. Each suite had 600
wall seconds, 500 CPU seconds per process, 1 GiB address space, one inherited
core, one cooperative numerical-library thread and 1 MiB outer log output.
All completed within those bounds; no partial test range was silently accepted.

The next discriminating proof-runtime check is the repaired full 93-module
compile/axiom/replay run once the exact runtime is restored. More finite
assertions alone do not replace that check or close sample-wise calibration,
statistical calibration, verified execution or general admissible realization.

## Current evidence

`verification/CURRENT_RELEASE_VERIFICATION.json` is the complete machine-readable
summary. `verification/python_replay` holds final bounded finite evidence.
`verification/runner_plan_check` holds source/driver evidence.
`verification/RUNTIME_RECOVERY.json` records the exact recovery failures.
`verification/MANIFEST_VALIDATION.json` records the seventeen successful
provenance validations.

The release root `AxiomAudit.lean` is regenerated from all **1,159** current
registry names. Source-only correspondence checks verify unique complete
coverage. The original 1,010-command wrapper is preserved under inherited
provenance. Regeneration is not a fresh transitive axiom audit.
