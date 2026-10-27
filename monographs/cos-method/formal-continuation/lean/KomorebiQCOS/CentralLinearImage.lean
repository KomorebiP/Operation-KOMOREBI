import KomorebiQCOS.SpectralGaussian
import Mathlib.Analysis.InnerProductSpace.Adjoint

/-!
# Central quadratic forms of linear Gaussian images

For X = L Z with a genuine standard Gaussian Z, the law of <X,M X>
is reduced to the spectral law of L* M L. L need not be injective or
surjective. This includes singular linear Gaussian images without an inverse.
No noncentral shift, covariance-square-root construction, or rounded input
interpretation is asserted here.
-/

namespace KomorebiQCOS
open MeasureTheory ProbabilityTheory

variable {E F : Type*}
  [NormedAddCommGroup E] [InnerProductSpace ℝ E] [FiniteDimensional ℝ E]
  [MeasurableSpace E] [BorelSpace E]
  [NormedAddCommGroup F] [InnerProductSpace ℝ F] [FiniteDimensional ℝ F]
  [MeasurableSpace F] [BorelSpace F]

/-- The exact law of a centered linear image of standard Gaussian noise. -/
noncomputable def centralLinearGaussian (L : F →ₗ[ℝ] E) : Measure E :=
  (stdGaussian F).map L

/-- The whitening operator is derived by adjunction and composition. -/
noncomputable def pulledBackOperator (L : F →ₗ[ℝ] E) (M : E →ₗ[ℝ] E) : F →ₗ[ℝ] F :=
  L.adjoint.comp (M.comp L)

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace F] [BorelSpace F] in
theorem pulledBackOperator_symmetric (L : F →ₗ[ℝ] E) (M : E →ₗ[ℝ] E)
    (hM : M.IsSymmetric) : (pulledBackOperator L M).IsSymmetric :=
  hM.adjoint_conj L

omit [MeasurableSpace E] [BorelSpace E] [MeasurableSpace F] [BorelSpace F] in
theorem operatorQuadratic_pullback (L : F →ₗ[ℝ] E) (M : E →ₗ[ℝ] E) (z : F) :
    operatorQuadratic M (L z) = operatorQuadratic (pulledBackOperator L M) z := by
  exact (L.adjoint_inner_right z (M (L z))).symm

/-- Exact distributional whitening. It uses no inverse or full-rank premise. -/
theorem centralLinearGaussian_quadratic_law (L : F →ₗ[ℝ] E) (M : E →ₗ[ℝ] E) :
    (centralLinearGaussian L).map (operatorQuadratic M) =
      (stdGaussian F).map (operatorQuadratic (pulledBackOperator L M)) := by
  unfold centralLinearGaussian
  rw [Measure.map_map (operatorQuadratic_measurable M)
    L.continuous_of_finiteDimensional.measurable]
  congr 1
  funext z
  exact operatorQuadratic_pullback L M z

/-- General symmetric central reduction for the explicit linear-image Gaussian law. -/
theorem centralLinearGaussian_spectral_law (L : F →ₗ[ℝ] E) (M : E →ₗ[ℝ] E)
    (hM : M.IsSymmetric) :
    (centralLinearGaussian L).map (operatorQuadratic M) =
      gaussianQuadraticLaw ((pulledBackOperator_symmetric L M hM).eigenvalues rfl) := by
  rw [centralLinearGaussian_quadratic_law L M]
  exact symmetric_operatorQuadratic_law _ (pulledBackOperator_symmetric L M hM)

theorem centralLinearGaussian_spectral_tail (L : F →ₗ[ℝ] E) (M : E →ₗ[ℝ] E)
    (hM : M.IsSymmetric) (q : ℝ) :
    tailProbability (centralLinearGaussian L) (operatorQuadratic M) q =
      gaussianWeightedTail ((pulledBackOperator_symmetric L M hM).eigenvalues rfl) q := by
  rw [tailProbability_eq_map _ (operatorQuadratic_measurable M),
    centralLinearGaussian_spectral_law L M hM, gaussianWeightedTail_eq_law]

/-- The remaining spectral and analytic endpoint obligations are explicit inputs. -/
theorem centralLinearGaussian_rational_acceptance
    (L : F →ₗ[ℝ] E) (M : E →ₗ[ℝ] E) (hM : M.IsSymmetric)
    (lower upper : Fin (Module.finrank ℝ F) → ℝ)
    (hl : ∀ i, lower i ≤ (pulledBackOperator_symmetric L M hM).eigenvalues rfl i)
    (hu : ∀ i, (pulledBackOperator_symmetric L M hM).eigenvalues rfl i ≤ upper i)
    (q : ℝ) (pLower pUpper tolerance : ℚ) (estimate : ℝ)
    (hL : (pLower : ℝ) ≤ gaussianWeightedTail lower q)
    (hU : gaussianWeightedTail upper q ≤ (pUpper : ℝ))
    (he : Enclosed estimate (pLower : ℝ) (pUpper : ℝ))
    (ha : acceptsRational pLower pUpper tolerance = true) :
    0 < tailProbability (centralLinearGaussian L) (operatorQuadratic M) q ∧
      |estimate - tailProbability (centralLinearGaussian L) (operatorQuadratic M) q| /
        tailProbability (centralLinearGaussian L) (operatorQuadratic M) q ≤ (tolerance : ℝ) := by
  rw [centralLinearGaussian_spectral_tail L M hM]
  exact gaussianWeightedTail_rational_acceptance lower _ upper hl hu q pLower pUpper
    tolerance estimate hL hU he ha

end KomorebiQCOS
