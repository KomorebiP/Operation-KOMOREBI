# Exact proof boundary — AVOC v0.39.0

## Kernel-checked mathematics

- Exact rational binomial count normalization and nonnegativity.
- Uniform-cell envelopes, grid coverage, valid interval hulls, and miss mass <=alpha.
- Simultaneous finite-schedule coverage and arbitrary data-dependent selection
  from that schedule, without cross-checkpoint independence.
- Explicit binomial marginal-law bridge and learned-band-to-fixed-policy coverage.
- Exact identity/replay rules, conflicting replay rejection, and exclusion of
  faults/unfinished intents from binary samples.
- Probability replacement preserves deterministic quote fields and identities;
  changed evidence obstructs acknowledgement of an authentic prior intent.
- Competitor-only dominance and executable checker soundness.
- The inherited Q/value and expected whole-policy regret guarantees, conditional
  on compatible realizations and the same conservative reservation policy.

The axiom audit covers all explicitly named theorem/lemma declarations, including
two inherited private helpers omitted from the previous public-name inventory.
The allowed foundational union is `propext`, `Classical.choice`, `Quot.sound`.

## Executed bounded implementation evidence

Independent Fraction calculations, count-distribution convolution, binary-sequence
enumeration, actual Lean interval comparisons, log/parser/replay checks, and an
actual Lean calibration-to-planning scenario are recorded under results/v0.39.0.
These finite executions do not replace universal theorems or prove the host.

## Supplied model assumptions

1. Each scheduled count has the stated binomial marginal law for its exact
   operation stratum. Stationary independent Bernoulli accepted observations
   provide the usual interpretation, but this release does not formalize a
   derivation from a concrete physical sampling process to that count law.
2. The finite schedule, grids, and error allowances are specified before the
   observations used by them. The parser cannot prove historical precommitment.
3. Fault exclusion must leave the accepted sample law valid. If failures become
   timeouts and successes become checked records, discarding timeouts biases the
   accepted stream. The formal choice not to count faults does not prove
   noninformative censoring. If the probability instead means success conditional
   on completion, the planner must explicitly use that same target.
4. Identity separation does not prove provider stationarity or remote authenticity.
   Protected authority inputs and checked outcome labels are supplied. An
   evidence_id is not a cryptographic attestation or proof-checker invocation.
5. Deterministic setup/gross interval membership remains supplied. Learning a
   success probability does not calibrate costs, savings, or workload counts.
6. The underlying formal probability is rational. No formal coverage theorem for
   arbitrary irrational parameters is claimed in this release.

## Scope of the statistical policy conclusion

Coverage is an outer probability over data. It is not a posterior probability
for the interval already observed. Inside the coverage event, the controller's
regret is an expected finite-horizon policy-value difference under a fixed model,
not realized sample-path loss. Quotes stay fixed within that episode. A newly
selected checkpoint can start another episode, but no cumulative cross-episode
reward/accounting theorem is claimed.

The benchmark retains upper-setup reservations. Runtime `spent` records those
reservations, while the robust true reward can use realized setup. No automatic
refund or identity with physical spending follows. The lower-Q controller
maximizes its certified lower bound; it is not asserted to solve the exact
maximin problem over all compatible models.

## Runtime and storage trust

Lean compiler/kernel, pinned cached dependencies, Python, SQLite, OS, and protected
filesystem remain trusted. Local project sources are rebuilt; external dependency
caches are not rebuilt from all source. There is no alternate kernel check,
universal Python/SQLite refinement, hostile rollback defense, or power-loss
certification. New calibration consumes protected log snapshots and emits fresh
plans; it does not silently authorize probability mutation of active durable runs.

The supported launcher and raw new Lean entrypoint reject decimal/exponent number
tokens; exact integer and reduced rational-string fields are used. Resource caps
are implementation guards, not a proof of parser/arithmetical complexity.

## Corrections to inherited evidence descriptions

Fresh reproduction found five old negative files failed on missing finite-field
instances and a sixth failed because decide saw a free variable. These were
setup/tactic failures, not the claimed mathematical rejections. Minimal repairs
and original failures are preserved under provenance/v0.38_negative_setup.
The repaired suite is rerun substantively in this release.

The v0.38 concrete action-reversal and dominance reports are executable evidence;
the source's scalar example lemmas did not prove those full selector equalities.
The generic theorems remain intact. The new checked ten-trial interval examples
and generic learned-policy composition are explicitly distinguished from the
larger executable demonstration.

## Claims deliberately not made

Empirical calibration of an actual service; authenticated real outcome provenance;
unrestricted optional stopping; data-selected unbudgeted grids/checkpoints;
mid-episode probability updates; automatic retry of unresolved paid operations;
optimal confidence width; global computational-cost optimality; real LLM
productivity or autonomous discovery; historical novelty.

## Provenance

The authoritative predecessor is v0.38.0 with archive SHA-256
`a54dac36e77636ffd974e849a653995daea78091214921042c5f273b5a8cc6c4`.
Its lineage remains v0.37 reconstructed from complete v0.35 source and retained
v0.36 specification because the complete v0.36 source was absent. No missing
v0.36 source is retroactively described as independently checked.
