# Neuralese Operator Workspace: Initial Test Report

**Profile:** `smoke`  
**Frozen source digest:** `0b059dd3345ececfad7e40fba702c5e4ab893edfc12af24f687604b8466a77fc`

## Behavioral and causal summary

| Arm | D4 ID | D4 long | C8 ID | Random-family ID | Relation endpoint | State patch | Matched state control | Operator patch | Random operator control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| linear_terminal | 0.2383 | 0.1536 | 0.2207 | 0.1758 | 0.2552 | 0.1250 | 0.1055 | 0.1406 | 0.1406 |
| linear_relation | 0.2109 | 0.1393 | 0.1787 | 0.1367 | 0.2669 | 0.1133 | 0.1328 | 0.1680 | 0.1719 |
| gru_terminal | 0.1318 | 0.1120 | 0.1436 | 0.1133 | 0.0664 | 0.1445 | 0.1367 | 0.1406 | 0.1406 |
| gru_intermediate | 0.1357 | 0.1172 | 0.1514 | 0.1279 | 0.0456 | 0.1484 | 0.1367 | 0.1250 | 0.1406 |
| one_shot_terminal | 0.1191 | 0.1302 | 0.1260 | 0.1221 | 0.1159 | — | — | — | — |
| token_only_terminal | 0.1240 | 0.1068 | 0.1514 | 0.1104 | 0.0807 | 0.1328 | 0.1328 | 0.1055 | 0.0977 |

## Frozen development gates

- **FAIL** `linear_terminal_d4_id`: observed `0.238281`, criterion `>= 0.95`
- **FAIL** `linear_terminal_d4_long`: observed `0.153646`, criterion `>= 0.7`
- **FAIL** `linear_terminal_c8_id`: observed `0.220703`, criterion `>= 0.8`
- **FAIL** `linear_terminal_state_patch`: observed `0.125000`, criterion `>= 0.9`
- **FAIL** `linear_terminal_operator_patch`: observed `0.140625`, criterion `>= 0.9`
- **PASS** `linear_terminal_random_state_control`: observed `0.105469`, criterion `<= 0.4`
- **PASS** `linear_terminal_zero_state_lesion`: observed `0.109375`, criterion `<= 0.4`
- **PASS** `linear_terminal_random_operator_control`: observed `0.140625`, criterion `<= 0.4`
- **FAIL** `linear_terminal_state_patch_margin`: observed `0.019531`, criterion `>= 0.5`
- **FAIL** `linear_terminal_operator_patch_margin`: observed `0.000000`, criterion `>= 0.5`
- **PASS** `token_only_d4_id`: observed `0.124023`, criterion `<= 0.3`
- **FAIL** `linear_over_gru_long_advantage`: observed `0.041667`, criterion `>= 0.1`

## Interpretation boundary

This is a controlled finite-state development assay. The linear-hypernetwork arm is intentionally biased toward a latent operator representation. Success demonstrates learned coordinate alignment, recurrent composition, causal state/operator use, and transportability under the tested distribution. It does not establish spontaneous Neuralese, natural-language-model internals, consciousness, or unrestricted operator discovery.
