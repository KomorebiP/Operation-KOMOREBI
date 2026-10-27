# AVOC v0.15.0 — update to the serious-audit gap ledger

This is a focused update, not a completion percentage. The previous ledger is preserved under `provenance/`.

## G17: posterior/model error to feasible Bellman-Q error
**CLOSED FOR THE DECLARED COMPATIBILITY CLASS.**

The primitive-to-continuation-to-Q-to-whole-policy chain now kernel-checks. It requires exact feasibility/metadata transport, bounded belief-Lipschitz approximate continuation tables, valid model backup residuals, and quantified prior/channel/codec/reward errors. Mean posterior bounds require no evidence floor. These hypotheses cannot be discarded for arbitrary discontinuous models.

Main declarations: `expected_posterior_l1_of_primitive_bounds`, `bayesian_link_expectation_error`, `bayesian_primitive_q_error`, `certified_bayesian_model_policy`.

## G16: guarded approximation/history/replay adapters
**APPROXIMATION ADAPTER CLOSED; HISTORY/PROVENANCE ADAPTERS STILL OPEN.**

The new ModelCertificate explicitly transports state-dependent feasibility and expected continuation to the guarded controller. This does not port every archival replay or certified-history theorem to the enlarged protocol.

## G18: exact candidate-to-receipt/semantic identity binding
**UNCHANGED, OPEN IMPLEMENTATION AND PROOF-INTERFACE GAP.**

Pending entries in the inherited protocol still identify tasks, not immutable candidate bytes bound to the exact statement, dependencies and proof environment. The next practical block should model and implement this binding with explicit trusted boundaries.

## G20: costed computation of controller/context
**PARTLY BETTER SPECIFIED, NOT CLOSED.**

Value tables may now be approximate, with explicit backup and Q reconstruction residuals. Bounded linear-row tables provide a certified regularity class. No efficient general planner or global residual checker was delivered, and computation/context-construction cost still needs an explicit model.

## G21: real-system identification/effectiveness
**UNCHANGED, OPEN EMPIRICAL GAP.**

No real model probabilities, costs, error rates or productivity gains are inferred from these theorems or the exact finite regression.

## Other audit entries

Existing closed release and audit-corollary entries remain as recorded. Decision-only minimum-code optimization, full certification/provenance replay, integration of fallible empirical evidence, richer artifact investment, dynamic tasks, concurrency and optional broader-horizon theories remain outside this block. The existing safe controller is not reclassified as missing.
