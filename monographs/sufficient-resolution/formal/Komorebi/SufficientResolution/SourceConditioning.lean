import Komorebi.SufficientResolution.MinimumNormOptimality
import Komorebi.SufficientResolution.HilbertConditioning

/-!
# Source conditioning is not compatibility conditioning

The positive constant alpha belongs to A on ker(A)^perp. It is unrelated to
sigma for a compatibility operator. Bounds concern a fixed, known linear map.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.SourceConditioning

open MinimumNormReconstruction MinimumNormOptimality HilbertConditioning

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable (A : G →L[ℝ] V) [CompleteSpace A.range]

/-- Closed range supplies some positive source coercivity, including A=0. -/
 theorem exists_source_coercivity :
    ∃ alpha : ℝ, 0 < alpha ∧ CoerciveOffKernel A alpha := by
  let c : ℝ := ‖recover A‖ + 1
  have hc : 0 < c := by dsimp [c]; linarith [norm_nonneg (recover A)]
  refine ⟨c⁻¹, inv_pos.mpr hc, ?_⟩
  intro g hg
  have hr : recover A (A g) = g := (exact_source_recovery_iff A g).mpr hg
  have hb : ‖g‖ ≤ c * ‖A g‖ := by
    calc
      ‖g‖ = ‖recover A (A g)‖ := congrArg norm hr.symm
      _ ≤ ‖recover A‖ * ‖A g‖ := (recover A).le_opNorm _
      _ ≤ c * ‖A g‖ := mul_le_mul_of_nonneg_right (by dsimp [c]; linarith) (norm_nonneg _)
  calc
    c⁻¹ * ‖g‖ ≤ c⁻¹ * (c * ‖A g‖) := mul_le_mul_of_nonneg_left hb (inv_nonneg.mpr hc.le)
    _ = ‖A g‖ := by rw [← mul_assoc, inv_mul_cancel₀ hc.ne', one_mul]

 theorem recover_projected_bound (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (v : V) :
    ‖recover A v‖ ≤ ‖A.range.starProjection v‖ / alpha := by
  apply (le_div_iff₀ ha).mpr
  have hb := hc _ (recover_mem A v)
  rw [image_recover] at hb
  nlinarith

 theorem recover_bound (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (v : V) :
    ‖recover A v‖ ≤ ‖v‖ / alpha := by
  exact (recover_projected_bound A alpha ha hc v).trans
    ((div_le_div_iff_of_pos_right ha).mpr (A.range.norm_starProjection_apply_le v))

 theorem recover_opNorm_bound (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) : ‖recover A‖ ≤ alpha⁻¹ := by
  apply (recover A).opNorm_le_bound (inv_nonneg.mpr ha.le)
  intro v
  simpa only [div_eq_mul_inv, mul_comm] using recover_bound A alpha ha hc v

 theorem recover_noise_bound (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (v w : V) :
    ‖recover A v - recover A w‖ ≤ ‖v-w‖ / alpha := by
  rw [← map_sub]
  exact recover_bound A alpha ha hc (v-w)

 theorem recover_noise_projected_bound (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (v w : V) :
    ‖recover A v - recover A w‖ ≤ ‖A.range.starProjection (v-w)‖ / alpha := by
  rw [← map_sub]
  exact recover_projected_bound A alpha ha hc (v-w)

 theorem identifiable_source_bound (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (v : V) (g : G) :
    ‖recover A v - A.kerᗮ.starProjection g‖ ≤ ‖v - A g‖ / alpha := by
  rw [← recover_image A g]
  exact recover_noise_bound A alpha ha hc v (A g)

 theorem noisy_source_bound_sq (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (g : G) (e : V) :
    ‖recover A (A g+e) - g‖ ^ 2 ≤
      (‖e‖ / alpha)^2 + ‖A.ker.starProjection g‖ ^ 2 := by
  rw [noisy_source_error_sq]
  have hb := recover_bound A alpha ha hc e
  exact add_le_add ((sq_le_sq₀ (norm_nonneg _) (div_nonneg (norm_nonneg _) ha.le)).mpr hb) le_rfl

 theorem noisy_identifiable_source_bound (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (g : G) (hg : g ∈ A.kerᗮ) (e : V) :
    ‖recover A (A g+e) - g‖ ≤ ‖e‖ / alpha := by
  rw [map_add, (exact_source_recovery_iff A g).mpr hg, add_sub_cancel_left]
  exact recover_bound A alpha ha hc e

/-- A candidate source has an exact split into identifiable error and kernel ambiguity. -/
 theorem candidate_source_error_sq (v : V) (g : G) :
    ‖g-recover A v‖^2 =
      ‖A.kerᗮ.starProjection g-recover A v‖^2 + ‖A.ker.starProjection g‖^2 := by
  have ho : inner ℝ (A.kerᗮ.starProjection g-recover A v) (A.ker.starProjection g) = 0 :=
    inner_eq_zero_symm.mp ((A.kerᗮ.sub_mem (A.kerᗮ.starProjection_apply_mem g)
      (recover_mem A v)) _ (A.ker.starProjection_apply_mem g))
  have hp := norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero _ _ ho
  have he : (A.kerᗮ.starProjection g-recover A v)+A.ker.starProjection g = g-recover A v := by
    rw [Submodule.starProjection_orthogonal_val]
    abel
  simpa only [he, pow_two] using hp

 theorem candidate_identifiable_bound (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (v : V) (g : G) :
    ‖A.kerᗮ.starProjection g-recover A v‖ ≤ ‖A g-A.range.starProjection v‖ / alpha := by
  apply (le_div_iff₀ ha).mpr
  have hb := hc _ (A.kerᗮ.sub_mem (A.kerᗮ.starProjection_apply_mem g) (recover_mem A v))
  rw [map_sub, source_projection_image, image_recover] at hb
  nlinarith

/-- A posteriori source certificate retains both fitting and kernel-selection errors. -/
 theorem candidate_source_bound_sq (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (v : V) (g : G) :
    ‖g-recover A v‖^2 ≤
      (‖A g-A.range.starProjection v‖ / alpha)^2 + ‖A.ker.starProjection g‖^2 := by
  rw [candidate_source_error_sq]
  have hb := candidate_identifiable_bound A alpha ha hc v g
  exact add_le_add ((sq_le_sq₀ (norm_nonneg _) (div_nonneg (norm_nonneg _) ha.le)).mpr hb) le_rfl

 theorem candidate_tolerance_bound_sq (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) (v : V) (g : G) (tau kappa : ℝ)
    (ht : ‖A g-A.range.starProjection v‖ ≤ tau)
    (hk : ‖A.ker.starProjection g‖ ≤ kappa) :
    ‖g-recover A v‖^2 ≤ (tau/alpha)^2 + kappa^2 := by
  apply (candidate_source_bound_sq A alpha ha hc v g).trans
  have htn : 0 ≤ tau := (norm_nonneg _).trans ht
  have hkn : 0 ≤ kappa := (norm_nonneg _).trans hk
  gcongr

end Komorebi.SufficientResolution.SourceConditioning
