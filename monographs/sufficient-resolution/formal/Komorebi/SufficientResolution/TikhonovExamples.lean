import Komorebi.SufficientResolution.TikhonovPerturbation

/-!
# Exact scalar sharpness and vanishing-parameter boundaries

All examples use the actual constructed regularized operator. They are real-variable
proofs, not sampled floating-point tests or substituted closed-form definitions.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovExamples

open TikhonovConstruction TikhonovBounds

/-- Scalar forward operator as an actual continuous linear map. -/
def scalar (c : ℝ) : ℝ →L[ℝ] ℝ := c • ContinuousLinearMap.id ℝ ℝ

 theorem scalar_apply (c x : ℝ) : scalar c x = c*x := rfl

 theorem scalar_adjoint_apply (c x : ℝ) : (scalar c).adjoint x = c*x := by
  apply ext_inner_right ℝ
  intro y
  rw [ContinuousLinearMap.adjoint_inner_left, scalar_apply]
  simp only [RCLike.inner_apply, conj_trivial]
  ring

 theorem scalar_regularized (c lam : ℝ) (hlam : 0 < lam) (v : ℝ) :
    regularized (scalar c) lam hlam v = c*v/(c^2+lam) := by
  symm
  apply (normal_equation_iff (scalar c) lam hlam v _).mp
  rw [normal_apply, scalar_adjoint_apply, scalar_apply, scalar_adjoint_apply]
  have hd : c^2+lam ≠ 0 := ne_of_gt (by positivity)
  simp only [smul_eq_mul]
  field_simp

 theorem scalar_bias (c lam : ℝ) (hlam : 0 < lam) (g : ℝ) :
    regularized (scalar c) lam hlam (scalar c g)-g = -lam*g/(c^2+lam) := by
  rw [scalar_regularized, scalar_apply]
  have hd : c^2+lam ≠ 0 := ne_of_gt (by positivity)
  field_simp
  ring

 theorem zero_forward_regularized (lam : ℝ) (hlam : 0 < lam) (v : ℝ) :
    regularized (scalar 0) lam hlam v = 0 := by
  rw [scalar_regularized]
  simp

 theorem kernel_source_not_recovered (lam : ℝ) (hlam : 0 < lam) :
    ‖regularized (scalar 0) lam hlam (scalar 0 1)-1‖ = 1 := by
  rw [zero_forward_regularized]
  norm_num

 theorem scalar_matched_parameter (r : ℝ) (hr : 0 < r) (v : ℝ) :
    regularized (scalar r) (r^2) (sq_pos_of_pos hr) v = v/(2*r) := by
  rw [scalar_regularized]
  field_simp
  ring

 theorem sharp_noise_squared (r : ℝ) (hr : 0 < r) (v : ℝ) :
    4*(r^2)*‖regularized (scalar r) (r^2) (sq_pos_of_pos hr) v‖^2 = ‖v‖^2 := by
  rw [scalar_matched_parameter r hr, Real.norm_eq_abs, Real.norm_eq_abs, sq_abs, sq_abs]
  field_simp
  ring

 theorem matched_parameter_retains_half (r : ℝ) (hr : 0 < r) :
    regularized (scalar r) (r^2) (sq_pos_of_pos hr) (scalar r 1) = 1/2 := by
  rw [scalar_matched_parameter r hr, scalar_apply]
  field_simp

/-- Small data alone do not give uniform recovery control when lambda can vanish. -/
 theorem arbitrarily_small_data_unit_recovery (eps : ℝ) (heps : 0 < eps) :
    ∃ r : ℝ, ∃ hr : 0 < r, ∃ e : ℝ,
      ‖e‖ < eps ∧ regularized (scalar r) (r^2) (sq_pos_of_pos hr) e = 1 := by
  let r := eps/4
  have hr : 0 < r := by dsimp [r]; positivity
  refine ⟨r, hr, 2*r, ?_, ?_⟩
  · rw [Real.norm_eq_abs, abs_of_pos (mul_pos (by norm_num) hr)]
    dsimp [r]
    linarith
  · rw [scalar_matched_parameter r hr]
    exact div_self (ne_of_gt (mul_pos (by norm_num) hr))

/-- The positivity requirement cannot be dropped from uniqueness. -/
 theorem zero_parameter_not_unique :
    (fun x : ℝ => ‖scalar 0 x‖^2+(0:ℝ)*‖x‖^2) 0 =
    (fun x : ℝ => ‖scalar 0 x‖^2+(0:ℝ)*‖x‖^2) 1 ∧ (0:ℝ) ≠ 1 := by
  constructor
  · simp [scalar_apply]
  · norm_num

end Komorebi.SufficientResolution.TikhonovExamples
