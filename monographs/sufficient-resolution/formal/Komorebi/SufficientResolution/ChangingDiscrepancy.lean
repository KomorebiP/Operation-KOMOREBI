import Komorebi.SufficientResolution.OperatorUncertainty
import Komorebi.SufficientResolution.InexactDiscrepancy

/-!
# Discrepancy estimates for a changing forward model

The norm bound applies to a fixed source p of the limiting operator, not to
unrelated minimum-norm sources of each model. No agreement of kernels or ranks
is assumed. This distinction enables consistency without projector convergence.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ChangingDiscrepancy

open OperatorUncertainty DiscrepancyRule DiscrepancyResidual InexactDiscrepancy
open TikhonovConstruction DiscrepancyConvergence MinimumNormReconstruction

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A C : G →L[ℝ] V)

 theorem accepted_fit (v : V) (epsilon tau : ℝ) (x : G)
    (hx : Accepted C v epsilon tau x) : ‖C x-v‖ ≤ tau*epsilon := by
  rcases hx with ⟨h, rfl⟩ | ⟨lam, hl, rfl, _, h⟩
  · simpa using h
  · simpa only [DiscrepancyResidual.residual, recoveryAt_pos C lam hl] using h

 theorem norm_control (p x : G) (v : V) (eta delta M tau : ℝ)
    (hd : ‖C-A‖ ≤ delta) (hM : ‖p‖ ≤ M) (he : ‖A p-v‖ ≤ eta)
    (hx : Accepted C v (effectiveNoise eta delta M) tau x) : ‖x‖ ≤ ‖p‖ := by
  exact (accepted_norm C v (effectiveNoise eta delta M) tau x p
    (effective_data_noise A C p v eta delta M hd hM he) hx).trans
    (C.kerᗮ.norm_starProjection_apply_le p)

 theorem true_residual (p x : G) (v : V) (eta delta M tau : ℝ)
    (hd : ‖C-A‖ ≤ delta) (hM : ‖p‖ ≤ M) (he : ‖A p-v‖ ≤ eta)
    (hx : Accepted C v (effectiveNoise eta delta M) tau x) :
    ‖A x-A p‖ ≤ (tau+1)*effectiveNoise eta delta M := by
  have hn := (norm_control A C p x v eta delta M tau hd hM he hx).trans hM
  have hdn := operator_allowance_nonneg A C delta hd
  calc
    _ ≤ delta*‖x‖+tau*effectiveNoise eta delta M+eta :=
      true_residual_bound A C x p v eta delta (tau*effectiveNoise eta delta M)
        hd he (accepted_fit C v (effectiveNoise eta delta M) tau x hx)
    _ ≤ delta*M+tau*effectiveNoise eta delta M+eta := by
      gcongr
    _ = _ := by simp only [effectiveNoise]; ring

 theorem near_norm_control (p x : G) (v : V) (eta delta M tau kappa : ℝ)
    (hd : ‖C-A‖ ≤ delta) (hM : ‖p‖ ≤ M) (he : ‖A p-v‖ ≤ eta)
    (hx : NearAccepted C v (effectiveNoise eta delta M) tau kappa x) :
    ‖x‖ ≤ ‖p‖+kappa := by
  obtain ⟨y, hy, hxy⟩ := hx
  calc
    _ ≤ ‖x-y‖+‖y‖ := norm_le_norm_sub_add _ _
    _ ≤ kappa+‖p‖ := add_le_add hxy (norm_control A C p y v eta delta M tau hd hM he hy)
    _ = _ := add_comm _ _

 theorem near_true_residual (p x : G) (v : V) (eta delta M tau kappa : ℝ)
    (hd : ‖C-A‖ ≤ delta) (hM : ‖p‖ ≤ M) (he : ‖A p-v‖ ≤ eta)
    (hx : NearAccepted C v (effectiveNoise eta delta M) tau kappa x) :
    ‖A x-A p‖ ≤ ‖A‖*kappa+(tau+1)*effectiveNoise eta delta M := by
  obtain ⟨y, hy, hxy⟩ := hx
  have hb : ‖A x-A y‖ ≤ ‖A‖*kappa := by
    rw [← map_sub]
    exact (A.le_opNorm (x-y)).trans (mul_le_mul_of_nonneg_left hxy (norm_nonneg _))
  exact (norm_sub_le_norm_sub_add_norm_sub (A x) (A y) (A p)).trans
    (add_le_add hb (true_residual A C p y v eta delta M tau hd hM he hy))

 theorem source_condition_rate (w : V) (x : G) (v : V) (eta delta M tau : ℝ)
    (hd : ‖C-A‖ ≤ delta) (hM : ‖A.adjoint w‖ ≤ M)
    (he : ‖A (A.adjoint w)-v‖ ≤ eta)
    (hx : Accepted C v (effectiveNoise eta delta M) tau x) :
    ‖x-A.adjoint w‖^2 ≤ 2*‖w‖*(tau+1)*effectiveNoise eta delta M := by
  have h := source_distance_estimate A (A.adjoint w) x w
    (norm_control A C (A.adjoint w) x v eta delta M tau hd hM he hx)
  simp only [sub_self, norm_zero, mul_zero, zero_add] at h
  calc
    _ ≤ 2*‖w‖*‖A x-A (A.adjoint w)‖ := h
    _ ≤ 2*‖w‖*((tau+1)*effectiveNoise eta delta M) :=
      mul_le_mul_of_nonneg_left
        (true_residual A C (A.adjoint w) x v eta delta M tau hd hM he hx) (by positivity)
    _ = _ := by ring

 theorem near_source_condition_rate (w : V) (x : G) (v : V) (eta delta M tau kappa : ℝ)
    (hd : ‖C-A‖ ≤ delta) (hM : ‖A.adjoint w‖ ≤ M)
    (he : ‖A (A.adjoint w)-v‖ ≤ eta)
    (hx : NearAccepted C v (effectiveNoise eta delta M) tau kappa x) :
    ‖x-A.adjoint w‖^2 ≤ 2*kappa^2+4*‖w‖*(tau+1)*effectiveNoise eta delta M := by
  obtain ⟨y, hy, hxy⟩ := hx
  have hk : 0 ≤ kappa := (norm_nonneg _).trans hxy
  have hxy2 := (sq_le_sq₀ (norm_nonneg _) hk).mpr hxy
  have hb := source_condition_rate A C w y v eta delta M tau hd hM he hy
  have ht := norm_sub_le_norm_sub_add_norm_sub x y (A.adjoint w)
  have hs := (sq_le_sq₀ (norm_nonneg _) (add_nonneg (norm_nonneg _) (norm_nonneg _))).mpr ht
  nlinarith [sq_nonneg (‖x-y‖-‖y-A.adjoint w‖)]

omit [CompleteSpace V] in
 theorem projection_effective_noise (g : G) (v : V) (eta delta M : ℝ)
    (hd : ‖C-A‖ ≤ delta) (hM : ‖A.kerᗮ.starProjection g‖ ≤ M)
    (he : ‖A g-v‖ ≤ eta) :
    ‖C (A.kerᗮ.starProjection g)-v‖ ≤ effectiveNoise eta delta M := by
  exact effective_data_noise A C _ v eta delta M hd hM
    (by simpa only [source_projection_image] using he)

end Komorebi.SufficientResolution.ChangingDiscrepancy
