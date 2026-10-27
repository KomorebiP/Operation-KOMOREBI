# AVOC v0.22.0 — exact proof and runtime boundary

## Proved in this block

- Executable single-operation retry recurrence equals a separately instantiated
  state-dependent Guarded Bellman system.
- The executable selected deterministic adaptive plan is legal, attains that
  finite-horizon value, and dominates all legal deterministic adaptive plans.
- NoRevival implies an exact pG>c retry threshold, with tie-breaking to abandon.
- A weighted variance proof derives decreasing predictive resolve probability
  after faults in a fixed finite latent-reliability model.
- The Bayesian model therefore satisfies NoRevival for fixed nonnegative benefit
  and fixed nonnegative integer fee.
- Remaining credit and attempt slots guard retry and are consumed exactly.
- Existing ledger room/renew conditions match the derived resource guard; accepted
  advice preserves safety, charges afresh, retains confirmed fees, fences the old
  ticket and preserves the inherited scientific checkpoint.
- The executed dynamic evaluator agrees with the specification and visits at most
  horizon+1 states; the threshold action agrees with that evaluator.
- Successful explicitly requested operational-fault updating leaves the supplied
  attempt ledger unchanged.
- Checked persistent versus i.i.d. examples and a counterexample to a universal
  greedy retry rule.

## Assumptions and non-claims

1. Single unresolved operation; fixed latent operational types; conditionally i.i.d.
   binary resolve/fault observations within a type; fixed fee and fixed benefit.
2. No repair/backoff/provider alternatives, improving service, arbitrary dependence,
   variable fee/benefit, or non-binary fault-information policies are covered by the
   threshold specialization. The more general recurrence does not need NoRevival.
3. Resolution means completion of this operational subproblem, not correctness of
   a proof or successful artifact admission. The existing sound monitor remains
   required before any scientific update.
4. Reliability parameters and resolution benefit are declared model data, not
   calibrated measurements. A fault may carry scientific information under a
   different joint model; no universal irrelevance result is claimed.
5. The advice assumes the supplied ledger describes the current authoritative
   attempt. A missing commit or timeout is not automatically classified as the
   modeled fault. The advisor is read-only and does not authorize any retry.
6. Previous sunk attempt charges are retained and influence remaining resources.
   The objective is incremental future value, not historical total return.
7. Optimality is for deterministic finite-horizon adaptive plans in this model.
   No universal physical-cost or full research-project optimality is asserted.
8. The meter counts evaluator visits only, not rational arithmetic bit complexity,
   likelihood evaluation, environment capture, parser, checker, SQL, or host time.
9. The wrapper is tested, not formally refined. Lean/Std/mathlib runtime, cached
   dependencies, Python and the host remain trusted.
10. Existing protected-store guarantees are inherited unchanged. The physical
    backend, arbitrary Lean/mathlib artifact support, multi-task live execution,
    crash-inclusive metareasoning and empirical usefulness remain separate gaps.
11. Reconciliation and explicit keyed retries retain v0.21 semantics. No old store
    migration, automatic fault inference, automatic retry, or new live recovery
    experiments are part of this release.

## Verification interpretation

The fresh build checks local source against the nine exact pinned dependency
caches, not a new source build of mathlib. The theorem census includes helper
lemmas and examples. Invalid proof-script rejection is secondary evidence; the
positive library separately proves the relevant counterexamples. See the current
verification report for final counts and the bounded independent test range.
