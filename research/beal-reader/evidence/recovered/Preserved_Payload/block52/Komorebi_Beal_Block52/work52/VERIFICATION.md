# Verification contract

## Domains, ranges and exclusions

All new computation is exact: integer arithmetic, F_q, explicit quadratic
extensions F_q^2, and Z[phi] with phi^2=phi+1. No floating-point comparison,
random sample, OCR result, numerical optimizer or timeout supplies a
load-bearing conclusion.

`finite_frobenius.py` covers q=13,29,43,71. It partitions all7744 smooth
parameter pairs into164 weighted curve orbits, tests admissibility separately
for every member, and records the complete1240-member good equation set.
It counts each representative over F_q and F_q^2 using a norm character.

`independent_pointcounts.py` directly enumerates all1240 admissible pairs,
checks a polynomial gcd for smoothness at every pair, and obtains the same
N1,N2 and Pq using explicit square-root tables in an independently chosen
quadratic-field model. It verifies the twist through the defining radicand,
squares Frobenius with Newton identities, and agrees on every order and
residual decision. It imports no code from the first implementation or
from a predecessor.

`kummer_and_matrix_checks.py` checks the good13 unit symbol by exponentiation
and by enumerating all168 nonzero field elements' seventh powers. It checks
five local coefficient functionals, five sample inert-minus symbol pairs,
the two historical ray-prime places,2500 integral matrix cases, all48
nonzero projective ratio candidates after good13, and the declared negative
controls. The uniform matrix, unit, and cohomology consequences are supplied
by separate written proofs, not by extrapolation from these finite tests.

## Provenance and runner

The original Block51 archive has SHA256
`2db43f22efa22e5e21ee2359eb132d4744a18c60dda39792f57f12a3385c5fd6`.
The startup Block51 replay passed its own result plus six selected prior
jobs. That raw record is preserved as `verification/STARTUP_BLOCK51_REPLAY.json`.
The final top-level run is recorded outside the package with actual commands,
return codes, stdout/stderr, timings, environment and before/after hashes.

The portable verifier executes in temporary copies, removes old result
files before every new computation, and compares fresh JSON against pinned
fixtures. The independent implementation is passed the fresh output of the
first implementation, not a stale result. Input hashes and the package
manifest are checked before and after. Nested predecessors are retained
byte for byte and their own manifests are checked by their own verifier.

A failure exits nonzero. A timeout is marked INCONCLUSIVE_TIMEOUT; it is not
counted as a pass or mathematical contradiction. The final run is considered
successful only after its report explicitly says PASS_DECLARED_CHECKS.

## Review status

The mathematical notes received an adversarial SELF-REVIEW, recorded in
notes/SELF_REVIEW.md. The point-count algorithm is independently implemented,
but there was no second human/agent mathematical reviewer. Block50's
interrupted extension-geometry review is not silently reclassified.

No new Lean compilation was attempted. No literature-wide novelty claim is
made. Checksums prove byte integrity, not the truth of a theorem.
