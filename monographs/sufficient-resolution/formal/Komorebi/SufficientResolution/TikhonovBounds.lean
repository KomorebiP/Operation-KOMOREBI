import Komorebi.SufficientResolution.TikhonovOptimality

/-!
# Rank-independent fixed-parameter bounds

The sharp noise factor is 1/(2 sqrt lambda). Bounds do not assume that A has
closed range. They are fixed-positive-parameter bounds, not uniform inversion
claims as lambda tends to zero.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.TikhonovBounds

open TikhonovConstruction TikhonovOptimality

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V) (lam : ℝ)

 theorem normal_lower_bound (x : G) :
    lam * ‖x‖ ≤ ‖normal A lam x‖ := by
  by_cases hx : x = 0
  · simp [hx]
  · have hp := norm_pos_iff.mpr hx
    have hc := real_inner_le_norm (normal A lam x) x
    rw [normal_energy] at hc
    nlinarith [sq_nonneg ‖A x‖]

 theorem resolvent_bound (hlam : 0 < lam) (x : G) :
    ‖resolvent A lam hlam x‖ ≤ ‖x‖/lam := by
  apply (le_div_iff₀ hlam).mpr
  have h := normal_lower_bound A lam (resolvent A lam hlam x)
  rw [normal_resolvent] at h
  nlinarith

 theorem resolvent_opNorm_bound (hlam : 0 < lam) :
    ‖resolvent A lam hlam‖ ≤ lam⁻¹ := by
  apply (resolvent A lam hlam).opNorm_le_bound (inv_nonneg.mpr hlam.le)
  intro x
  simpa only [div_eq_mul_inv, mul_comm] using resolvent_bound A lam hlam x

 theorem regularized_bound_squared (hlam : 0 < lam) (v : V) :
    4*lam*‖regularized A lam hlam v‖^2 ≤ ‖v‖^2 := by
  have he := solution_energy A lam hlam v
  have hc := real_inner_le_norm v (A (regularized A lam hlam v))
  nlinarith [sq_nonneg (2*‖A (regularized A lam hlam v)‖-‖v‖)]

 theorem regularized_bound (hlam : 0 < lam) (v : V) :
    ‖regularized A lam hlam v‖ ≤ ‖v‖/(2*Real.sqrt lam) := by
  have hs := Real.sq_sqrt hlam.le
  have hp : 0 < 2*Real.sqrt lam := mul_pos (by norm_num) (Real.sqrt_pos.mpr hlam)
  apply (le_div_iff₀ hp).mpr
  apply (sq_le_sq₀ (mul_nonneg (norm_nonneg _) hp.le) (norm_nonneg _)).mp
  calc
    (‖regularized A lam hlam v‖*(2*Real.sqrt lam))^2 =
        4*lam*‖regularized A lam hlam v‖^2 := by rw [mul_pow, mul_pow, hs]; ring
    _ ≤ ‖v‖^2 := regularized_bound_squared A lam hlam v

 theorem regularized_opNorm_bound (hlam : 0 < lam) :
    ‖regularized A lam hlam‖ ≤ (2*Real.sqrt lam)⁻¹ := by
  apply (regularized A lam hlam).opNorm_le_bound (by positivity)
  intro v
  simpa only [div_eq_mul_inv, mul_comm] using regularized_bound A lam hlam v

 theorem data_noise_bound (hlam : 0 < lam) (v w : V) :
    ‖regularized A lam hlam v-regularized A lam hlam w‖ ≤
      ‖v-w‖/(2*Real.sqrt lam) := by
  rw [← map_sub]
  exact regularized_bound A lam hlam (v-w)

 theorem fitted_data_bound (hlam : 0 < lam) (v : V) :
    ‖A (regularized A lam hlam v)‖ ≤ ‖v‖ := by
  have he := solution_energy A lam hlam v
  have hc := real_inner_le_norm v (A (regularized A lam hlam v))
  have hn := mul_nonneg hlam.le (sq_nonneg ‖regularized A lam hlam v‖)
  nlinarith [norm_nonneg (A (regularized A lam hlam v)), norm_nonneg v]

 theorem residual_data_bound (hlam : 0 < lam) (v : V) :
    ‖A (regularized A lam hlam v)-v‖ ≤ ‖v‖ := by
  have h := objective_zero_comparison A lam hlam v
  unfold objective at h
  have hn := mul_nonneg hlam.le (sq_nonneg ‖regularized A lam hlam v‖)
  exact (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mp (by linarith)

 theorem approximate_solver_identity (hlam : 0 < lam) (v : V) (x : G) :
    x-regularized A lam hlam v =
      resolvent A lam hlam (normal A lam x-A.adjoint v) := by
  rw [map_sub, resolvent_normal]
  rfl

 theorem approximate_solver_bound (hlam : 0 < lam) (v : V) (x : G) :
    ‖x-regularized A lam hlam v‖ ≤ ‖normal A lam x-A.adjoint v‖/lam := by
  rw [approximate_solver_identity]
  exact resolvent_bound A lam hlam _

 theorem source_kernel_orthogonal (hlam : 0 < lam) (v : V) :
    regularized A lam hlam v ∈ A.kerᗮ := by
  intro k hk
  have he := residual_pairing A lam hlam v k
  change A k = 0 at hk
  rw [hk, inner_zero_right, zero_add] at he
  have hz : inner ℝ (regularized A lam hlam v) k = 0 := (mul_eq_zero.mp he).resolve_left hlam.ne'
  exact inner_eq_zero_symm.mp hz

 theorem regularized_ignores_range_orthogonal (hlam : 0 < lam) (e : V)
    (he : e ∈ A.rangeᗮ) : regularized A lam hlam e = 0 := by
  have hz : A.adjoint e = 0 := by
    apply ext_inner_right ℝ
    intro x
    rw [ContinuousLinearMap.adjoint_inner_left, inner_zero_left]
    exact inner_eq_zero_symm.mp (he _ (A.mem_range_self x))
  change resolvent A lam hlam (A.adjoint e) = 0
  rw [hz, map_zero]

 theorem orthogonal_data_invariance (hlam : 0 < lam) (v e : V)
    (he : e ∈ A.rangeᗮ) : regularized A lam hlam (v+e) = regularized A lam hlam v := by
  rw [map_add, regularized_ignores_range_orthogonal A lam hlam e he, add_zero]

end Komorebi.SufficientResolution.TikhonovBounds
