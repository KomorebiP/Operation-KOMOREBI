# Neuralese Operator Workspace: Initial Test Report

**Profile:** `pilot`  
**Frozen source digest:** `0b059dd3345ececfad7e40fba702c5e4ab893edfc12af24f687604b8466a77fc`

## Behavioral and causal summary

| Arm | D4 ID | D4 long | C8 ID | Random-family ID | Relation endpoint | State patch | Matched state control | Operator patch | Random operator control |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| linear_terminal | 0.9996 | 0.9054 | 0.9958 | 0.7991 | 0.9992 | 0.9565 | 0.0771 | 0.9648 | 0.0664 |

## Frozen development gates

- **PASS** `linear_terminal_d4_id`: observed `0.999634`, criterion `>= 0.95`
- **PASS** `linear_terminal_d4_long`: observed `0.905436`, criterion `>= 0.7`
- **PASS** `linear_terminal_c8_id`: observed `0.995850`, criterion `>= 0.8`
- **PASS** `linear_terminal_state_patch`: observed `0.956543`, criterion `>= 0.9`
- **PASS** `linear_terminal_operator_patch`: observed `0.964844`, criterion `>= 0.9`
- **PASS** `linear_terminal_random_state_control`: observed `0.077148`, criterion `<= 0.4`
- **PASS** `linear_terminal_zero_state_lesion`: observed `0.125000`, criterion `<= 0.4`
- **PASS** `linear_terminal_random_operator_control`: observed `0.066406`, criterion `<= 0.4`
- **PASS** `linear_terminal_state_patch_margin`: observed `0.879395`, criterion `>= 0.5`
- **PASS** `linear_terminal_operator_patch_margin`: observed `0.898438`, criterion `>= 0.5`

## Interpretation boundary

This is a controlled finite-state development assay. The linear-hypernetwork arm is intentionally biased toward a latent operator representation. Success demonstrates learned coordinate alignment, recurrent composition, causal state/operator use, and transportability under the tested distribution. It does not establish spontaneous Neuralese, natural-language-model internals, consciousness, or unrestricted operator discovery.
