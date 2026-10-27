import Komorebi.SufficientResolution.ReconstructionGlobalization

/-!
# Exact source-reconstruction boundary examples

The zero map separates best fit from recovery of every source. Nonzero scalar
maps show that source sensitivity cannot be controlled without A's conditioning.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.ReconstructionExamples

open MinimumNormReconstruction MinimumNormOptimality SourceConditioning

/-- Real scalar forward map, with the Euclidean norm. -/
def scalar (c : ℝ) : ℝ →L[ℝ] ℝ := c • ContinuousLinearMap.id ℝ ℝ

 theorem scalar_apply (c x : ℝ) : scalar c x = c*x := rfl

 theorem scalar_injective (c : ℝ) (hc : c ≠ 0) : Function.Injective (scalar c) := by
  intro x y h
  exact mul_left_cancel₀ hc h

 theorem scalar_surjective (c : ℝ) (hc : c ≠ 0) : Function.Surjective (scalar c) := by
  intro v
  refine ⟨v/c, ?_⟩
  change c*(v/c)=v
  field_simp

 theorem scalar_range (c : ℝ) (hc : c ≠ 0) : (scalar c).range = ⊤ :=
  LinearMap.range_eq_top.mpr (scalar_surjective c hc)

 theorem scalar_recover (c : ℝ) (hc : c ≠ 0) (v : ℝ) :
    recover (scalar c) v = v/c := by
  apply scalar_injective c hc
  rw [image_recover]
  have hv : v ∈ (scalar c).range := scalar_surjective c hc v
  rw [Submodule.starProjection_eq_self_iff.mpr hv]
  change v = c*(v/c)
  field_simp

 theorem scalar_recover_norm (c : ℝ) (hc : 0 < c) (v : ℝ) :
    ‖recover (scalar c) v‖ = ‖v‖/c := by
  rw [scalar_recover c hc.ne', norm_div, Real.norm_of_nonneg hc.le]

 theorem scalar_coercivity (c : ℝ) (hc : 0 ≤ c) :
    HilbertConditioning.CoerciveOffKernel (scalar c) c := by
  intro x _
  change c * ‖x‖ ≤ ‖c*x‖
  rw [norm_mul, Real.norm_of_nonneg hc]

 theorem source_bound_attained (c : ℝ) (hc : 0 < c) :
    ‖recover (scalar c) 1‖ = 1/c := by
  rw [scalar_recover_norm c hc, norm_one]

/-- The canonical source is zero even though every source has the same zero image. -/
 theorem zero_map_recovery (v : ℝ) : recover (0 : ℝ →L[ℝ] ℝ) v = 0 := by
  apply (recover_eq_zero_iff (0 : ℝ →L[ℝ] ℝ) v).mpr
  simp

 theorem zero_map_every_source_best (v g : ℝ) :
    ‖v-(0 : ℝ →L[ℝ] ℝ) g‖ =
      ‖v-(0 : ℝ →L[ℝ] ℝ) (recover (0 : ℝ →L[ℝ] ℝ) v)‖ := by simp

 theorem zero_map_not_full_source_recovery :
    recover (0 : ℝ →L[ℝ] ℝ) ((0 : ℝ →L[ℝ] ℝ) 1) ≠ 1 := by
  rw [zero_map_recovery]
  norm_num

 theorem arbitrarily_small_data_unit_source (epsilon : ℝ) (he : 0 < epsilon) :
    ∃ c : ℝ, 0 < c ∧ ‖c‖ < epsilon ∧ ‖recover (scalar c) c‖ = 1 := by
  refine ⟨epsilon/2, half_pos he, ?_, ?_⟩
  · rw [Real.norm_of_nonneg (half_pos he).le]
    exact half_lt_self he
  · rw [scalar_recover _ (half_pos he).ne', div_self (half_pos he).ne', norm_one]

/-- No constant controls inverse sensitivity over every nonzero scalar forward map. -/
 theorem no_uniform_source_conditioning :
    ¬ ∃ C : ℝ, ∀ c : ℝ, 0 < c → ∀ v : ℝ, ‖recover (scalar c) v‖ ≤ C*‖v‖ := by
  rintro ⟨C,hC⟩
  have hnonneg : 0 ≤ C := by
    have hh := hC 1 zero_lt_one 1
    rw [source_bound_attained 1 zero_lt_one, div_one, norm_one, mul_one] at hh
    linarith
  let c : ℝ := (C+1)⁻¹
  have hc : 0 < c := inv_pos.mpr (by linarith)
  have hh := hC c hc c
  rw [scalar_recover _ hc.ne', div_self hc.ne', norm_one, Real.norm_of_nonneg hc.le] at hh
  have hlt : C*c < 1 := by
    change C*(C+1)⁻¹ < 1
    rw [← div_eq_mul_inv, div_lt_one (by linarith : 0 < C+1)]
    linarith
  linarith

end Komorebi.SufficientResolution.ReconstructionExamples
