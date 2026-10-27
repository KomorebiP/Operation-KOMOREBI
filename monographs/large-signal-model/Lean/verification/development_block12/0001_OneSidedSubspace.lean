import KomorebiLSM.SubspaceCoordinates

set_option autoImplicit false
namespace Komorebi.LSM.OneSidedSubspace
open Komorebi.LSM.SubspaceCoordinates
variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
variable [FiniteDimensional ℝ E]

theorem coordinate_lower (P Q : Submodule ℝ E) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ∀ x : P, ‖(x:E)-Q.starProjection x‖ ≤ δ*‖x‖) (x : P) :
    Real.sqrt (1-δ^2) * ‖x‖ ≤ ‖project P Q x‖ := by
  have hres := hgap x
  have hp := Q.norm_sq_eq_add_norm_sq_starProjection (x:E)
  have horth : Qᗮ.starProjection (x:E) = (x:E)-Q.starProjection x := by
    have h := Q.starProjection_add_starProjection_orthogonal (x:E)
    exact eq_sub_of_add_eq' h
  rw [horth] at hp
  have hs : 0 ≤ 1-δ^2 := by nlinarith
  have hsqrt := Real.sq_sqrt hs
  have hn : ‖project P Q x‖ = ‖Q.starProjection (x:E)‖ := rfl
  rw [hn]
  have hres0 := norm_nonneg ((x:E)-Q.starProjection x)
  have hsq : ‖(x:E)-Q.starProjection x‖^2 ≤ (δ*‖x‖)^2 := by nlinarith
  have hx : ‖(x:E)‖ = ‖x‖ := rfl
  rw [hx] at hp
  have hprod : (Real.sqrt (1-δ^2)*‖x‖)^2 = (1-δ^2)*‖x‖^2 := by
    rw [mul_pow, hsqrt]
  nlinarith [Real.sqrt_nonneg (1-δ^2), norm_nonneg (Q.starProjection (x:E)), norm_nonneg x]

theorem coordinate_injective (P Q : Submodule ℝ E) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ∀ x : P, ‖(x:E)-Q.starProjection x‖ ≤ δ*‖x‖) :
    Function.Injective (project P Q) := by
  apply (project P Q).toLinearMap.ker_eq_bot.mp
  apply le_antisymm _ bot_le
  intro x hx
  have hz : project P Q x = 0 := hx
  have hl := coordinate_lower P Q δ hδ hsmall hgap x
  rw [hz, norm_zero] at hl
  have hp : 0 < Real.sqrt (1-δ^2) := Real.sqrt_pos.mpr (by nlinarith)
  have hnorm : ‖x‖ = 0 := by nlinarith [norm_nonneg x]
  simp [norm_eq_zero.mp hnorm]

noncomputable def coordinateEquiv (P Q : Submodule ℝ E) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ∀ x : P, ‖(x:E)-Q.starProjection x‖ ≤ δ*‖x‖)
    (hdim : Module.finrank ℝ P = Module.finrank ℝ Q) : P ≃L[ℝ] Q :=
  (LinearEquiv.ofBijective (project P Q).toLinearMap
    ⟨coordinate_injective P Q δ hδ hsmall hgap,
      (LinearMap.injective_iff_surjective_of_finrank_eq_finrank hdim).mp
        (coordinate_injective P Q δ hδ hsmall hgap)⟩).toContinuousLinearEquiv

theorem coordinate_inverse_bound (P Q : Submodule ℝ E) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ∀ x : P, ‖(x:E)-Q.starProjection x‖ ≤ δ*‖x‖)
    (hdim : Module.finrank ℝ P = Module.finrank ℝ Q) :
    ‖(coordinateEquiv P Q δ hδ hsmall hgap hdim).symm.toContinuousLinearMap‖ ≤
      (Real.sqrt (1-δ^2))⁻¹ := by
  have hp : 0 < Real.sqrt (1-δ^2) := Real.sqrt_pos.mpr (by nlinarith)
  apply ContinuousLinearMap.opNorm_le_bound _ (inv_nonneg.mpr hp.le)
  intro y
  have h := coordinate_lower P Q δ hδ hsmall hgap
    ((coordinateEquiv P Q δ hδ hsmall hgap hdim).symm y)
  have he : project P Q ((coordinateEquiv P Q δ hδ hsmall hgap hdim).symm y) = y :=
    (coordinateEquiv P Q δ hδ hsmall hgap hdim).apply_symm_apply y
  rw [he] at h
  rw [inv_mul_eq_div]
  exact (le_div_iff₀ hp).mpr (by simpa [mul_comm] using h)

end Komorebi.LSM.OneSidedSubspace
