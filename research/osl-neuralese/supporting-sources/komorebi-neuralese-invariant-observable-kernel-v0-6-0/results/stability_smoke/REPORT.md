# Komorebi Neuralese Stable Quotient v0.2.0

## Result

**Developmental gate status:** `PASS`  
**Elapsed:** `5.173` seconds  
**Claim status:** frozen-checkpoint mechanistic development result, not confirmatory emergence evidence.

The original norm explosion decomposes into two effects. Positive radial scale is an exact gauge of the bias-free linear model, so per-step normalization preserves all finite predictions. The remaining depth failure is angular/projective drift. A full-rank future-observability audit found no nonzero fixed additive nuisance packet. An exact table-to-anchor closure arm removes the angular defect and remains bounded while preserving causal interventions.

## D4 depth accuracy

| Variant | L64 |
|---|---:|
| raw | 0.4766 |
| normalized_raw | 0.4375 |
| metric_polar | 0.2188 |
| anchor_closed | 1.0000 |
| semantic_chart_closed | 1.0000 |

`normalized_raw` fixes overflow only. `metric_polar` tests whether norm preservation alone is sufficient. `anchor_closed` compiles each exposed anonymous table as transport between the model's learned state anchors. `semantic_chart_closed` expresses the same closure in a canonical one-hot chart, removing the ill-conditioned ambient metric. Both closed arms are strong structural positive controls and must not be described as spontaneous discovery.

## Mechanistic adjudication

| Gate | Observed | Criterion | Result |
|---|---:|---|---|
| `no_fixed_additive_nuisance_packet` | 0 | `finite-horizon future-null dimension == 0` | PASS |
| `projective_gauge_prediction_equivalence` | 1 | `>= 0.999999` | PASS |
| `semantic_chart_all_depth_accuracy` | 1 | `>= 0.999` | PASS |
| `semantic_chart_all_depth_finite` | 1 | `>= 1.0` | PASS |
| `semantic_chart_closure_backward_error` | 0 | `<= 1e-5` | PASS |
| `semantic_chart_isometry_backward_error` | 0 | `<= 1e-4` | PASS |
| `semantic_chart_metric_condition` | 1 | `<= 1.0001` | PASS |
| `semantic_chart_null_cycle_accuracy` | 1 | `>= 0.999` | PASS |
| `semantic_chart_deep_state_patch` | 1 | `>= 0.99` | PASS |
| `semantic_chart_deep_operator_patch` | 1 | `>= 0.99` | PASS |
| `semantic_chart_random_state_control` | 0.046875 | `<= 0.40` | PASS |
| `semantic_chart_random_operator_control` | 0.046875 | `<= 0.40` | PASS |

## Interpretation

1. The exploding radius was not itself semantic because every positive rescaling produces the same downstream argmax continuation.
2. Normalization keeps computation finite but leaves directional accuracy unchanged until the unnormalized run overflows.
3. The centered decoder has an instantaneous null direction, but the operator family makes it future-observable. A forced linear P/Q split would therefore be false.
4. The learned state anchors already form a complete eight-state semantic coordinate system. Compiling table actions as `B P B^{-1}` removes arbitrary-depth drift; transporting that action into the canonical semantic chart reduces the recurrent metric condition number to one.
5. This establishes an engineering resolution and localizes the learning failure to the unconstrained operator encoder. It does not show that terminal training discovered the closed representation unaided.

## Next scientific threshold

Train a projective/conformal operator encoder with fixed-temperature normalized states, anonymous composition consistency, bounded metric conditioning, and table-derived held-out null cycles. The decisive result is whether the learned encoder approaches the anchor-closed behavior without being given the exact `B P B^{-1}` compiler.
