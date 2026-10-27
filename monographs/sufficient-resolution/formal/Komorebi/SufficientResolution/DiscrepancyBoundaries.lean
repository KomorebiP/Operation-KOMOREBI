import Komorebi.SufficientResolution.DiscrepancyRule

/-!
# Endpoint and small-data boundaries for discrepancy selection

Positive exact roots require a genuine interior target. The identity example
calculates the actual selected parameter; endpoint failures are not numerical artifacts.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.DiscrepancyBoundaries

open TikhonovConstruction TikhonovBounds DiscrepancyResidual DiscrepancySelection

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

 theorem residual_strictly_below_data (v : V) (hv : A.adjoint v ≠ 0)
    (lam : ℝ) (hl : 0 < lam) : residual A v lam < ‖v‖ := by
  exact (residual_strictMono A v hv hl (by linarith : 0 < lam+1) (by linarith)).trans_le
    (residual_le_data A v (lam+1) (by linarith))

 theorem no_parameter_above_data (v : V) (rho : ℝ) (hr : ‖v‖ < rho) :
    ¬ ∃ lam : ℝ, 0 < lam ∧ residual A v lam = rho := by
  rintro ⟨lam, hl, he⟩
  have h := residual_le_data A v lam hl
  rw [he] at h
  linarith

 theorem no_parameter_at_data_norm (v : V) (hv : A.adjoint v ≠ 0) :
    ¬ ∃ lam : ℝ, 0 < lam ∧ residual A v lam = ‖v‖ := by
  rintro ⟨lam, hl, he⟩
  have h := residual_strictly_below_data A v hv lam hl
  rw [he] at h
  exact lt_irrefl _ h

 theorem zero_residual_iff_zero_data (v : V) (lam : ℝ) (hl : 0 < lam) :
    residual A v lam = 0 ↔ v = 0 := by
  constructor
  · intro h
    have hv : A (regularized A lam hl v) = v := by
      apply sub_eq_zero.mp
      apply norm_eq_zero.mp
      simpa only [DiscrepancyResidual.residual, recoveryAt_pos A lam hl] using h
    have he := solution_energy A lam hl v
    rw [hv, real_inner_self_eq_norm_sq] at he
    have hz : ‖regularized A lam hl v‖^2 = 0 := by nlinarith
    have hx := norm_eq_zero.mp (sq_eq_zero_iff.mp hz)
    rw [hx, map_zero] at hv
    exact hv.symm
  · rintro rfl; simp [DiscrepancyResidual.residual]

 theorem no_zero_target_for_nonzero_data (v : V) (hv : v ≠ 0) :
    ¬ ∃ lam : ℝ, 0 < lam ∧ residual A v lam = 0 := by
  rintro ⟨lam, hl, he⟩
  exact hv ((zero_residual_iff_zero_data A v lam hl).mp he)

 theorem orthogonal_data_has_no_interior_root (v : V) (hv : A.adjoint v = 0)
    (rho : ℝ) (hr : rho < ‖v‖) :
    ¬ ∃ lam : ℝ, 0 < lam ∧ residual A v lam = rho := by
  rintro ⟨lam, hl, he⟩
  rw [residual_constant_of_adjoint_zero A v hv lam hl] at he
  linarith

/-- Actual identity-operator root, with no finite approximation to the parameter. -/
 theorem identity_parameter_formula (v rho : ℝ) (hr : 0 < rho) (hv : rho < v) :
    let lam := rho/(v-rho)
    let hl : 0 < lam := div_pos hr (sub_pos.mpr hv)
    regularized (ContinuousLinearMap.id ℝ ℝ) lam hl v = v-rho ∧
      residual (ContinuousLinearMap.id ℝ ℝ) v lam = rho := by
  dsimp only
  have hl : 0 < rho/(v-rho) := div_pos hr (sub_pos.mpr hv)
  have he : regularized (ContinuousLinearMap.id ℝ ℝ) (rho/(v-rho)) hl v = v-rho := by
    symm
    apply (normal_equation_iff (ContinuousLinearMap.id ℝ ℝ) (rho/(v-rho)) hl v _).mp
    simp only [normal_apply, ContinuousLinearMap.adjoint_id, ContinuousLinearMap.id_apply,
      smul_eq_mul]
    field_simp [ne_of_gt (sub_pos.mpr hv)]
    ring
  refine ⟨he, ?_⟩
  rw [DiscrepancyResidual.residual, recoveryAt_pos _ _ hl, he]
  simp only [ContinuousLinearMap.id_apply, sub_sub_cancel_left, norm_neg, Real.norm_eq_abs,
    abs_of_pos hr]

end Komorebi.SufficientResolution.DiscrepancyBoundaries
