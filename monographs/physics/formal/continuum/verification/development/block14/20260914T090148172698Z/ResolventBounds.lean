module
public import KomorebiPhysics.ResolventCommutator

/-! The nonreal norm bound is derived from the imaginary part of the
quadratic pairing and genuine inverse identities. It is not an assumption
inside the commutator certificate. Symmetry plus an existing inverse suffices. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace ResolventDomain

variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable {T : H →ₗ.[ℂ] H}

theorem shifted_inner_im (hT : GraphDomain.IsSymmetric T) (z : ℂ) (x : T.domain) :
    (inner ℂ (x : H) (shifted T z x)).im = -z.im * ‖(x : H)‖ ^ 2 := by
  simp only [shifted_apply, inner_sub_right, inner_smul_right, Complex.sub_im,
    Complex.mul_im, GraphDomain.symmetric_self_im_zero T hT x,
    inner_self_im, inner_self_eq_norm_sq]
  ring

/-- The imaginary spectral distance controls the actual shifted action. -/
theorem shifted_coercive (hT : GraphDomain.IsSymmetric T) (z : ℂ) (x : T.domain) :
    |z.im| * ‖(x : H)‖ ≤ ‖shifted T z x‖ := by
  have h := (Complex.abs_im_le_norm (inner ℂ (x : H) (shifted T z x))).trans
    (norm_inner_le_norm (x : H) (shifted T z x))
  rw [shifted_inner_im hT z x, abs_mul, abs_neg, abs_of_nonneg (sq_nonneg _)] at h
  by_cases hx : ‖(x : H)‖ = 0
  · simp only [hx, mul_zero]
    exact norm_nonneg _
  · have hp : 0 < ‖(x : H)‖ := lt_of_le_of_ne (norm_nonneg _) (Ne.symm hx)
    nlinarith

namespace Certificate
variable {z : ℂ} (R : Certificate T z)

theorem nonreal_state_bound (hT : GraphDomain.IsSymmetric T) (hz : z.im ≠ 0) (x : H) :
    ‖R.op x‖ ≤ |z.im|⁻¹ * ‖x‖ := by
  have h := shifted_coercive hT z (R.lift x)
  rw [R.shifted_lift, R.lift_coe] at h
  have hp : 0 < |z.im| := abs_pos.mpr hz
  calc
    _ ≤ ‖x‖ / |z.im| := (le_div_iff₀ hp).mpr (by simpa only [mul_comm] using h)
    _ = _ := by ring

theorem nonreal_norm_bound (hT : GraphDomain.IsSymmetric T) (hz : z.im ≠ 0) :
    ‖R.op‖ ≤ |z.im|⁻¹ :=
  R.op.opNorm_le_bound (inv_nonneg.mpr (abs_nonneg _)) (R.nonreal_state_bound hT hz)

theorem nonreal_commutator_bound {P : H →L[ℂ] H} (B : BoundedCommutator T P)
    (hT : GraphDomain.IsSymmetric T) (hz : z.im ≠ 0) :
    ‖commutator R.op P‖ ≤ ‖B.bound‖ / z.im ^ 2 := by
  have h := R.commutator_norm_bound_of_le B (R.nonreal_norm_bound hT hz)
  convert h using 1
  rw [inv_pow, sq_abs, div_eq_mul_inv]
  ring

end Certificate

/-- Literal imaginary-axis estimate (6.56), with eta nonzero. -/
theorem imaginary_axis_commutator_bound (η : ℝ) (hη : η ≠ 0)
    (R : Certificate T ((η : ℂ) * Complex.I)) {P : H →L[ℂ] H}
    (B : BoundedCommutator T P) (hT : GraphDomain.IsSymmetric T) :
    ‖commutator R.op P‖ ≤ ‖B.bound‖ / η ^ 2 := by
  have him : (((η : ℂ) * Complex.I).im) = η := by simp
  simpa only [him] using R.nonreal_commutator_bound B hT (by simpa only [him] using hη)

end ResolventDomain
end KomorebiPhysics
