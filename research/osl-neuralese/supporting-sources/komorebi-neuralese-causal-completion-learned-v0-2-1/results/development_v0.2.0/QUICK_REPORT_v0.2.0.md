# Neuralese Causal Completion — learned-checkpoint result

Author: Komorebi P.  
Version: 0.2.0  
Execution: `FAIL`  
All scientific gates: `NOT PASSED`

## Bottom line

The projective checkpoint remains behaviorally strong but is not path-flat: identity-word histories can be distinguished by registered future continuations.
It did not obtain a normally attracting certificate under the registered tangent assay.

This is the first run in this line that tests loop defects through exhaustive future suffixes and state-dependent projective tangent Jacobians on the saved learned checkpoints. It performs no retraining.

## Registered gates

| Gate | Status | Observed | Criterion |
|---|---|---|---|
| `execution_checkpoint_digests` | PASS | `true` | all exact |
| `execution_numpy_replay` | FAIL | `0.02783203125` | <= 0.001 |
| `P1_positive_scale_gauge` | PASS | `1.0` | == 1.0 |
| `P2_projective_path_flatness` | FAIL | `{"minimum_H8_survival": 0.8125, "worst_median_angle": 0.8483956771987371}` | angle <= 0.01 and H8 survival >= 0.999 |
| `A1_finite_D4_cayley` | FAIL | `{"minimum_H4_survival": 0.875, "minimum_current": 0.875}` | current >= 0.999 and H4 survival >= 0.99 |
| `A2_action_separation` | PASS | `1.0` | >= 0.99 |
| `N1_normal_attraction` | FAIL | `3.146735947799505` | all relation p95 one-loop top tangent gains < 1.0 |
| `comparative_completion` | PASS | `{"angle_advantage_raw_minus_projective": {"cluster_count": 48, "paired_mean_difference": 0.5184727803584787, "percentile_95_interval": [0.4695681191695193, 0.5698014358829109], "replicates": 100}, "survival": {"cluster_count": 48, "paired_mean_difference": 0.8802083333333334, "percentile_95_interval": [0.828125, 0.9194010416666666], "replicates": 100}}` | projective has higher H8 survival and lower angle |

## Repeat-16 identity-loop audit

| Arm | Min endpoint accuracy | Mean H8 survival | Worst median angle | Worst p95 one-loop tangent gain |
|---|---:|---:|---:|---:|
| raw_terminal | 0.1562 | 0.0417 | 1.3389 | 2.4430 |
| relation_pressure | 0.1094 | 0.0469 | 1.4804 | 1.8115 |
| projective_terminal | 1.0000 | 0.9219 | 0.8484 | 3.1467 |

## Paired checkpoint comparison

Projective-minus-raw H8 survival: `0.880208` (cluster-bootstrap 95% interval `[0.828125, 0.9194010416666666]`).

Raw-minus-projective identity-loop angle: `0.518473` (95% interval `[0.4695681191695193, 0.5698014358829109]`).

## Interpretation

The positive-scale gate tests the radial gauge separately from path flatness. The Cayley gate checks all 64 D4 products, while the action-separation gate prevents a collapsed representation from receiving credit merely for satisfying identity relations. The tangent gate uses the implemented normalized map

\[
DF_M(h)=\frac{(I-uu^{\mathsf T})M}{\lVert Mh\rVert},\qquad u=\frac{Mh}{\lVert Mh\rVert},
\]

rather than treating the raw matrix spectrum as the spectrum of the projective dynamics.

No same-space quotient spectrum or invariant-metric certificate is claimed. The local observability tower has not been promoted to a closed quotient because finite-horizon null directions would first need a generator-invariance certificate.

## Claim boundary

These results concern six fixed checkpoints, 64 fresh D4 coordinate randomizations per seed, all eight starting states, and suffixes through the registered finite horizons. They do not establish spontaneous or universal Neuralese, architecture-independent emergence, unbounded recurrence, or any claim about frontier language models or awareness.
