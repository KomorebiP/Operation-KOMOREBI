# AVOC v0.24.0 — exact proof and live-store boundary

## Kernel-checked

- Prepaid evaluation-state safety, without switching the active component.
- Two-phase settlement exactly refines the inherited funded upgrade step.
- Finish never debits the reserved evaluation a second time.
- Abandonment preserves the complete current ledger and refunds nothing.
- Generic command/replay safety, budget and endpoint net-bound preservation.
- Complete accepted traces have exact evaluation and switching debit sums.
- Active utility never decreases on a successful command or replay.
- Exact begin, finish and abandonment idempotence at the canonical ledger level.
- Closed-key request conflicts and stale complete pre-state rejection.
- Replayed journal matching, restoration safety and restoration idempotence.
- Certified runtime dispatch preserves the original action-only contract.
- Exact paid-rejection/promotion, abandoned-reservation, omitted-history and forged
  checkpoint witnesses in the positive library.

## Actual implementation, tested rather than universally proved

The Python wrapper executes the very Lean runtime defined above. It obtains the
canonical command history and materialized journal from a protected SQLite store.
A single transaction writes each command, journal and active dispatch pointer.
Keys are unique in the campaign and bind an exact request plus expected event epoch.
Every access checks frozen authority/source/build/runtime descriptors. Invoke
executes the retained compiled strategy after replay validation.

## Assumptions and exclusions

1. The authority's sound checker and utility bounds remain proof obligations. The
   concrete authority is the old immutable three-version catalogue, not arbitrary
   Lean/Python/plugin source or learned confidence intervals.
2. One pending evaluation and one cooperative local writer. No live modification of
   the frozen checker, objective, tariffs or candidate catalogue is supported.
3. The new database is separate from all previous AVOC run formats. No migration or
   automatic replacement of the existing proof-research database occurs.
4. Deployment means persistent dispatch among already compiled components. No
   arbitrary file installation, executable rewriting or autonomous proposer is added.
5. Evaluation credit is reserved before a NEW candidate gate evaluation. On restart,
   replay may recompute old pure checks and finish may reexecute interrupted pure
   evaluation. Such computation is not covered by an exactly-once work claim.
6. Idempotence covers ledger, active version and nominal charges. Diagnostics and
   read/replay/environment work may change or cost time on repeated requests.
7. SQLite atomic commit, storage flushing, Python/JSON projection, source descriptors,
   Lean compiler/kernel/runtime and the pinned external cache remain trusted. No
   universal Python/SQL refinement, independent kernel or power-loss proof is given.
8. Store integrity is protected-host trust, not cryptographic history attestation.
   Replacing BOTH canonical log and checkpoint consistently, hostile rollback,
   malicious hosts and noncooperative writers are outside scope. Ordinary omission
   or checkpoint divergence is detected under the checked correspondence contract.
9. A valid active component does not make a campaign profitable. All authorized
   trials, including abandonment, remain charged. Costs are illustrative tariffs,
   not full physical metareasoning costs or wall-clock speedups.
10. The runtime caps event history and numeric fields. It does not guarantee
    efficient long-running replay, infinite liveness or scale.
11. Process-exit tests cover named crash boundaries. They are not electrical power
    loss, arbitrary interleavings, storage corruption or adversarial filesystem tests.
12. Earlier artifact/crash/retry test suites remain historical. This block runs its
    own promotion-store tests and checks all local mathematical modules. External
    mathlib caches are retained, not rebuilt from their full source.
