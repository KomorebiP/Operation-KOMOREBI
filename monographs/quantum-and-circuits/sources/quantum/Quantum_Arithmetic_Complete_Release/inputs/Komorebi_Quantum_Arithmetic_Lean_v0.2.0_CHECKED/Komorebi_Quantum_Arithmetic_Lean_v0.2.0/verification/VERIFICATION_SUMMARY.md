# Lean verification report

## Result

**PASS.** All 22 original draft theorem statements are preserved. There are
59 checked mathematical declarations, plus four checked refutations used by the
negative tests. All four deliberately false source variants were rejected.

## Toolchain

Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)

Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`

## Final clean run

| Stage | Exit code | Seconds |
|---|---:|---:|
| compile QuantumArithmeticBridge | 0 | 27.33 |
| compile QuantumArithmeticSpecification | 0 | 11.28 |
| compile QuantumArithmeticComplex | 0 | 2.29 |
| compile QuantumArithmeticUnitary | 0 | 21.80 |
| axiom audit | 0 | 1.44 |
| kernel replay QuantumArithmeticBridge | 0 | 11.61 |
| kernel replay QuantumArithmeticSpecification | 0 | 14.80 |
| kernel replay QuantumArithmeticComplex | 0 | 4.49 |
| kernel replay QuantumArithmeticUnitary | 0 | 26.19 |
| prove control refutations | 0 | 1.28 |
| kernel replay control refutations | 0 | 3.86 |
| independent Python exact arithmetic | 0 | 0.77 |

The four mathematical source modules were rebuilt into an empty temporary build
directory. No previous project `.olean` was reused. The pinned imported libraries
were reused and are part of the stated trust boundary.

## Axioms

The full project audit uses only `propext`, `Classical.choice`, and `Quot.sound`.
There is no `sorryAx`, no `Lean.ofReduceBool`, and no project-specific axiom in the
checked theorem dependencies. See `axiom_audit.log` and `control_refutations.log`.

## Deliberate falsehoods tested

* `wrong_energy`: mutation rejected with exit code 1. Its negation was also proved in `tests/ControlRefutations.lean`.
* `wrong_root_order`: mutation rejected with exit code 1. Its negation was also proved in `tests/ControlRefutations.lean`.
* `noise_retained`: mutation rejected with exit code 1. Its negation was also proved in `tests/ControlRefutations.lean`.
* `phase_mode_invented`: mutation rejected with exit code 1. Its negation was also proved in `tests/ControlRefutations.lean`.

## Boundary

The finite arithmetic tables, rational projector identities, sound interpretation
in the complex numbers, and normalized Fourier unitarity are checked. See
`PROOF_BOUNDARY.md` for cross-representation equalities and generalizations that
are not claimed here. This is not a quantum hardware test or a quantum advantage
claim.

## Repairs

The initial broad Mathlib import hit the memory ceiling. Focused imports and
module mode fixed that problem. The added symbolic extensions needed several
elaboration and rewriting repairs. No original theorem statement or coefficient
table was altered. Historical diagnostics are retained under `verification/development`.
