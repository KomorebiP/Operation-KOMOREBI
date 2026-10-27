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

theorem reverse_coordinate_lower (P Q : Submodule ℝ E) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ∀ x : P, ‖(x:E)-Q.starProjection x‖ ≤ δ*‖x‖)
    (hdim : Module.finrank ℝ P = Module.finrank ℝ Q) (y : Q) :
    Real.sqrt (1-δ^2) * ‖y‖ ≤ ‖project Q P y‖ := by
  let e := coordinateEquiv P Q δ hδ hsmall hgap hdim
  let x : P := e.symm y
  have hxy : project P Q x = y := e.apply_symm_apply y
  have hxy' : Q.starProjection (x:E) = (y:E) := congrArg Subtype.val hxy
  have hl := coordinate_lower P Q δ hδ hsmall hgap x
  rw [hxy] at hl
  have hi : inner ℝ (P.starProjection (y:E)) (x:E) = ‖y‖^2 := by
    rw [P.inner_starProjection_left_eq_right, P.starProjection_eq_self_iff.mpr x.property,
      ← Q.starProjection_eq_self_iff.mpr y.property,
      Q.inner_starProjection_left_eq_right, hxy']
    simp
  have hc := real_inner_le_norm (P.starProjection (y:E)) (x:E)
  rw [hi] at hc
  have hp : 0 < Real.sqrt (1-δ^2) := Real.sqrt_pos.mpr (by nlinarith)
  have hmul := mul_le_mul_of_nonneg_left hc hp.le
  have hmul' := mul_le_mul_of_nonneg_left hl (norm_nonneg (P.starProjection (y:E)))
  have hn : ‖project Q P y‖ = ‖P.starProjection (y:E)‖ := rfl
  rw [hn]
  by_cases hy : y = 0
  · simp [hy]
  · have hypos := norm_pos_iff.mpr hy
    have hxnorm : ‖(x:E)‖ = ‖x‖ := rfl
    rw [hxnorm] at hmul
    nlinarith

theorem reverse_residual (P Q : Submodule ℝ E) (δ : ℝ) (hδ : 0 ≤ δ)
    (hsmall : δ < 1) (hgap : ∀ x : P, ‖(x:E)-Q.starProjection x‖ ≤ δ*‖x‖)
    (hdim : Module.finrank ℝ P = Module.finrank ℝ Q) (y : Q) :
    ‖(y:E)-P.starProjection y‖ ≤ δ*‖y‖ := by
  have hl := reverse_coordinate_lower P Q δ hδ hsmall hgap hdim y
  have hn : ‖project Q P y‖ = ‖P.starProjection (y:E)‖ := rfl
  rw [hn] at hl
  have hp := P.norm_sq_eq_add_norm_sq_starProjection (y:E)
  have horth : Pᗮ.starProjection (y:E) = (y:E)-P.starProjection y :=
    eq_sub_of_add_eq' (P.starProjection_add_starProjection_orthogonal (y:E))
  rw [horth] at hp
  have hynorm : ‖(y:E)‖ = ‖y‖ := rfl
  rw [hynorm] at hp
  have hs : 0 ≤ 1-δ^2 := by nlinarith
  have hprod : (Real.sqrt (1-δ^2)*‖y‖)^2 = (1-δ^2)*‖y‖^2 := by
    rw [mul_pow, Real.sq_sqrt hs]
  have hsquare : (Real.sqrt (1-δ^2)*‖y‖)^2 ≤ ‖P.starProjection (y:E)‖^2 :=
    pow_le_pow_left₀ (mul_nonneg (Real.sqrt_nonneg _) (norm_nonneg _)) hl 2
  nlinarith [norm_nonneg ((y:E)-P.starProjection y), mul_nonneg hδ (norm_nonneg y)]

end Komorebi.LSM.OneSidedSubspace
