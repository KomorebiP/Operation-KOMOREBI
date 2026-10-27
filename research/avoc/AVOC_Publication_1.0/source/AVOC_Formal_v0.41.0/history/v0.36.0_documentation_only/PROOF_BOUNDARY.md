# AVOC v0.36.0 — exact proof and execution boundary

## Kernel-checked in this block

1. Proof-carrying warm and cold staged options with declared probabilities in `[0,1]`.
2. Gross deployment savings are nonnegative, and setup fee plus later gross saving equals the inherited deployment payoff.
3. Cache inspection and cold generation are paid, fallible, nonterminal actions.
4. Warm/cold deployment actions are unavailable until the corresponding stage succeeds.
5. Exact executable realization of the state-dependent guarded Bellman system.
6. Executed finite-depth value equality and Bellman-optimal feasible action selection.
7. Exact common-envelope conservation on every allowed observation branch.
8. Existence of a budget-safe optimal deterministic adaptive finite-horizon plan.
9. Operational faults are not observations; unsupported or zero-probability reports are rejected.
10. Accepted reports preserve the budget and set the appropriate ready/failed status.
11. Ready warm/cold states expose exact semantic and no-worse-cost deployment proofs.
12. Halted states have zero continuation value.
13. Checked rank-one setup/gross/net and availability examples.

## Executed and independently tested

The Lean JSON entrypoint validates a retained warm record and a cold factor certificate,
constructs the typed staged model, replays supported report history, and invokes the actual
executable evaluator.  An independent exact-`Fraction` Python dynamic program checked 96
valid requests and eight invalid requests, including the six headline cases.

## Essential assumptions and non-claims

1. The runtime validates both candidate certificates while constructing the typed model.
   Logical setup charges are staged in the Bellman objective, but physical eager validation,
   parsing and process startup are not yet selected lazily by the controller.
2. Success probabilities are supplied exact model data.  They are not inferred from actual
   cache availability, generator reliability, production telemetry or LLM calibration.
3. A successful report means the declared proof-carrying deployment became available.  It
   does not prove that an arbitrary external process faithfully produced that report.
4. The formal controller is one fixed affine workload with warm/cold options.  It does not
   yet combine the v0.33 rank-probe catalogue and this staged operational state in one model.
5. Setup fees are natural-number accounting units; rewards are rational.  They are not a
   complete CPU, token, memory, energy or wall-time model.
6. The affine proof backend remains exact `ZMod 5` at runtime with inherited bounded parsing.
   No arbitrary Lean/mathlib artifact backend is added.
7. The executable wrapper is tested, not universally formally refined to the Lean JSON
   parser, compiler, OS or filesystem.
8. No persistent staged store, crash recovery, retry protocol or authenticated cache lookup
   is added here.
9. Finite-horizon exhaustive evaluation may scale exponentially.
10. No empirical LLM productivity or universally optimal AI-use claim is made.
11. The local build checks this project against exact pinned cached dependencies.  It is not
    an independent kernel implementation or source rebuild of all mathlib.
