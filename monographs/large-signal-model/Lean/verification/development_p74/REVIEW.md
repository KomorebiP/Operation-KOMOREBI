# P74 author source dictionary

Target: frozen FOUNDATIONS Section 83, Proposition 74 (three displayed error inequalities).
This is the author's self-review; coordinator raw review remains separate.

| Registered object or clause | Actual Lean object or endpoint |
| --- | --- |
| Frobenius norm | `EuclideanMatrixNorms.frobenius`: norm of entry flattening into `EuclideanSpace ℝ (D × D)`; `frobenius_sq` is the entry-square sum |
| Spectral matrix norm | `spectralNorm A = ‖Matrix.toEuclideanCLM A‖`, on Euclidean vectors |
| Symmetric Frobenius domain | `ProposalError.symmetricSpace D`, the actual transpose-fixed entry submodule |
| Euclidean product target | `EuclideanSpace ℝ ((D × D) ⊕ Unit)`; `constraint_norm_sq` identifies squared norm with Frobenius squared plus trace squared |
| M_A(H) | `constraint A H`, literally `(Aᵀ * matrix H * A - matrix H, trace H)` |
| Exact scale normalization | `constraint_eq_target_iff`: actual target equation iff invariant form and trace one |
| Residual | `residual A H = constraint A H - target`; target is literally `(0,1)` |
| Least singular value | `leastSingular L`: actual last domain-indexed `LinearMap.singularValues`; `leastSingular_mul_norm_le` derives the full-domain inequality from the complete singular head |
| Singular perturbation | `leastSingular_sub_le`, from the verified actual ordered singular-value perturbation theorem |
| First boxed inequality | `invariant_form_frobenius_error` |
| Matrix perturbation constant | `constraint_perturbation`, from literal trace cancellation and `frobenius_congruence_sub_le` |
| Derived-budget endpoint | `invariant_form_matrix_budget` combines the actual matrix bound, invariant form, trace one and positive singular gap |
| Actual fixed centers | `fixedCenter A b = toLp 2 ((1-A)⁻¹ *ᵥ b)`; `fixedCenter_equation` derives its defining equation from determinant invertibility |
| Third displayed inequality | `fixed_center_error`, with explicit Euclidean vector and spectral matrix budgets and actual positive denominator |

No estimate of a perturbation budget is inferred from an observed residual. Positive definiteness, cone preservation, complete operator validity, and statistical coverage are not conclusions of P74. The error endpoints require the stated exact reference equation and a positive singular-value gap. The center endpoint retains invertibility of both actual center matrices. Empty finite spatial dimension is permitted; the least singular value is zero for a zero-dimensional domain, so a nonnegative budget cannot satisfy the strict gap there.

The reference injectivity hypothesis is unnecessary as an extra input to these endpoints: `reference_injective` derives it from the actual perturbation budget and the strict gap. This strengthens the registered conditional implication rather than replacing its matrix problem by assumed target identities.

Controls reject: identifying Frobenius and spectral identity norms; applying the residual formula without the positive gap despite an injective exact reference; and treating a singular nonsingular-inverse formula as a solution of `0c=1`.
