# v0.4 learned-checkpoint causal-completion probe

Author: Komorebi P.  
Version: 0.1.0  
Status: posthoc mechanism audit

## Outcome

The compact additive linear quotient proposed in the frozen protocol is
**unsupported** by the twelve sealed v0.4 checkpoints. In every `polar_cr`
seed and every one of the 32 shared D4 coordinate contexts, the primary
finite behavioral rank changes from `q0 = 7` to `q1 = 12` and remains 12
through `q4`. The `q4 = 12` result is unchanged at all four relative rank
tolerances from `1e-2` through `1e-6`.

This is a sharp delayed-observability result. The reachable anchor space has
rank eight at horizon zero and contains one centered-logit-null direction.
After one generator step, the reachable space and finite behavioral quotient
both have rank twelve. The horizon-zero direction therefore is not a closed
nuisance fiber. Its maximum generator leakage is `0.40527`, `0.25630`, and
`0.19239` in seeds 101, 211, and 307. A magnitude-0.10 perturbation changes the
current centered-logit ray by at most `2.11e-8` radians, but changes a one-step
future ray by as much as `0.01725`, `0.01508`, and `0.01051` radians.

The result does not rule out a nonlinear or finite decision-packet account of
the behavior. It specifically rejects the tested claim that the learned
`polar_cr` dynamics admit a causally complete additive linear quotient of
dimension at most eight over this horizon.

## Typed D4 loops

The hard-polar `polar_cr` checkpoints satisfy the radial assay but have clear
angular holonomy.

| Seed | Repeat-1 p95 angle | Repeat-16 p95 angle | Repeat-16 agreement | Repeat-16 max absolute log gain |
|---:|---:|---:|---:|---:|
| 101 | 0.09982 | 0.72514 | 1.00000 | 2.90e-5 |
| 211 | 0.07348 | 0.72377 | 1.00000 | 2.00e-5 |
| 307 | 0.09402 | 0.97136 | 0.97778 | 2.22e-5 |

All three single-loop p95 angles exceed the protocol's 0.05 angular-holonomy
cutoff. Sixteen repeated null loops amplify the defect substantially. The
behavior remains buffered for seeds 101 and 211 across the audited future D4
continuations, while seed 307 loses agreement in some cells. Because the
repeat-16 radial log gain stays below `1e-4` in absolute value, the hard-polar
failure is angular rather than radial.

The raw Euclidean arms also show angular holonomy. Their median loop log gains
are strongly negative, approximately -3.36 to -3.97 for one loop and -53.67
to -63.50 for sixteen loops. Projective normalization removes this contraction
but does not remove their directional error.

`RESULTS.json` retains, for each checkpoint and repeat count:

- the pooled `8 x 3 x 8` future-behavior congruence and joint-correctness tensors
- the continuation-averaged per-context `32 x 8 x 3 x 8` tensors
- the canonical centered-logit signed and RMS tensors, pooled and per context
- oriented loop-angle and log-radial-gain summaries for `r4`, `f2`, and `frfr`

## Integrity and controls

The v0.4 archive SHA-256 matched
`4132faa934e94647ec267c0140240397b459c68b6770e95edc30144c39f3662d`.
All twelve official checkpoint receipts matched their SHA-256 values. Every
checkpoint loaded with `weights_only=True`, a strict state-dictionary load,
and matching sealed final-state digest. The actual checkpoint path, including
operator encoding and hard-polar SVD, remained float32. Only extracted arrays
were promoted to float64 for downstream diagnostics.

The exact anchor-compiled D4 control passed in all twelve learned anchor
charts. Its worst oriented loop angle was `2.98e-8` radians, its worst full
12-dimensional relator spectral residual was `2.12e-14`, and both behavioral
congruence and oracle-decoder joint correctness were one. This supports the
implementation's ability to recognize exact closure.

## Retained boundary

This analysis does not repair the original v0.4 study. The original assay
status remains `FAIL`, including the retained A15 packet-result-contract
failure for `euclidean_cr`, seed 211. The archived diagnosis records one case
whose promoted normalized margin was positive while the float32 decoder was
wrong. That failure remains explicit in `RESULTS.json`.

The independent replication unit throughout this report is the training seed.
Contexts and trajectories are deterministic within-seed audit cases, not
independent population replicates. No population p-value is reported.
