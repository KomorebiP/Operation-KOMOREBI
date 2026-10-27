# AVOC v0.31.0 — failures and repairs

## Proof development (all repaired in final sources)

1. `dev_paidprobe_01.log`: Omega could not normalize the scan accounting expression
   involving `probeFee * (tested + 1)`. Explicit distributivity via Nat.mul_add and
   Nat.mul_one reduced it to the additive invariant.
2. The same attempt used `split at h ⊢`, which this Lean tactic does not support.
   It was replaced by explicit cases for the credit predicate and determinant check.
3. The unused-section-variable linter rejected DecidableEq R in purely algebraic
   corollaries. These declarations now explicitly omit that unused instance.
4. `dev_paidprobe_02.log`: a documentation comment before `omit` was parsed as an
   attached declaration comment at the wrong location. Moving `omit` before the
   documentation comment repaired the parser error.

Final AffineRankProbe, PaidRankProbe, AffineProbeCodec, examples, aggregate and
entrypoint sources compile with warnings as errors. No placeholder or custom
axiom was introduced to work around those failures.

## Environment

An initial interactive-session command was rejected by the container before it
started (`StreamingExecNotEnabledContainerError`). Runtime assembly was instead
launched as an ordinary logged subprocess, observed through completion. All seven
archive chunks and the combined hash passed. The tool failure is not a proof failure.

## Preserved negative outcomes (not bugs)

- Rank-one probing spends eight units and finds no stronger floor. The ensuing
  selected implementation is correct, but setup is eight units worse than bypass.
- A corner minor can vanish for a rank-two matrix. This is an explicit proof and
  runtime case, not permission to report low rank.
- A seven-unit allowance buys no eight-unit probe.
- Repeated probes consume budget unless an earlier successful witness stops scanning.
- Skipping a futile factor search still leaves the already paid preflight/probe cost.

The final differential suite and eight end-to-end tests passed on their recorded
source. No incomplete or timeout run was substituted for a pass. Current evidence
collector and complete negative suite passed. No physical speedup is claimed.
