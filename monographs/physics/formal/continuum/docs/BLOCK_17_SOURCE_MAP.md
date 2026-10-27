# Block 17 source map

Source: `source/Projector_Refinement_Physics_Complete_Unified_Theory.pdf`, physical PDF page 40 / 550, printed page 27.

| Source item | Lean realization |
|---|---|
| (8.1) Pauli involutions and anticommutation | `RelativisticPauli.alpha_sq`, `beta_sq`, `anticommute` |
| (8.2) ordered update | `DiracWalk1D.massStep`, `shiftStep`, `update` |
| (8.3) unitarity | `DiracWalk1D.update_unitary_left`, `update_unitary_right` |
| (8.4) determinant one | `DiracWalk1D.det_update` |
| (8.5) normalized trace | `DiracWalk1D.half_trace_update` |
| (8.6) exact shell | `Dispersion1D.principalFrequency_shell` |
| (8.7) principal arccos branch | `Dispersion1D.principalFrequency_formula`, `principalFrequency_unique` |
| (8.8) involution exponential for actual α, β | `InvolutionExponential.exp_alpha_closed`, `exp_beta_closed` |
| (8.9) exact product form | `DiracWalk1D.update_closed_product` plus explicit factor theorems |
| (8.10) trace after expansion | `DiracWalk1D.trace_update`, `Dispersion1D.trace_eq_two_shell` |

Added exact consequences include the 2 by 2 characteristic polynomial and the half-turn noncommuting witness. Equations (8.11) onward are deliberately outside Block 17.
