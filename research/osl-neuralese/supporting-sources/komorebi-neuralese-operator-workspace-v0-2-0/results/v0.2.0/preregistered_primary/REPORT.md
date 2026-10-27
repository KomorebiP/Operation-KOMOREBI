# V0.2 recurrent closure and intrinsic-metric report

**Protocol:** `komorebi-v0.2-prospectively-frozen-primary-2026-09-02`  
**Analysis status:** `prospectively_frozen_primary_after_development_calibration`  
**Coordinate split:** `test`

## Arm summary

| Arm | D4 depth 8 | D4 depth 64 | D4 depth 128 | C8 depth 64 | Composition substitution | G-isometry defect p95 | Metric condition | Context patch | Patch margin |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| terminal | 0.9348 | 0.3402 | 0.2723 | 0.1988 | 0.8748 | 2.3482 | 1.0000 | 0.3182 | 0.2270 |
| relation_060 | 1.0000 | 0.8301 | 0.5922 | 0.5699 | 0.8748 | 0.7300 | 1.0000 | 0.4486 | 0.3668 |
| fixed_metric | 1.0000 | 0.7039 | 0.4359 | 0.3461 | 0.8748 | 0.0764 | 1.0000 | 0.4437 | 0.3652 |
| learned_metric | 0.9977 | 0.5465 | 0.3977 | 0.2543 | 0.8748 | 0.1008 | 4.3935 | 0.4437 | 0.3660 |
| composition | 0.9973 | 0.6797 | 0.3984 | 0.4477 | 0.8748 | 4.6308 | 1.0000 | 0.4500 | 0.3750 |
| metric_composition | 0.9879 | 0.8660 | 0.6105 | 0.7203 | 0.8750 | 0.2128 | 6.4119 | 0.4146 | 0.3342 |
| metric_composition_shuffled | 0.9844 | 0.6078 | 0.3871 | 0.3078 | 0.8748 | 0.3973 | 8.5803 | 0.4211 | 0.3385 |
| gru_terminal | 0.4152 | 0.3086 | 0.2758 | 0.2051 | 0.6912 | — | — | 0.1229 | -0.0016 |

## Frozen gates

| Gate | Status | Observed | Criterion |
|---|---|---:|---|
| `primary_d4_depth8` | **PASS** | 0.9879 | >= 0.98 |
| `primary_d4_depth32` | **PASS** | 0.9375 | >= 0.85 |
| `primary_d4_depth64` | **PASS** | 0.8660 | >= 0.6 |
| `primary_d4_depth128` | **PASS** | 0.6105 | >= 0.45 |
| `primary_c8_depth64` | **PASS** | 0.7203 | >= 0.3 |
| `primary_random_depth64` | **PASS** | 0.2273 | >= 0.2 |
| `finite_depth128` | **PASS** | 1.0000 | >= 1.0 |
| `g_transient_depth128` | **PASS** | 1.0161 | <= 5.0 |
| `g_endpoint_depth128` | **FAIL** | 0.0013 | in [0.1, 10.0] |
| `heldout_isometry` | **PASS** | 0.2128 | <= 0.3 |
| `heldout_spectral_radius` | **PASS** | 0.9924 | <= 1.06 |
| `heldout_singular_gain` | **PASS** | 1.0115 | <= 1.12 |
| `metric_condition` | **PASS** | 6.4119 | <= 20.0 |
| `composition_substitution` | **FAIL** | 0.8750 | >= 0.9 |
| `composition_output_agreement` | **FAIL** | 0.6617 | >= 0.8 |
| `composition_closure_residual` | **FAIL** | 0.7797 | <= 0.6 |
| `composition_beats_shuffled_residual` | **PASS** | 0.1222 | paired mean delta >= 0.05 |
| `composition_beats_shuffled_depth64` | **PASS** | 0.2582 | paired mean delta >= 0.05 |
| `cross_context_patch` | **FAIL** | 0.4146 | >= 0.7 |
| `cross_context_wrong_control` | **PASS** | 0.0805 | <= 0.2 |
| `cross_context_margin` | **FAIL** | 0.3342 | >= 0.5 |
| `transport_aligned` | **PASS** | 0.9848 | >= 0.75 |
| `transport_shuffled_control` | **PASS** | 0.1406 | <= 0.4 |
| `transport_random_control` | **PASS** | 0.0809 | <= 0.4 |
| `transport_operator_behavior` | **PASS** | 0.9820 | >= 0.75 |
| `transport_metric_compatibility` | **PASS** | 0.4683 | <= 0.75 |

## Cross-seed transport

| Metric | Mean |
|---|---:|
| `by_family.d4.aligned_state_patch_accuracy` | 0.9848 |
| `by_family.d4.shuffled_pair_state_patch_accuracy` | 0.1406 |
| `by_family.d4.random_map_state_patch_accuracy` | 0.0809 |
| `by_family.d4.decode_reembed_state_patch_accuracy` | 0.9922 |
| `by_family.d4.operator_intertwining_behavior_agreement` | 0.9820 |
| `by_family.d4.metric_compatibility_normalized_defect` | 0.4683 |

## Completeness and interpretation

The exact arm-by-seed grid was complete (80/80 cells).

The model receives complete transition tables and an operator-shaped 8×8 latent channel. An exact table-transpose executor exists. Results therefore test stable learned equivariant table execution, anonymous closure, and coordinate transport under this explicit inductive bias; they do not establish spontaneous Neuralese, abstract operator discovery, language-model generality, or awareness.
