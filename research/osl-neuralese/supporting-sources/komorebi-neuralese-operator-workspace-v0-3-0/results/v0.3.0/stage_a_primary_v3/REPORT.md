# V0.3 hard-stable recurrent operator report

**Protocol:** `komorebi-v0.3-stage-a-strict-path-primary-v3-2026-09-02`  
**Analysis status:** `prospectively_frozen_primary_after_development_calibration_test_unopened`  
**Coordinate split:** `test`

## Arm summary

| Arm | D4 d8 | D4 d64 | D4 d128 | C8 d64 | D4 norm d2048 | Composition substitution | Sequential/direct | Closure residual | Context patch |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hard_correct | 0.8757 | 0.4840 | 0.3576 | 0.3960 | 1.0000 | 0.8636 | 0.5951 | 1.1575 | 0.2189 |
| hard_shuffled | 0.8913 | 0.1955 | 0.1401 | 0.1401 | 1.0000 | 0.8621 | 0.5915 | 1.1714 | 0.2150 |
| soft_correct | 1.0000 | 0.9054 | 0.5521 | 0.7869 | 0.0000 | 0.8822 | 0.6697 | 0.8589 | 0.4429 |
| soft_shuffled | 0.9990 | 0.1466 | 0.1361 | 0.1489 | 0.0000 | 0.8854 | 0.6725 | 0.9228 | 0.3853 |

## Split-conditioned final-action assay

| Arm | Depth | Endpoint accuracy | Candidate acceptance rate |
|---|---:|---:|---:|
| hard_correct | 8 | 0.8564 | 0.1513 |
| hard_correct | 64 | 0.4880 | 0.1468 |
| hard_correct | 128 | 0.3464 | 0.1443 |
| hard_shuffled | 8 | 0.8861 | 0.1513 |
| hard_shuffled | 64 | 0.1862 | 0.1468 |
| hard_shuffled | 128 | 0.1436 | 0.1443 |
| soft_correct | 8 | 1.0000 | 0.1513 |
| soft_correct | 64 | 0.9157 | 0.1468 |
| soft_correct | 128 | 0.5342 | 0.1443 |
| soft_shuffled | 8 | 0.9980 | 0.1513 |
| soft_shuffled | 64 | 0.1165 | 0.1468 |
| soft_shuffled | 128 | 0.1133 | 0.1443 |

Every scored word in this assay has both its primitive maps and its full composite finite-state action in the requested dev/test hash partition. This is split-conditioned final-action evaluation; it does not establish that the abstract group element or word-equivalence class is globally novel.

## Frozen gates

| Gate | Status | Mean | Mean criterion | Seed pass fraction | Required fraction |
|---|---|---:|---|---:|---:|
| `H1_d4_depth8` | **FAIL** | 0.8757 | >= 0.85 | 0.6667 | 0.7500 |
| `H1_d4_depth64` | **FAIL** | 0.4840 | >= 0.25 | 0.5000 | 0.7500 |
| `H1_d4_depth128` | **FAIL** | 0.3576 | >= 0.15 | 0.6667 | 0.7500 |
| `H1_split_conditioned_d4_depth8` | **FAIL** | 0.8564 | >= 0.85 | 0.5000 | 0.7500 |
| `H1_split_conditioned_d4_depth64` | **FAIL** | 0.4880 | >= 0.2 | 0.6667 | 0.7500 |
| `H1_split_conditioned_d4_depth128` | **FAIL** | 0.3464 | >= 0.15 | 0.5833 | 0.7500 |
| `H1_c8_depth64` | **FAIL** | 0.3960 | >= 0.15 | 0.5000 | 0.7500 |
| `H1_random_depth64` | **FAIL** | 0.1800 | >= 0.18 | 0.5000 | 0.6667 |
| `H1_depth2048_finite` | **PASS** | 1.0000 | >= 1.0 | 1.0000 | 1.0000 |
| `H1_depth2048_endpoint_norm` | **PASS** | 1.0000 | in [0.98, 1.02] | 1.0000 | 1.0000 |
| `H1_depth2048_minimum_norm` | **PASS** | 1.0000 | >= 0.98 | 1.0000 | 1.0000 |
| `H1_depth2048_transient` | **PASS** | 1.0001 | <= 1.02 | 1.0000 | 1.0000 |
| `H1_hard_orthogonality` | **PASS** | 0.0000 | <= 1e-05 | 1.0000 | 1.0000 |
| `H1_hard_minimum_singular` | **PASS** | 1.0000 | >= 0.99999 | 1.0000 | 1.0000 |
| `H1_hard_behavior_margin` | **FAIL** | -0.4214 | paired mean delta >= -0.1 | 0.3333 | 0.6667 |
| `H1_hard_avoids_soft_contraction` | **PASS** | 1.0000 | paired mean delta >= 0.5 | 1.0000 | 0.7500 |
| `H2_composition_substitution` | **FAIL** | 0.8636 | >= 0.9 | 0.0000 | 0.7500 |
| `H2_sequential_direct_agreement` | **FAIL** | 0.5951 | >= 0.8 | 0.0000 | 0.7500 |
| `H2_absolute_closure_residual` | **FAIL** | 1.1575 | <= 0.6 | 0.0000 | 0.7500 |
| `H2_correct_beats_shuffled_residual` | **FAIL** | 0.0139 | paired mean delta >= 0.05 | 0.0000 | 0.6667 |
| `H2_correct_beats_shuffled_depth64` | **FAIL** | 0.2886 | paired mean delta >= 0.05 | 0.5833 | 0.6667 |
| `H2_native_two_step` | **FAIL** | 0.6927 | >= 0.9 | 0.0000 | 0.7500 |
| `H3_recipient_native` | **FAIL** | 0.3333 | >= 0.6 | 0.0000 | 0.7500 |
| `H3_cross_context_patch` | **FAIL** | 0.2189 | >= 0.55 | 0.0000 | 0.7500 |
| `H3_wrong_state_control` | **PASS** | 0.1074 | <= 0.2 | 1.0000 | 0.7500 |
| `H3_cross_context_margin` | **FAIL** | 0.1115 | >= 0.4 | 0.0000 | 0.7500 |

## Cross-seed transport

| Metric | Mean |
|---|---:|
| `by_family.d4.aligned_state_patch_accuracy` | 0.8495 |
| `by_family.d4.shuffled_pair_state_patch_accuracy` | 0.1218 |
| `by_family.d4.random_map_state_patch_accuracy` | 0.1069 |
| `by_family.d4.decode_reembed_state_patch_accuracy` | 0.9088 |
| `by_family.d4.operator_intertwining_behavior_agreement` | 0.8608 |
| `by_family.d4.metric_compatibility_normalized_defect` | 0.5204 |

## Completeness and interpretation

The exact arm-by-seed grid was complete (48/48 cells).
The parameter-free exact table oracle passed its fail-closed orientation, closure, and stability checks.

Training confines every nonempty contiguous subword action to the train map partition. The model receives complete transition tables and an operator-shaped 8×8 latent channel, and an exact table-transpose executor exists. Results therefore test learned table execution, anonymous closure, and coordinate transport under this explicit inductive bias. Exact norm preservation and orthogonality in the hard arm are architectural integrity properties, not learned discoveries. The assay does not establish spontaneous Neuralese, a learned invariant metric, globally novel group elements, language-model generality, or awareness.
