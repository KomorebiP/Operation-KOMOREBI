# Post-hoc seed-paired descriptive analysis

**Status:** `posthoc_descriptive_not_preregistered_not_a_frozen_gate`  
**Bootstrap replicates per metric and contrast:** `100,000`  
**Primary protocol:** `komorebi-v0.3-stage-a-strict-path-primary-v3-2026-09-02`  
**Analysis input SHA-256:** `25f6a802b01c74ca1f90bc787a5d39899c92ac53800b6cbe1148a77fcf3185d8`

These intervals are exploratory summaries over the completed finite seed grid. They do not retroactively create confirmatory tests, p-values, population guarantees, or multiplicity-adjusted evidence. A paired unit is one shared training seed.

Each interval resamples shared seed pairs and summarizes the mean of left-minus-right deltas. Every PCG64 seed is independently derived from the immutable analysis-input hash and the canonical contrast specification.

## Paired contrasts

| Category | Metric | Contrast | Left mean | Right mean | Mean delta | 95% percentile CI | n |
|---|---|---|---:|---:|---:|---:|---:|
| behavior | C8 endpoint accuracy, depth 64 | hard_correct - hard_shuffled | 0.395996 | 0.140137 | 0.255859 | [0.0849609, 0.440755] | 12 |
| closure | Median operator closure residual | hard_correct - hard_shuffled | 1.15753 | 1.17145 | -0.0139176 | [-0.0214261, -0.00688734] | 12 |
| closure | Native two-step accuracy | hard_correct - hard_shuffled | 0.692708 | 0.695964 | -0.00325521 | [-0.0202637, 0.0111491] | 12 |
| closure | True composition substitution accuracy | hard_correct - hard_shuffled | 0.863607 | 0.862142 | 0.00146484 | [-0.00390625, 0.0069987] | 12 |
| closure | Sequential/direct output agreement | hard_correct - hard_shuffled | 0.595052 | 0.591471 | 0.00358073 | [-0.0113118, 0.0157064] | 12 |
| cross_context | Cross-context patch margin | hard_correct - hard_shuffled | 0.111491 | 0.104818 | 0.00667318 | [-0.0266927, 0.0377604] | 12 |
| cross_context | Cross-context state-patch accuracy | hard_correct - hard_shuffled | 0.218913 | 0.215007 | 0.00390625 | [-0.0211589, 0.0276693] | 12 |
| cross_context | On-manifold wrong-state control accuracy | hard_correct - hard_shuffled | 0.107422 | 0.110189 | -0.00276693 | [-0.0138346, 0.00797526] | 12 |
| cross_context | Recipient-native accuracy | hard_correct - hard_shuffled | 0.333333 | 0.352376 | -0.019043 | [-0.0528971, 0.0123698] | 12 |
| behavior | D4 endpoint accuracy, depth 128 | hard_correct - hard_shuffled | 0.357585 | 0.140137 | 0.217448 | [0.0791016, 0.368815] | 12 |
| behavior | D4 endpoint accuracy, depth 64 | hard_correct - hard_shuffled | 0.484049 | 0.195475 | 0.288574 | [0.114258, 0.474447] | 12 |
| behavior | D4 endpoint accuracy, depth 8 | hard_correct - hard_shuffled | 0.875651 | 0.891276 | -0.015625 | [-0.0773112, 0.0400391] | 12 |
| stability | D4 finite trajectories, depth 2048 | hard_correct - hard_shuffled | 1 | 1 | 0 | [0, 0] | 12 |
| stability | D4 G-norm endpoint ratio, depth 2048 | hard_correct - hard_shuffled | 1.00001 | 1 | 6.57141e-06 | [-1.07785e-06, 1.38506e-05] | 12 |
| stability | D4 minimum G-norm step ratio, depth 2048 | hard_correct - hard_shuffled | 1 | 1 | 0 | [-3.97364e-08, 3.97364e-08] | 12 |
| stability | D4 P95 G-transient gain, depth 2048 | hard_correct - hard_shuffled | 1.00009 | 1.00008 | 1.33062e-05 | [-7.50025e-08, 2.71946e-05] | 12 |
| stability | D4 hard-operator minimum singular value | hard_correct - hard_shuffled | 1 | 1 | 1.28307e-08 | [-1.11861e-08, 3.54003e-08] | 12 |
| stability | D4 hard-operator P95 orthogonality defect | hard_correct - hard_shuffled | 3.10596e-07 | 3.03204e-07 | 7.39217e-09 | [-6.08621e-09, 2.20256e-08] | 12 |
| behavior | Random-family endpoint accuracy, depth 64 | hard_correct - hard_shuffled | 0.180013 | 0.129232 | 0.0507812 | [0.0227865, 0.0794271] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.128.endpoint_accuracy | hard_correct - hard_shuffled | 0.346354 | 0.143555 | 0.202799 | [0.0634766, 0.358724] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.64.endpoint_accuracy | hard_correct - hard_shuffled | 0.487956 | 0.186198 | 0.301758 | [0.109375, 0.509766] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.8.endpoint_accuracy | hard_correct - hard_shuffled | 0.856445 | 0.886068 | -0.0296224 | [-0.0960286, 0.0335286] | 12 |
| split_boundary | Split-conditioned final-action accuracy | hard_correct - hard_shuffled | 0.563585 | 0.405273 | 0.158312 | [0.0315755, 0.294813] | 12 |
| behavior | C8 endpoint accuracy, depth 64 | hard_correct - soft_correct | 0.395996 | 0.786947 | -0.390951 | [-0.555176, -0.216471] | 12 |
| closure | Median operator closure residual | hard_correct - soft_correct | 1.15753 | 0.858939 | 0.298592 | [0.274374, 0.318043] | 12 |
| closure | Native two-step accuracy | hard_correct - soft_correct | 0.692708 | 0.77124 | -0.0785319 | [-0.0947266, -0.0637207] | 12 |
| closure | True composition substitution accuracy | hard_correct - soft_correct | 0.863607 | 0.882243 | -0.0186361 | [-0.0243327, -0.0123698] | 12 |
| closure | Sequential/direct output agreement | hard_correct - soft_correct | 0.595052 | 0.669678 | -0.0746257 | [-0.0877279, -0.0628255] | 12 |
| cross_context | Cross-context patch margin | hard_correct - soft_correct | 0.111491 | 0.367676 | -0.256185 | [-0.280599, -0.23112] | 12 |
| cross_context | Cross-context state-patch accuracy | hard_correct - soft_correct | 0.218913 | 0.442871 | -0.223958 | [-0.242188, -0.206055] | 12 |
| cross_context | On-manifold wrong-state control accuracy | hard_correct - soft_correct | 0.107422 | 0.0751953 | 0.0322266 | [0.019694, 0.0429688] | 12 |
| cross_context | Recipient-native accuracy | hard_correct - soft_correct | 0.333333 | 0.585286 | -0.251953 | [-0.294108, -0.21403] | 12 |
| behavior | D4 endpoint accuracy, depth 128 | hard_correct - soft_correct | 0.357585 | 0.552083 | -0.194499 | [-0.332845, -0.0488281] | 12 |
| behavior | D4 endpoint accuracy, depth 64 | hard_correct - soft_correct | 0.484049 | 0.905436 | -0.421387 | [-0.601725, -0.229655] | 12 |
| behavior | D4 endpoint accuracy, depth 8 | hard_correct - soft_correct | 0.875651 | 1 | -0.124349 | [-0.205404, -0.0493164] | 12 |
| stability | D4 finite trajectories, depth 2048 | hard_correct - soft_correct | 1 | 1 | 0 | [0, 0] | 12 |
| stability | D4 G-norm endpoint ratio, depth 2048 | hard_correct - soft_correct | 1.00001 | 7.05626e-19 | 1.00001 | [1, 1.00002] | 12 |
| stability | D4 minimum G-norm step ratio, depth 2048 | hard_correct - soft_correct | 1 | 0 | 1 | [1, 1] | 12 |
| stability | D4 P95 G-transient gain, depth 2048 | hard_correct - soft_correct | 1.00009 | 1 | 9.30394e-05 | [8.43957e-05, 0.000101354] | 12 |
| behavior | Random-family endpoint accuracy, depth 64 | hard_correct - soft_correct | 0.180013 | 0.279622 | -0.0996094 | [-0.138672, -0.0621745] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.128.endpoint_accuracy | hard_correct - soft_correct | 0.346354 | 0.53418 | -0.187826 | [-0.333008, -0.0309245] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.64.endpoint_accuracy | hard_correct - soft_correct | 0.487956 | 0.91569 | -0.427734 | [-0.616536, -0.228516] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.8.endpoint_accuracy | hard_correct - soft_correct | 0.856445 | 1 | -0.143555 | [-0.233398, -0.0582682] | 12 |
| split_boundary | Split-conditioned final-action accuracy | hard_correct - soft_correct | 0.563585 | 0.816623 | -0.253038 | [-0.38954, -0.112196] | 12 |
| behavior | C8 endpoint accuracy, depth 64 | soft_correct - soft_shuffled | 0.786947 | 0.148926 | 0.638021 | [0.584635, 0.694336] | 12 |
| closure | Median operator closure residual | soft_correct - soft_shuffled | 0.858939 | 0.922771 | -0.0638323 | [-0.115822, -0.0207463] | 12 |
| closure | Native two-step accuracy | soft_correct - soft_shuffled | 0.77124 | 0.77238 | -0.00113932 | [-0.00423177, 0.00211589] | 12 |
| closure | True composition substitution accuracy | soft_correct - soft_shuffled | 0.882243 | 0.885417 | -0.00317383 | [-0.00642904, -0.000488281] | 12 |
| closure | Sequential/direct output agreement | soft_correct - soft_shuffled | 0.669678 | 0.672526 | -0.00284831 | [-0.0078125, 0.00211589] | 12 |
| cross_context | Cross-context patch margin | soft_correct - soft_shuffled | 0.367676 | 0.30127 | 0.0664062 | [0.0515951, 0.0812174] | 12 |
| cross_context | Cross-context state-patch accuracy | soft_correct - soft_shuffled | 0.442871 | 0.385254 | 0.0576172 | [0.0441081, 0.0716146] | 12 |
| cross_context | On-manifold wrong-state control accuracy | soft_correct - soft_shuffled | 0.0751953 | 0.0839844 | -0.00878906 | [-0.0169271, -0.0016276] | 12 |
| cross_context | Recipient-native accuracy | soft_correct - soft_shuffled | 0.585286 | 0.561849 | 0.0234375 | [0.0151367, 0.0325521] | 12 |
| behavior | D4 endpoint accuracy, depth 128 | soft_correct - soft_shuffled | 0.552083 | 0.136068 | 0.416016 | [0.379069, 0.455729] | 12 |
| behavior | D4 endpoint accuracy, depth 64 | soft_correct - soft_shuffled | 0.905436 | 0.146647 | 0.758789 | [0.731934, 0.785319] | 12 |
| behavior | D4 endpoint accuracy, depth 8 | soft_correct - soft_shuffled | 1 | 0.999023 | 0.000976562 | [0.000325521, 0.00179036] | 12 |
| stability | D4 finite trajectories, depth 2048 | soft_correct - soft_shuffled | 1 | 1 | 0 | [0, 0] | 12 |
| stability | D4 G-norm endpoint ratio, depth 2048 | soft_correct - soft_shuffled | 7.05626e-19 | 3.56427e-08 | -3.56427e-08 | [-1.06928e-07, 1.96925e-18] | 12 |
| stability | D4 minimum G-norm step ratio, depth 2048 | soft_correct - soft_shuffled | 0 | 9.69082e-05 | -9.69082e-05 | [-0.000290725, 0] | 12 |
| stability | D4 P95 G-transient gain, depth 2048 | soft_correct - soft_shuffled | 1 | 1 | 0 | [0, 0] | 12 |
| behavior | Random-family endpoint accuracy, depth 64 | soft_correct - soft_shuffled | 0.279622 | 0.140299 | 0.139323 | [0.113281, 0.161458] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.128.endpoint_accuracy | soft_correct - soft_shuffled | 0.53418 | 0.113281 | 0.420898 | [0.362956, 0.472982] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.64.endpoint_accuracy | soft_correct - soft_shuffled | 0.91569 | 0.116536 | 0.799154 | [0.765951, 0.829427] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.8.endpoint_accuracy | soft_correct - soft_shuffled | 1 | 0.998047 | 0.00195312 | [0.000651042, 0.00358073] | 12 |
| split_boundary | Split-conditioned final-action accuracy | soft_correct - soft_shuffled | 0.816623 | 0.409288 | 0.407335 | [0.378255, 0.433268] | 12 |
| behavior | C8 endpoint accuracy, depth 64 | hard_shuffled - hard_correct | 0.140137 | 0.395996 | -0.255859 | [-0.440267, -0.086263] | 12 |
| closure | Median operator closure residual | hard_shuffled - hard_correct | 1.17145 | 1.15753 | 0.0139176 | [0.00689716, 0.021478] | 12 |
| closure | Native two-step accuracy | hard_shuffled - hard_correct | 0.695964 | 0.692708 | 0.00325521 | [-0.0112305, 0.0202637] | 12 |
| closure | True composition substitution accuracy | hard_shuffled - hard_correct | 0.862142 | 0.863607 | -0.00146484 | [-0.00708008, 0.00390625] | 12 |
| closure | Sequential/direct output agreement | hard_shuffled - hard_correct | 0.591471 | 0.595052 | -0.00358073 | [-0.015625, 0.0113932] | 12 |
| cross_context | Cross-context patch margin | hard_shuffled - hard_correct | 0.104818 | 0.111491 | -0.00667318 | [-0.0379232, 0.0265299] | 12 |
| cross_context | Cross-context state-patch accuracy | hard_shuffled - hard_correct | 0.215007 | 0.218913 | -0.00390625 | [-0.0273438, 0.0209961] | 12 |
| cross_context | On-manifold wrong-state control accuracy | hard_shuffled - hard_correct | 0.110189 | 0.107422 | 0.00276693 | [-0.00813802, 0.0138346] | 12 |
| cross_context | Recipient-native accuracy | hard_shuffled - hard_correct | 0.352376 | 0.333333 | 0.019043 | [-0.0125326, 0.0527344] | 12 |
| behavior | D4 endpoint accuracy, depth 128 | hard_shuffled - hard_correct | 0.140137 | 0.357585 | -0.217448 | [-0.368652, -0.0792643] | 12 |
| behavior | D4 endpoint accuracy, depth 64 | hard_shuffled - hard_correct | 0.195475 | 0.484049 | -0.288574 | [-0.475098, -0.113932] | 12 |
| behavior | D4 endpoint accuracy, depth 8 | hard_shuffled - hard_correct | 0.891276 | 0.875651 | 0.015625 | [-0.0400391, 0.0771484] | 12 |
| stability | D4 finite trajectories, depth 2048 | hard_shuffled - hard_correct | 1 | 1 | 0 | [0, 0] | 12 |
| stability | D4 G-norm endpoint ratio, depth 2048 | hard_shuffled - hard_correct | 1 | 1.00001 | -6.57141e-06 | [-1.38084e-05, 1.12007e-06] | 12 |
| stability | D4 minimum G-norm step ratio, depth 2048 | hard_shuffled - hard_correct | 1 | 1 | 0 | [-3.97364e-08, 3.97364e-08] | 12 |
| stability | D4 P95 G-transient gain, depth 2048 | hard_shuffled - hard_correct | 1.00008 | 1.00009 | -1.33062e-05 | [-2.71391e-05, 7.65671e-08] | 12 |
| stability | D4 hard-operator minimum singular value | hard_shuffled - hard_correct | 1 | 1 | -1.28307e-08 | [-3.56552e-08, 1.11465e-08] | 12 |
| stability | D4 hard-operator P95 orthogonality defect | hard_shuffled - hard_correct | 3.03204e-07 | 3.10596e-07 | -7.39217e-09 | [-2.22804e-08, 6.20112e-09] | 12 |
| behavior | Random-family endpoint accuracy, depth 64 | hard_shuffled - hard_correct | 0.129232 | 0.180013 | -0.0507812 | [-0.0791016, -0.0224609] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.128.endpoint_accuracy | hard_shuffled - hard_correct | 0.143555 | 0.346354 | -0.202799 | [-0.359701, -0.063151] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.64.endpoint_accuracy | hard_shuffled - hard_correct | 0.186198 | 0.487956 | -0.301758 | [-0.507487, -0.109049] | 12 |
| frozen_gate | Gate metric: split_conditioned_final_action.by_depth.8.endpoint_accuracy | hard_shuffled - hard_correct | 0.886068 | 0.856445 | 0.0296224 | [-0.0335286, 0.0960286] | 12 |
| split_boundary | Split-conditioned final-action accuracy | hard_shuffled - hard_correct | 0.405273 | 0.563585 | -0.158312 | [-0.294488, -0.0330919] | 12 |

## Completeness

- Available paired metric/contrast analyses: `88`
- Structurally unavailable arm or contrast metrics recorded: `8`
- Full seed-level values, paired deltas, hashes, and per-analysis RNG receipts are in `POSTHOC_DESCRIPTIVE.json`.
