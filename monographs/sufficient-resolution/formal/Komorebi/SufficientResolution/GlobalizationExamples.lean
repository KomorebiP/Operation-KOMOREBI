import Komorebi.SufficientResolution.FiniteGlobalization
import Mathlib.Tactic.NormNum

/-!
# Exact obstruction and conditioning counterexamples

All examples are universal real equalities or inequalities. A zero residual does
not remove obstruction, and no conditioning constant is uniform across all
nonzero scalar compatibility operators.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.GlobalizationExamples

open OrthogonalResolution HilbertConditioning

/-- An actual bounded scalar compatibility operator. -/
def scaledCompatibility (s : ℝ) : ℝ →L[ℝ] ℝ := s • ContinuousLinearMap.id ℝ ℝ

 theorem scaledCompatibility_apply (s x : ℝ) : scaledCompatibility s x = s * x := rfl

 theorem scalar_kernel (s : ℝ) (hs : s ≠ 0) : (scaledCompatibility s).ker = ⊥ := by
  ext x
  change s * x = 0 ↔ x = 0
  exact mul_eq_zero.trans (or_iff_right hs)

 theorem zero_space_distance (v : ℝ) :
    Metric.infDist v ((⊥ : Submodule ℝ ℝ) : Set ℝ) = |v| := by
  rw [infDist_eq_error]
  simp [realized, Real.norm_eq_abs]

 theorem pure_obstruction :
    obstruction (⊥ : Submodule ℝ ℝ) ⊤ 1 = 1 ∧
    inconsistency (⊤ : Submodule ℝ ℝ) 1 = 0 ∧
    Metric.infDist (1 : ℝ) ((⊥ : Submodule ℝ ℝ) : Set ℝ) = 1 := by
  simp [obstruction, inconsistency, Submodule.starProjection_top]

/-- Every residual-only bound fails for A=0 and delta=0, at the single exact input 1. -/
 theorem zero_residual_cannot_bound_obstruction (c : ℝ) :
    ¬ (∀ v : ℝ, Metric.infDist v ((⊥ : Submodule ℝ ℝ) : Set ℝ) ≤
      c * ‖(0 : ℝ →L[ℝ] ℝ) v‖) := by
  intro h
  have hb := h 1
  norm_num [zero_space_distance] at hb

 theorem scalar_coercivity (s : ℝ) (hs : 0 < s) :
    CoerciveOffKernel (scaledCompatibility s) s := by
  intro x _
  simp only [scaledCompatibility_apply, norm_mul, Real.norm_eq_abs, abs_of_pos hs, le_refl]

 theorem scalar_residual_at_one (s : ℝ) (hs : 0 ≤ s) :
    ‖scaledCompatibility s 1‖ = s := by
  simp [scaledCompatibility_apply, Real.norm_eq_abs, abs_of_nonneg hs]

 theorem scalar_conditioned_bound_attained (s : ℝ) (hs : 0 < s) :
    Metric.infDist (1 : ℝ) ((⊥ : Submodule ℝ ℝ) : Set ℝ) ^ 2 =
      (‖scaledCompatibility s 1‖ / s) ^ 2 := by
  rw [zero_space_distance, scalar_residual_at_one s hs.le, div_self hs.ne']
  norm_num

/-- A small nonzero residual may coexist with unit reconstruction error even when the chain is exact. -/
 theorem arbitrarily_small_residual_unit_error (epsilon : ℝ) (he : 0 < epsilon) :
    ∃ s : ℝ, 0 < s ∧ (scaledCompatibility s).ker = ⊥ ∧
      ‖scaledCompatibility s 1‖ = epsilon ∧
      Metric.infDist (1 : ℝ) ((⊥ : Submodule ℝ ℝ) : Set ℝ) = 1 := by
  refine ⟨epsilon, he, scalar_kernel epsilon he.ne', scalar_residual_at_one epsilon he.le, ?_⟩
  norm_num [zero_space_distance]

/-- No fixed nonnegative multiplier works across all exact scalar presentations. -/
 theorem no_uniform_conditioning_over_scalar_family (c : ℝ) (hc : 0 ≤ c) :
    ∃ s : ℝ, 0 < s ∧ (scaledCompatibility s).ker = ⊥ ∧
      c * ‖scaledCompatibility s 1‖ <
      Metric.infDist (1 : ℝ) ((⊥ : Submodule ℝ ℝ) : Set ℝ) := by
  have hd : 0 < c+1 := by linarith
  refine ⟨(c+1)⁻¹, inv_pos.mpr hd, scalar_kernel _ (inv_ne_zero hd.ne'), ?_⟩
  rw [scalar_residual_at_one _ (inv_nonneg.mpr hd.le), zero_space_distance]
  norm_num only [abs_one]
  rw [← div_eq_mul_inv]
  exact (div_lt_one hd).mpr (by linarith)

/-- Enlarging realizations removes pure obstruction, but does not change compatibility. -/
 theorem pure_obstruction_refinement :
    ‖obstruction (⊥ : Submodule ℝ ℝ) ⊤ 1‖ ^ 2 = 1 ∧
    ‖obstruction (⊤ : Submodule ℝ ℝ) ⊤ 1‖ ^ 2 = 0 ∧
    Metric.infDist (1 : ℝ) ((⊤ : Submodule ℝ ℝ) : Set ℝ) = 0 := by
  simp [obstruction, Submodule.starProjection_top, Metric.infDist_zero_of_mem]

end Komorebi.SufficientResolution.GlobalizationExamples
