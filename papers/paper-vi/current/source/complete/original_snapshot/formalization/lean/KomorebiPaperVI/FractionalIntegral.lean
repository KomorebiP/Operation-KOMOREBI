import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.Rpow.IntegralRepresentation
import Mathlib.MeasureTheory.Integral.Bochner.ContinuousLinearMap

/-! Author: Komorebi P. A common-measure integral for the actual CFC fractional defect.
The explicit sine normalization and the manuscript norm constants remain to be identified. -/
namespace KomorebiPaperVI.FractionalIntegral
open Set MeasureTheory
open scoped NNReal
variable {R : Type*} [CStarAlgebra R] [PartialOrder R] [StarOrderedRing R]

noncomputable def integrand (a : ℝ≥0) (t : ℝ) (A : R) : R :=
  cfcₙ (Real.rpowIntegrand₀₁ a t) A

theorem common_measure_defect (a : ℝ≥0) (ha : a∈Ioo 0 1) :
    ∃ μ : Measure ℝ,∀ A B : R,0 ≤ A → 0 ≤ B → ∀ C : R,
      IntegrableOn (fun t => C*integrand a t A-integrand a t B*C) (Ioi 0) μ ∧
      C*CFC.nnrpow A a-CFC.nnrpow B a*C=
        ∫ t in Ioi 0,C*integrand a t A-integrand a t B*C ∂μ := by
  obtain ⟨μ,hμ⟩ := CFC.exists_measure_nnrpow_eq_integral_cfcₙ_rpowIntegrand₀₁ R ha
  refine ⟨μ,?_⟩
  intro A B hA hB C
  have hiA : IntegrableOn (integrand a · A) (Ioi 0) μ := (hμ A hA).1
  have hiB : IntegrableOn (integrand a · B) (Ioi 0) μ := (hμ B hB).1
  have hl : IntegrableOn (fun t => C*integrand a t A) (Ioi 0) μ :=
    (ContinuousLinearMap.mul ℝ R C).integrable_comp hiA
  have hr : IntegrableOn (fun t => integrand a t B*C) (Ioi 0) μ :=
    (ContinuousLinearMap.mul ℝ R).flip C |>.integrable_comp hiB
  refine ⟨hl.sub hr,?_⟩
  rw [integral_sub hl hr,integral_const_mul_of_integrable hiA,integral_mul_const_of_integrable hiB]
  exact congrArg₂ (fun x y : R => C*x-y*C) (hμ A hA).2 (hμ B hB).2

theorem scalar_normalizer_positive (a : ℝ) (ha : a∈Ioo 0 1) :
    0 < ∫ t in Ioi 0,Real.rpowIntegrand₀₁ a t 1 :=
  Real.integral_rpowIntegrand₀₁_one_pos ha

theorem scalar_normalized_representation (a x : ℝ) (ha : a∈Ioo 0 1) (hx : 0 ≤ x) :
    x^a=(∫ t in Ioi 0,Real.rpowIntegrand₀₁ a t 1)⁻¹*
      ∫ t in Ioi 0,Real.rpowIntegrand₀₁ a t x :=
  Real.rpow_eq_const_mul_integral ha hx

end KomorebiPaperVI.FractionalIntegral
