import KomorebiQCOS.GaussianTail
import Mathlib.Probability.Distributions.Gaussian.Multivariate
import Mathlib.Analysis.InnerProductSpace.Spectrum

/-!
# Exact central Gaussian spectral reduction

A real self-adjoint operator supplies its eigenbasis through the existing proved
spectral theorem. Basis invariance of the actual Gaussian measure then identifies
its quadratic-form distribution with the concrete independent-squares law.
All eigenvalues, including zeros, are retained. No numerical eigensolver is used.
-/

namespace KomorebiQCOS
open MeasureTheory ProbabilityTheory
open scoped BigOperators RealInnerProductSpace

variable {E I : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] [Fintype I]

/-- The exact quadratic statistic of a real linear operator. -/
def operatorQuadratic (T : E →ₗ[ℝ] E) (x : E) : ℝ := inner ℝ x (T x)

theorem operatorQuadratic_measurable (T : E →ₗ[ℝ] E) :
    Measurable (operatorQuadratic T) := by
  have hT : Continuous T := T.continuous_of_finiteDimensional
  exact (continuous_id.inner hT).measurable

omit [FiniteDimensional ℝ E] [MeasurableSpace E] [BorelSpace E] in
/-- In an actual orthonormal eigenbasis the exact form is the sum of weighted squares. -/
theorem operatorQuadratic_basis_sum (T : E →ₗ[ℝ] E) (b : OrthonormalBasis I ℝ E)
    (coeff : I → ℝ) (h : ∀ i, T (b i) = coeff i • b i) (z : I → ℝ) :
    operatorQuadratic T (∑ i, z i • b i) = weightedSquares Finset.univ coeff z := by
  unfold operatorQuadratic weightedSquares
  simp only [map_sum, map_smul, h, smul_smul]
  rw [b.orthonormal.inner_sum]
  apply Finset.sum_congr rfl
  intro i _
  simp only [starRingEnd_apply, star_trivial]
  ring

/-- Complete distributional reduction from a supplied orthonormal eigenbasis. -/
theorem operatorQuadratic_law_of_basis (T : E →ₗ[ℝ] E) (b : OrthonormalBasis I ℝ E)
    (coeff : I → ℝ) (h : ∀ i, T (b i) = coeff i • b i) :
    (stdGaussian E).map (operatorQuadratic T) = gaussianQuadraticLaw coeff := by
  have hs : Measurable (fun z : I → ℝ => ∑ i, z i • b i) := by fun_prop
  rw [stdGaussian_eq_map_pi_orthonormalBasis b,
    Measure.map_map (operatorQuadratic_measurable T) hs]
  unfold gaussianQuadraticLaw standardGaussianProduct
  congr 1
  funext z
  exact operatorQuadratic_basis_sum T b coeff h z

/-- The spectral theorem constructs the eigenbasis; diagonalization is not a premise. -/
theorem symmetric_operatorQuadratic_law (T : E →ₗ[ℝ] E) (hT : T.IsSymmetric) :
    (stdGaussian E).map (operatorQuadratic T) =
      gaussianQuadraticLaw (hT.eigenvalues rfl) :=
  operatorQuadratic_law_of_basis T (hT.eigenvectorBasis rfl)
    (hT.eigenvalues rfl) (hT.apply_eigenvectorBasis rfl)

/-- The same identity at every closed upper-tail threshold, including atoms. -/
theorem symmetric_operatorQuadratic_tail (T : E →ₗ[ℝ] E) (hT : T.IsSymmetric)
    (q : ℝ) :
    tailProbability (stdGaussian E) (operatorQuadratic T) q =
      gaussianWeightedTail (hT.eigenvalues rfl) q := by
  rw [tailProbability_eq_map (stdGaussian E) (operatorQuadratic_measurable T),
    symmetric_operatorQuadratic_law T hT, gaussianWeightedTail_eq_law]

/-- Spectral coefficient intervals enclose the tail of the original operator. -/
theorem symmetric_operatorQuadratic_enclosed (T : E →ₗ[ℝ] E) (hT : T.IsSymmetric)
    (lower upper : Fin (Module.finrank ℝ E) → ℝ)
    (hl : ∀ i, lower i ≤ hT.eigenvalues rfl i)
    (hu : ∀ i, hT.eigenvalues rfl i ≤ upper i) (q : ℝ) :
    Enclosed (tailProbability (stdGaussian E) (operatorQuadratic T) q)
      (gaussianWeightedTail lower q) (gaussianWeightedTail upper q) := by
  rw [symmetric_operatorQuadratic_tail T hT]
  exact gaussianWeightedTail_enclosed lower _ upper hl hu q

/-- Checked composition from an actual operator to a multiplicative probability
contract. Eigenvalue bounds and endpoint probability enclosures remain explicit. -/
theorem symmetric_operatorQuadratic_rational_acceptance
    (T : E →ₗ[ℝ] E) (hT : T.IsSymmetric)
    (lower upper : Fin (Module.finrank ℝ E) → ℝ)
    (hl : ∀ i, lower i ≤ hT.eigenvalues rfl i)
    (hu : ∀ i, hT.eigenvalues rfl i ≤ upper i)
    (q : ℝ) (L U tolerance : ℚ) (estimate : ℝ)
    (hL : (L : ℝ) ≤ gaussianWeightedTail lower q)
    (hU : gaussianWeightedTail upper q ≤ (U : ℝ))
    (he : Enclosed estimate (L : ℝ) (U : ℝ))
    (ha : acceptsRational L U tolerance = true) :
    0 < tailProbability (stdGaussian E) (operatorQuadratic T) q ∧
      |estimate - tailProbability (stdGaussian E) (operatorQuadratic T) q| /
        tailProbability (stdGaussian E) (operatorQuadratic T) q ≤ (tolerance : ℝ) := by
  rw [symmetric_operatorQuadratic_tail T hT]
  exact gaussianWeightedTail_rational_acceptance lower _ upper hl hu q L U tolerance
    estimate hL hU he ha

end KomorebiQCOS
