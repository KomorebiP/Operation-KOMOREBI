# AVOC probability calibration continuation

Base checkpoint: AVOC_Formal_v0.38.0.zip, SHA-256
`a54dac36e77636ffd974e849a653995daea78091214921042c5f273b5a8cc6c4`.
The original archive is immutable. Its 13,389 payload hashes and ZIP CRC passed.

## Target contract

Derive reproducible rational probability bands from duplicate-free checked binary
outcomes under a stated stationary binomial count model. Prove finite-sample
coverage, simultaneous finite-checkpoint coverage, and selection from that fixed
schedule. Replace probability bands only before a fresh planning episode and
compose their membership with the existing fixed-model whole-policy theorem.

Coverage is a probability statement over repeated samples. It is not certainty
about an observed interval, an empirical proof of the sampling model, or a
posterior probability. Quote identities, deterministic bands, selected-only
artifact semantics, and durable intent identity remain protected.

A closed release requires checked Lean, exact-name axiom audit, substantive
negative tests, independent rational executable comparison, baseline source
identity verification, and final payload/ZIP checks. Historical build logs are
not fresh evidence. This working note is not a release-completion claim.

## Routes and choices

- Exact binomial cell envelopes: chosen. A rational grid envelope contains the
  binomial likelihood throughout its cell. Excluding a parameter implies its
  observed count mass is at most alpha/(n+1); summing all counts proves coverage.
- Moment/Chebyshev bands: viable but not used. Their moment development adds
  machinery and yields conservative widths.
- Direct probability-endpoint substitution in Bellman expectations: not used.
  The existing reward/law error propagation remains the planning theorem.

## Execution boundaries

The schedule, grid, and per-checkpoint error allowances are fixed before the
outcomes used by them. All checkpoints and both identities share one total error
budget. No cross-checkpoint independence is needed by the union bound. A
binomial marginal law is required at every scheduled count; adaptive arm
selection alone does not establish this law. Excluding infrastructure faults
requires an explicit noninformative observation assumption. Unresolved intents
block quote refresh. Bands remain fixed during each planning episode.

## Ownership

FiniteCalibration.lean: calibration_math agent.
CalibrationSchedule.lean: simultaneous_coverage agent.
CalibrationBridge.lean and source-boundary audit: core_audit agent.
CalibrationLog.lean, Lean CLI, release integration: root.
Python exact statistics/log adapter and bounded regression: calibration_exec agent.
Pinned environment and fresh predecessor build: runtime_recovery agent.
All work starts from the exact archive above and has disjoint source ownership.
