# AVOC v0.23.0 — exact proof and implementation boundary

## Kernel-checked in this block

- Fixed-authority candidate promotion binds parent, revision, core, objective and
  contract check, and requires certified lower/upper utility separation.
- Promoted utility strictly improves by at least the switching tariff plus margin.
- Funded rejected trials retain their full evaluation tariff. Unfunded trials do not run.
- Contract validity, credit limits and cumulative gain/cost relations survive finite
  and adaptive incumbent-dependent candidate sequences.
- Trace charges equal the sum of their debit records; net endpoint gain is at least
  cumulative promotion margins minus ALL funded search tariffs.
- Stale promoted requests cannot promote again. Wrong authority/objective or a
  rejected contract cannot promote.
- A real existing algorithm admits an action-only threshold specialization with
  identical decisions under NoRevival and nonincreasing counted state visits.
- An incorrect cheap candidate is refuted. Exact successful and net-loss campaign
  witnesses are checked, including reachability of the costly search ledger.
- The executed Lean campaign state carries its contract and budget proof; selecting
  the final component yields the reference decision throughout the stated scope.

## Essential assumptions and non-claims

1. Authority is fixed during a campaign. Semantic contract, valid utility bounds,
   objective/workload/unit convention and prices are input obligations. Numerical
   inequality checks do not authenticate empirical confidence intervals.
2. The concrete executable uses three immutable compiled versions. It cannot admit
   arbitrary Lean/Python code, prove arbitrary program equivalence, or modify itself.
3. The inherited retry specialization theorem is reused, not claimed as a new
   discovery here. Only the action is preserved; exact value reporting is NOT.
4. NoRevival is indispensable. Repairs and improving-after-failure models can violate
   it. The live wrapper's demonstration model satisfies it by a checked proof.
5. Counted state visits omit rational bit complexity, model callbacks, compiler,
   parser, checker, startup, memory and actual time. Evaluation/switch charges are
   protected illustrative tariffs, not measured physical cost or calibrated value.
6. The fixed workload's exact cost is not held-out empirical evidence. Universal
   action correctness comes from the proof, not a passing benchmark.
7. Performance is not guaranteed profitable after failed trials. Net is an endpoint
   accounting objective, not total accumulated service reward during search.
8. The adaptive preservation theorem does not promise useful candidate generation,
   termination of unconstrained external search, or improving the improver itself.
9. The executable is a replayed in-memory campaign, not durable deployment. It neither
   edits the older research store nor integrates the new gate with its retry/recovery
   API. Client-supplied omission of past events is not solved by this evaluator.
10. Version identity is a compiled catalogue identity in the theorem. Source pins and
    .olean checks are protected-host engineering controls, not adversarial attestation
    or a proof of hash injectivity, serialization, runtime or filesystem correctness.
11. Re-evaluating a stale funded request charges it again; only its promotion is
    blocked. No idempotent authorization/payment claim is made for this new API.
12. All finite empirical/script regressions have stated bounded scope. No production
    LLM improvement, autonomous research gain, benchmark generalization, optimal
    physical cost or general recursive-self-improvement claim is made.
13. Older live artifact/crash/retry suites remain historical and are NOT reported as
    fresh executions for this block. Every local Lean target is freshly checked using
    pinned external caches; mathlib and the Lean kernel are not independently rebuilt.
