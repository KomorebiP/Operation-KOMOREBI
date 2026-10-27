# AVOC v0.41.0 gap ledger

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

## G41: primitive source law to count law

CLOSED within the finite rational source model. The conditional fresh-outcome
contract implies product-vector probabilities and binomial prefix counts.
Shared-source prefix truncation is proved. Equal marginals alone are refuted as
sufficient. Remaining: verify this source contract for a real service; arbitrary
real/infinite/dependent/drifting source models are not covered.

## G42: faults and adaptive collection preserve scheduled samples

CLOSED for the explicit recursive reveal machine. Reports consume the next
source Boolean; rejection is retained; fault consumes none. All scheduled first-n
prefixes share the same per-identity history. The trace may depend arbitrarily on
outcomes. Fresh log steps agree with reveal steps under fresh-ID/next-bit premises.
Remaining: universal operation-ID/intent/host refinement and physical fault-model
applicability. A parsed log does not certify those premises.

## G43: safe observed-sample-to-policy composition

CLOSED for unconditional issuance risk. The final shared_stream theorem derives
both count-law and prefix correspondence, then bounds uncertified issued plans
by the finite scheduled sum. Either missing selected checkpoint prevents issue.
The stronger nominal guarantee conditioned on completion is FALSE; Lean and
exact interval-specific counterexamples are preserved. No availability or cost
of data collection bound is proved.

## G44: physical attempt process to accepted-source coupling

OPEN beyond the proved one-attempt censoring formulas and bounded oracle family.
Equal positive success/rejection retention preserves a one-attempt parameter;
a universal multi-attempt conditional-kernel-to-latent-stream construction is not
proved. Nor is empirical stationarity/authenticity established. Outcome-dependent
consuming censoring can break the target parameter and unconditional calibration.

## G45: operation-ID lifecycle and full generative refinement

CLOSED for the defined pure finite machines. Pending intent is stored separately
from terminal records; global IDs, once-only completion, exact replay, and
conflicting reuse are proved. Full generated runs refine the raw recorder and
reveal machine. A failed batch or any pending ID blocks actual log-derived
policy issuance. The final scheduled error theorem is unconditional.

The Python reducer and registry export have bounded independent/actual-Lean
comparisons. Universal Python/parser/storage refinement and the coupling of
arbitrary physical raw inputs to the generative source remain OPEN.

## G46: completion ordering and statistical target

The implication “independent attempted outcomes plus complete, resolved logs
imply IID first-completed prefixes” is FALSE. Exact finite evidence shows that
success-first completion biases even fully resolved logs and can violate the
implemented calibration interval's nominal coverage. An initiation-indexed or
otherwise justified report-order sampling contract remains OPEN.

## Remaining priorities

Physical attempt/report-order coupling and authenticated complete input;
universal host/storage refinement; multi-episode error/reward/cost accounting;
empirical costs/savings and workloads; broader artifacts; real-parameter,
infinite/stopping/drifting and scalable confidence methods. G45 closes the pure
lifecycle/refinement portion of G39/G42, not these physical/host obligations.
