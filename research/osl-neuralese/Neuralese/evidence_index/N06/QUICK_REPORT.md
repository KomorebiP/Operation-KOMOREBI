# Neuralese Causal Completion — learned-checkpoint result

Author: Komorebi P.  
Version: 0.2.1  
Execution: `PASS`  
All scientific gates: `NOT PASSED`

## Bottom line

The projective checkpoint remains behaviorally strong but is not path-flat: identity-word histories can be distinguished by registered future continuations.
It did not obtain a normally attracting certificate under the registered tangent assay.

This adaptive developmental run tests loop defects through exhaustive future suffixes and state-dependent projective tangent Jacobians on the saved learned checkpoints. It performs no retraining. The failed v0.2.0 smoke is preserved in `results/development_v0.2.0/`.

## Registered gates

| Gate | Status | Observed | Criterion |
|---|---|---|---|
| `execution_checkpoint_digests` | PASS | `true` | all exact |
| `execution_numpy_replay` | PASS | `{"maximum_long_depth_absolute_discrepancy": 0.02783203125, "maximum_short_depth_absolute_discrepancy": 0.0009765625}` | short <= 0.001; long <= 0.03 |
| `Q0_finite_behavioral_quotient` | PASS | `{"maximum_signatures_per_semantic_state": 1.0, "minimum_continuation_accuracy": 1.0}` | accuracy >= 0.99 and exactly one discrete signature per semantic state |
| `P1_positive_scale_gauge` | PASS | `1.0` | == 1.0 |
| `P2_projective_path_flatness` | FAIL | `{"minimum_H8_survival": 0.90625, "worst_median_angle": 0.5251048486315342}` | angle <= 0.01 and H8 survival >= 0.999 |
| `A1_finite_D4_cayley` | PASS | `{"minimum_H4_survival": 1.0, "minimum_current": 1.0}` | current >= 0.999 and H4 survival >= 0.99 |
| `A2_action_separation` | PASS | `1.0` | >= 0.99 |
| `N1_normal_attraction` | FAIL | `1.9772902378890573` | all relation p95 one-loop top tangent gains < 1.0 |
| `comparative_completion` | PASS | `{"angle_advantage_raw_minus_projective": {"cluster_count": 16, "paired_mean_difference": 0.5651000841657112, "percentile_95_interval": [0.4668135447580857, 0.6578212159253041], "replicates": 100}, "survival": {"cluster_count": 16, "paired_mean_difference": 0.9427083333333334, "percentile_95_interval": [0.8891276041666667, 0.96875], "replicates": 100}}` | projective has higher H8 survival and lower angle |

## Repeat-16 identity-loop audit

| Arm | Min endpoint accuracy | Mean H8 survival | Worst median angle | Worst p95 one-loop tangent gain |
|---|---:|---:|---:|---:|
| raw_terminal | 0.1562 | 0.0312 | 1.0933 | 1.8406 |
| relation_pressure | 0.1562 | 0.0417 | 1.4504 | 1.7398 |
| projective_terminal | 1.0000 | 0.9740 | 0.5251 | 1.9773 |

## Paired checkpoint comparison

Projective-minus-raw H8 survival: `0.942708` (cluster-bootstrap 95% interval `[0.8891276041666667, 0.96875]`).

Raw-minus-projective identity-loop angle: `0.565100` (95% interval `[0.4668135447580857, 0.6578212159253041]`).

## Interpretation

The positive-scale gate tests the radial gauge separately from path flatness. The Cayley gate checks all 64 D4 products, while the action-separation gate prevents a collapsed representation from receiving credit merely for satisfying identity relations. The tangent gate uses the implemented normalized map

\[
DF_M(h)=\frac{(I-uu^{\mathsf T})M}{\lVert Mh\rVert},\qquad u=\frac{Mh}{\lVert Mh\rVert},
\]

rather than treating the raw matrix spectrum as the spectrum of the projective dynamics.

No same-space quotient spectrum or invariant-metric certificate is claimed. The local observability tower has not been promoted to a closed quotient because finite-horizon null directions would first need a generator-invariance certificate.

## Claim boundary

These results concern six fixed checkpoints, 64 fresh D4 coordinate randomizations per seed, all eight starting states, and suffixes through the registered finite horizons. They do not establish spontaneous or universal Neuralese, architecture-independent emergence, unbounded recurrence, or any claim about frontier language models or awareness.
