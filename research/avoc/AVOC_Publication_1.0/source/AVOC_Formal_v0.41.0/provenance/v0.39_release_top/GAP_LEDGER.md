# AVOC v0.39.0 gap ledger

G30–G35 from v0.38 are retained with the precise qualifications in PROOF_BOUNDARY.md.

## G36: finite-sample evidence acquisition

CLOSED for the defined rational binomial count model: the implemented exact
cell-envelope interval has kernel-checked finite-sample coverage. Kernel-checked
nonvacuous examples and empirical-singleton counterexample are included.
Remaining: empirical validation of the count law, arbitrary real parameters,
sharper intervals, drift and dependent accepted outcomes.

## G37: selection-aware calibration

CLOSED for finite predeclared schedules with exact binomial marginals. Arbitrary
selection from that schedule inherits the summed budget. No checkpoint
independence is needed. Remaining: unrestricted anytime confidence sequences,
authenticated prospective scheduling, and joint fault/selection models.

## G38: robust replanning composition

CLOSED for a fresh frozen episode and supplied deterministic memberships.
learned_episode_coverage joins sampled bands to the actual inherited Q/value and
expected whole-policy regret contract. Mid-episode updates, cumulative
cross-episode accounting, and automatic migration of active durable runs remain open.

## G39: operational log interface

CLOSED as pure Lean rules plus bounded executable evidence for exact identity
strata, idempotent replay, conflicting replay rejection, fault separation,
fixed-checkpoint counting, and fresh-plan export. Remaining: proof-producing
outcome ingestion, cryptographic/remote authority, universal adapter refinement.

## G40: useful non-singleton dominance

CLOSED: the corrected test compares distinct competitors and is formally sound.
The original self-comparison theorem remains unchanged and sound but restrictive.

## Next strongest block

A concrete observation model connecting accepted records, infrastructure faults,
and adaptive sampling to the required count law. The key obstruction is
outcome-dependent censoring: excluding faults can create a biased accepted
sample. A valid next theorem must either prove noninformative censoring or model
the joint outcome/fault process and its resource costs explicitly.
