# Neuralese Operator Workspace: Initial Test Report

**Profile:** `pilot`  
**Frozen source digest:** `0b059dd3345ececfad7e40fba702c5e4ab893edfc12af24f687604b8466a77fc`

## Behavioral and causal summary

| Arm | D4 ID | D4 long | C8 ID | Random-family ID | Relation endpoint | State patch | Matched state control | Operator patch | Random operator control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| linear_terminal | 0.9998 | 0.8988 | 0.9972 | 0.7969 | 0.9996 | 0.9509 | 0.0742 | 0.9561 | 0.0605 |
| linear_relation | 1.0000 | 0.9980 | 1.0000 | 0.8010 | 1.0000 | 1.0000 | 0.0601 | 0.9990 | 0.0623 |
| gru_terminal | 0.7764 | 0.4585 | 0.5296 | 0.4063 | 0.7952 | 0.4709 | 0.0999 | 0.4829 | 0.0569 |
| gru_intermediate | 0.7820 | 0.4312 | 0.5573 | 0.4266 | 0.7574 | 0.4644 | 0.1101 | 0.4504 | 0.0725 |
| one_shot_terminal | 0.5024 | 0.2321 | 0.3062 | 0.2609 | 0.9864 | — | — | — | — |
| token_only_terminal | 0.2228 | 0.1843 | 0.1675 | 0.1501 | 0.9797 | 0.2188 | 0.1152 | 0.2131 | 0.0989 |

## Frozen development gates

- **PASS** `linear_terminal_d4_id`: observed `0.999756`, criterion `>= 0.95`
- **PASS** `linear_terminal_d4_long`: observed `0.898763`, criterion `>= 0.7`
- **PASS** `linear_terminal_c8_id`: observed `0.997192`, criterion `>= 0.8`
- **PASS** `linear_terminal_state_patch`: observed `0.950928`, criterion `>= 0.9`
- **PASS** `linear_terminal_operator_patch`: observed `0.956055`, criterion `>= 0.9`
- **PASS** `linear_terminal_random_state_control`: observed `0.074219`, criterion `<= 0.4`
- **PASS** `linear_terminal_zero_state_lesion`: observed `0.128418`, criterion `<= 0.4`
- **PASS** `linear_terminal_random_operator_control`: observed `0.060547`, criterion `<= 0.4`
- **PASS** `linear_terminal_state_patch_margin`: observed `0.876709`, criterion `>= 0.5`
- **PASS** `linear_terminal_operator_patch_margin`: observed `0.895508`, criterion `>= 0.5`
- **PASS** `token_only_d4_id`: observed `0.222778`, criterion `<= 0.3`
- **PASS** `linear_over_gru_long_advantage`: observed `0.440267`, criterion `>= 0.1`
- **PASS** `cross_seed_transport_patch`: observed `0.797852`, criterion `>= 0.7`
- **PASS** `cross_seed_random_map_control`: observed `0.063477`, criterion `<= 0.4`

## Cross-seed coordinate transport

The affine map was fitted only on D4 trajectories of lengths 1 through 4, then tested on new episodes.

| Test family | Native continuation | Aligned source patch | Random-map control | Hidden R² | Intertwining cosine |
|---|---:|---:|---:|---:|---:|
| d4 | 0.9473 | 0.7979 | 0.0635 | 0.4033 | 0.8572 |
| c8 | 0.8721 | 0.7490 | 0.0688 | 0.3139 | 0.8457 |
| mixed_cycle | 0.7959 | 0.7378 | 0.0776 | 0.3770 | 0.8558 |
| random | 0.5029 | 0.4951 | 0.0991 | 0.3269 | 0.8376 |

## Interpretation boundary

This is a controlled finite-state development assay. The linear-hypernetwork arm is intentionally biased toward a latent operator representation. Success demonstrates learned coordinate alignment, recurrent composition, causal state/operator use, and transportability under the tested distribution. It does not establish spontaneous Neuralese, natural-language-model internals, consciousness, or unrestricted operator discovery.

## Exploratory posthoc diagnostics

- `POSTHOC_GEOMETRY.md`: path-conditioned state geometry and decision-equivalence classes
- `POSTHOC_STABILITY.md`: depth extrapolation, hidden growth, and learned operator spectra
- `POSTHOC_RELATION_SWEEP.md`: two-seed relation-pressure phase sweep
- `INITIAL_FINDINGS.md`: integrated interpretation and next mechanism
