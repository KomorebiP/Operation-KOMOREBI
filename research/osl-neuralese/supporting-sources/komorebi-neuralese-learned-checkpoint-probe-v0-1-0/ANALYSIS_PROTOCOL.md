# Frozen posthoc analysis protocol

Author: Komorebi P.  
Version: 0.1.0  
Frozen: 2026-09-03

## Evidence status

This is a posthoc mechanism audit of already inspected, sealed checkpoints.
It cannot repair or supersede any original gate. The v0.4 calculations below
were fixed before their new rank ladders and state-resolved loop tensors were
computed. An exploratory v0.3 hard-QR check informed the secondary bridge
analysis, so that branch is explicitly descriptive.

## Source artifacts

- `Komorebi_Neuralese_Packet_Closure_v0.4.0.zip`
  - SHA-256: `4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d`
- `Komorebi_Neuralese_Operator_Workspace_v0.3.0.zip`
  - SHA-256: `80dfc185a4502e9086ba27f1725b05bb9f0b96ecafcc1b30ee5da474b003dbd1`

## Primary checkpoint census

Use all twelve official v0.4 checkpoints, without outcome-based selection:

- arms: `euclidean_supervised`, `euclidean_cr`, `polar_supervised`, `polar_cr`
- training seeds: `101`, `211`, `307`

Every checkpoint must match its sealed SHA-256 receipt, load with
`weights_only=True`, and satisfy a strict state-dictionary load.

## Context bank

Use 32 deterministic, unique D4 coordinate contexts shared by every
checkpoint. The bank seed is `2026090301`. Context freshness is relative to
this analysis only. It is not guaranteed to be absent from the full training
stream.

## Finite causal-completion ladder

For each model and context, let `B` contain the eight normalized state anchors,
let `C` be the decoder after removing the common-logit direction, and whiten
the latent coordinates with the recurrence metric. For horizons `H=0,...,4`,
form

\[
R_H=\operatorname{span}\{M_uB:|u|\le H\},
\qquad
O_H=\operatorname{rowspan}\{CM_v:|v|\le H\}.
\]

The finite reachable behavioral dimension is

\[
q_H=\operatorname{rank}(O_HU_{R_H}),
\]

where `U_RH` is an orthonormal basis of `R_H`. The candidate null fiber inside
the reachable space has dimension `rank(R_H)-q_H`.

Matrix-product blocks are rescaled before stacking. This does not change their
exact spans or kernels, but prevents arbitrary radial gain from dominating the
numerical rank. The primary relative tolerance is `1e-6`; sensitivity is
reported at `1e-2`, `1e-3`, `1e-4`, and `1e-6`.

For every nonempty candidate null fiber, report generator leakage into its
orthogonal complement. Also perturb actual anchor rays along the instantaneous
reachable-null direction and measure current versus one-step centered-logit
ray change. This checks whether instantaneous invisibility is delayed
observability rather than a closed nuisance fiber.

A compact additive quotient of dimension at most eight is supported only if
`q_4 <= 8` in every context of every `polar_cr` seed and its inferred null
fiber has maximum generator leakage at most `0.05`. Otherwise the compact
linear-quotient hypothesis is unsupported, even if a nonlinear finite
decision-packet description remains viable.

## Typed D4 relation audit

Use the three exact D4 relators `r4`, `f2`, and `frfr`, at repeats `1` and `16`.
For every context, canonical start state, and shortest representative of each
of the eight D4 elements:

1. compare the baseline ray with the ray after inserting the null loop;
2. record the sum of per-step log radial increments;
3. continue both rays through all eight D4 elements;
4. record baseline/loop prediction agreement and joint correctness.

After averaging over the eight continuations, this produces a
`8 x 3 x 8` tensor indexed by prefix element, relation, and canonical start
state. A second `8 x 3 x 8` tensor records canonicalized centered-logit
direction changes by start state, relation, and output coordinate.

Angles use oriented positive rays. Antipodes are distance pi, not zero.

Classification cutoffs are descriptive:

- radial-only: p95 loop angle at most `0.01` radians and behavioral agreement
  at least `0.99`, despite nontrivial log radial gain;
- angular holonomy: p95 angle above `0.05` radians or behavioral agreement
  below `0.95` after radial normalization;
- hard-polar assay check: absolute loop log gain at most `1e-4`;
- flat loop: both angular and radial defects below their cutoffs with preserved
  behavior.

An exact anchor-compiled D4 action is required to produce unit behavioral
agreement and negligible loop angle as an estimator positive control.

## Aggregation boundary

The independent replication unit is the training seed, not a context, state,
word, or trajectory. Report every seed and the median/full range across three
seeds. Do not use trajectory counts as a population sample size and do not
report a population-level p-value.

## Secondary v0.3 bridge

The separate v0.3 hard-QR Operator Workspace is analyzed across all retained
`hard_correct` seeds and its complete held-out coordinate split. It tests the
same observability and radial/angular separation in an eight-dimensional,
hard-stable architecture. It is a parallel case study, not a direct lineage
step into v0.4.
