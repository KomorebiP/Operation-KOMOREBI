import KomorebiSpace.RegularizedHilbertRepair

set_option autoImplicit false

/-!
# Independent primal/dual certificates and inexact correction bounds

The dual witness is arbitrary. Its gap is checked by an exact sum-of-squares
identity. A proposed correction need not solve the normal equation. Every
bound refers to the declared positive parameter and the actual Hilbert norm.
-/
noncomputable section
universe u v
namespace KomorebiSpace.RegularizationCertificates
open scoped RealInnerProductSpace
open RegularizedHilbertRepair
variable {H : Type u} {Y : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable (T : H →L[ℝ] Y) (α : ℝ)

def dual (r z : Y) : ℝ := 2*⟪r,z⟫ - ‖z‖^2 - ‖T.adjoint z‖^2/α

/-- A certificate for all primal vectors, not a test against a finite sample. -/
theorem primal_dual_gap (hα : 0 < α) (r z : Y) (a : H) :
    objective T α r a - dual T α r z =
      ‖T a-r+z‖^2 + ‖T.adjoint z-α • a‖^2/α := by
  simp only [objective, dual, norm_add_sq_real, norm_sub_sq_real,
    inner_sub_left, real_inner_smul_right, ContinuousLinearMap.adjoint_inner_left,
    norm_smul, Real.norm_eq_abs, abs_of_pos hα]
  rw [real_inner_comm z (T a)]
  field_simp
  <;> ring

theorem dual_le_objective (hα : 0 < α) (r z : Y) (a : H) :
    dual T α r z ≤ objective T α r a := by
  have he := primal_dual_gap T α hα r z a
  have hn := div_nonneg (sq_nonneg ‖T.adjoint z-α • a‖) hα.le
  nlinarith [sq_nonneg ‖T a-r+z‖]

/-- The residual is a natural dual witness even when the proposed solver is inexact. -/
theorem residual_witness_gap (hα : 0 < α) (r : Y) (a : H) :
    objective T α r a - dual T α r (r-T a) = ‖gradient T α r a‖^2/α := by
  rw [primal_dual_gap]
  have h1 : T a-r+(r-T a) = 0 := by abel
  have h2 : T.adjoint (r-T a)-α • a = -gradient T α r a := by
    rw [gradient, normal_apply, map_sub]
    abel
  rw [h1, h2, norm_zero, zero_pow (by decide : 2 ≠ 0), zero_add, norm_neg]

theorem dual_at_correction (hα : 0 < α) (r : Y) :
    dual T α r (r-T (correction T α hα r)) = objective T α r (correction T α hα r) := by
  have he := residual_witness_gap T α hα r (correction T α hα r)
  rw [gradient_correction, norm_zero, zero_pow (by decide : 2 ≠ 0), zero_div] at he
  linarith

theorem dual_maximizer (hα : 0 < α) (r z : Y) :
    dual T α r z ≤ dual T α r (r-T (correction T α hα r)) := by
  rw [dual_at_correction]
  exact dual_le_objective T α hα r z _

theorem gap_controls_correction (hα : 0 < α) (r z : Y) (a : H) :
    α*‖a-correction T α hα r‖^2 ≤ objective T α r a - dual T α r z := by
  have he := energy_identity T α hα r a
  have hd := dual_le_objective T α hα r z (correction T α hα r)
  nlinarith [sq_nonneg ‖T (a-correction T α hα r)‖]

/-- A unit support witness is a lower bound against the entire correction ball. -/
theorem budget_witness_bound (r z : Y) (a : H) (M : ℝ)
    (hz : ‖z‖ ≤ 1) (ha : ‖a‖ ≤ M) :
    ⟪r,z⟫-M*‖T.adjoint z‖ ≤ ‖r-T a‖ := by
  have h1 := real_inner_le_norm (r-T a) z
  have h2 := real_inner_le_norm a (T.adjoint z)
  rw [ContinuousLinearMap.adjoint_inner_right] at h2
  have h3 := mul_le_mul_of_nonneg_left hz (norm_nonneg (r-T a))
  have h4 := mul_le_mul_of_nonneg_right ha (norm_nonneg (T.adjoint z))
  rw [inner_sub_left] at h1
  nlinarith

/-- The exact normal equation gives the supporting equality before normalization. -/
theorem budget_support_identity (hα : 0 < α) (r : Y) :
    ⟪r,r-T (correction T α hα r)⟫ - ‖correction T α hα r‖ *
      ‖T.adjoint (r-T (correction T α hα r))‖ =
      ‖r-T (correction T α hα r)‖^2 := by
  have hn := normal_equation T α hα r
  have hi := congrArg (fun z => ⟪correction T α hα r,z⟫) hn
  rw [ContinuousLinearMap.adjoint_inner_right, real_inner_smul_right,
    real_inner_self_eq_norm_sq] at hi
  have he := real_inner_self_eq_norm_sq (r-T (correction T α hα r))
  rw [inner_sub_left] at he
  rw [hn, norm_smul, Real.norm_eq_abs, abs_of_pos hα]
  nlinarith

end KomorebiSpace.RegularizationCertificates
