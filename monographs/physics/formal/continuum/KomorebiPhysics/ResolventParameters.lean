module
public import KomorebiPhysics.ResolventBounds

/-! Added support: comparison of two genuine resolvents, with the scalar
orientation and both domain inverses retained. No analytic family is assumed. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace ResolventDomain
variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable {T : H →ₗ.[ℂ] H}

theorem shifted_change (z w : ℂ) (x : T.domain) :
    shifted T z x = shifted T w x + (w-z) • (x : H) := by
  simp only [shifted_apply, sub_smul]
  abel

namespace Certificate
variable {z w : ℂ} (R : Certificate T z) (S : Certificate T w)

theorem difference_vector (x : H) :
    R.op x - S.op x = (z-w) • R.op (S.op x) := by
  have h := congrArg R.op (shifted_change z w (S.lift x))
  simp only [R.left_inverse, S.shifted_lift, S.lift_coe, map_add, map_smul] at h
  calc
    R.op x - S.op x = R.op x - (R.op x + (w-z) • R.op (S.op x)) :=
      congrArg (fun y => R.op x - y) h
    _ = -((w-z) • R.op (S.op x)) := by abel
    _ = _ := by rw [← neg_smul, neg_sub]

/-- The true two-parameter resolvent identity, with sign z-w. -/
theorem difference_identity : R.op - S.op = (z-w) • (R.op * S.op) := by
  ext x
  exact R.difference_vector S x

theorem difference_norm_bound :
    ‖R.op - S.op‖ ≤ ‖z-w‖ * ‖R.op‖ * ‖S.op‖ := by
  rw [R.difference_identity S, norm_smul, mul_assoc]
  exact mul_le_mul_of_nonneg_left (norm_mul_le _ _) (norm_nonneg _)

theorem commute : R.op * S.op = S.op * R.op := by
  by_cases hzw : z = w
  · subst w
    rw [R.unique S]
  · have h1 := R.difference_identity S
    have h2 := S.difference_identity R
    have h : (z-w) • (R.op * S.op) = (z-w) • (S.op * R.op) := by
      calc
        _ = R.op - S.op := h1.symm
        _ = -(S.op - R.op) := by abel
        _ = -((w-z) • (S.op * R.op)) := by rw [h2]
        _ = _ := by rw [← neg_smul, neg_sub]
    exact (smul_right_injective (H →L[ℂ] H) (sub_ne_zero.mpr hzw)) h

theorem difference_norm_nonreal (hT : GraphDomain.IsSymmetric T)
    (hz : z.im ≠ 0) (hw : w.im ≠ 0) :
    ‖R.op - S.op‖ ≤ ‖z-w‖ / (|z.im| * |w.im|) := by
  calc
    _ ≤ ‖z-w‖ * ‖R.op‖ * ‖S.op‖ := R.difference_norm_bound S
    _ ≤ ‖z-w‖ * |z.im|⁻¹ * |w.im|⁻¹ := by
      gcongr
      · exact R.nonreal_norm_bound hT hz
      · exact S.nonreal_norm_bound hT hw
    _ = _ := by rw [div_eq_mul_inv, mul_inv]; ring

end Certificate
end ResolventDomain
end KomorebiPhysics
