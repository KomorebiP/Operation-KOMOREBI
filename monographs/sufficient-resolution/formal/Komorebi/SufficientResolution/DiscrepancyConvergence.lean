import Komorebi.SufficientResolution.DiscrepancySelection
import Komorebi.SufficientResolution.TikhonovDensity

/-!
# Discrepancy consistency without an assumed asymptotic parameter schedule

The proof uses norm domination, residual consistency and normal-range density.
It does not assume lambda tends to zero or noise/sqrt(lambda) tends to zero.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.DiscrepancyConvergence

open TikhonovConstruction TikhonovOptimality TikhonovBounds TikhonovDensity
open MinimumNormReconstruction DiscrepancyResidual
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

 theorem norm_domination_of_residual (lam : ℝ) (hl : 0 < lam) (v : V) (g : G)
    (hr : ‖A g-v‖ ≤ residual A v lam) :
    ‖regularized A lam hl v‖ ≤ ‖g‖ := by
  have hm := minimizes A lam hl v g
  unfold objective at hm
  have hs := (sq_le_sq₀ (norm_nonneg _) (residual_nonneg A v lam)).mpr hr
  rw [DiscrepancyResidual.residual, recoveryAt_pos A lam hl] at hs
  apply (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mp
  nlinarith

 theorem source_distance_estimate (g x : G) (w : V) (hn : ‖x‖ ≤ ‖g‖) :
    ‖x-g‖^2 ≤ 4*‖g‖*‖g-A.adjoint w‖+2*‖w‖*‖A x-A g‖ := by
  have hs := norm_sub_sq_real x g
  have hn2 := (sq_le_sq₀ (norm_nonneg _) (norm_nonneg _)).mpr hn
  have hi : ‖x-g‖^2 ≤ 2*inner ℝ g (g-x) := by
    rw [inner_sub_right, real_inner_self_eq_norm_sq]
    nlinarith [real_inner_comm x g]
  have hd : ‖g-x‖ ≤ 2*‖g‖ := (norm_sub_le g x).trans (by linarith)
  have he : inner ℝ g (g-x) =
      inner ℝ (g-A.adjoint w) (g-x)+inner ℝ w (A (g-x)) := by
    rw [inner_sub_left, ContinuousLinearMap.adjoint_inner_left]
    ring
  have h1 := real_inner_le_norm (g-A.adjoint w) (g-x)
  have h2 := real_inner_le_norm w (A (g-x))
  have hb := mul_le_mul_of_nonneg_left hd (norm_nonneg (g-A.adjoint w))
  rw [map_sub, norm_sub_rev] at h2
  rw [he, map_sub] at hi
  nlinarith

 theorem norm_control_residual_tendsto {ι : Type*} (f : Filter ι) (x : ι → G)
    (g : G) (hg : g ∈ A.kerᗮ) (hn : ∀ i, ‖x i‖ ≤ ‖g‖)
    (hr : Tendsto (fun i => ‖A (x i)-A g‖) f (𝓝 0)) :
    Tendsto x f (𝓝 g) := by
  apply Metric.tendsto_nhds.mpr
  intro eps heps
  obtain ⟨w, hw⟩ := approximate_identifiable A g hg
    (eps^2/(8*(‖g‖+1))) (by positivity)
  have hcut := (tendsto_order.mp hr).2
    (eps^2/(4*(‖A w‖+1))) (by positivity)
  have hwa : ‖g-gram A w‖*(8*(‖g‖+1)) < eps^2 :=
    (lt_div_iff₀ (by positivity)).mp hw
  filter_upwards [hcut] with i hi
  have hir : ‖A (x i)-A g‖*(4*(‖A w‖+1)) < eps^2 :=
    (lt_div_iff₀ (by positivity)).mp hi
  have hb := source_distance_estimate A g (x i) (A w) (hn i)
  change ‖x i-g‖^2 ≤ 4*‖g‖*‖g-gram A w‖+2*‖A w‖*‖A (x i)-A g‖ at hb
  rw [dist_eq_norm]
  have hs : ‖x i-g‖^2 < eps^2 := by
    nlinarith [norm_nonneg (g-gram A w), norm_nonneg (A (x i)-A g)]
  nlinarith [norm_nonneg (x i-g)]

 theorem discrepancy_source_norm (lam : ℝ) (hl : 0 < lam) (v : V)
    (g : G) (eta tau : ℝ) (heta : 0 ≤ eta) (htau : 1 ≤ tau)
    (hnoise : ‖A g-v‖ ≤ eta) (he : residual A v lam = tau*eta) :
    ‖regularized A lam hl v‖ ≤ ‖A.kerᗮ.starProjection g‖ := by
  apply norm_domination_of_residual A lam hl v (A.kerᗮ.starProjection g)
  rw [source_projection_image, he]
  exact hnoise.trans (by nlinarith)

 theorem discrepancy_true_residual (lam : ℝ) (hl : 0 < lam) (v : V)
    (g : G) (eta tau : ℝ) (hnoise : ‖A g-v‖ ≤ eta)
    (he : residual A v lam = tau*eta) :
    ‖A (regularized A lam hl v)-A g‖ ≤ (tau+1)*eta := by
  calc
    _ ≤ ‖A (regularized A lam hl v)-v‖+‖v-A g‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ tau*eta+eta := by
      apply add_le_add
      · exact le_of_eq (by simpa only [DiscrepancyResidual.residual, recoveryAt_pos A lam hl] using he)
      · simpa only [norm_sub_rev] using hnoise
    _ = _ := by ring

 theorem discrepancy_consistent {ι : Type*} (f : Filter ι)
    (lam eta : ι → ℝ) (v : ι → V) (g : G) (tau : ℝ)
    (hlam : ∀ i, 0 < lam i) (heta : ∀ i, 0 ≤ eta i) (htau : 1 ≤ tau)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (he : ∀ i, residual A (v i) (lam i) = tau*eta i)
    (heta0 : Tendsto eta f (𝓝 0)) :
    Tendsto (fun i => regularized A (lam i) (hlam i) (v i)) f
      (𝓝 (A.kerᗮ.starProjection g)) := by
  apply norm_control_residual_tendsto A f _ (A.kerᗮ.starProjection g)
    (A.kerᗮ.starProjection_apply_mem g)
  · intro i
    exact discrepancy_source_norm A (lam i) (hlam i) (v i) g (eta i) tau
      (heta i) htau (hnoise i) (he i)
  · apply squeeze_zero (fun i => norm_nonneg _)
      (fun i => ?_) (by simpa only [mul_zero] using (tendsto_const_nhds (x := tau+1)).mul heta0)
    rw [source_projection_image]
    exact discrepancy_true_residual A (lam i) (hlam i) (v i) g (eta i) tau (hnoise i) (he i)

 theorem discrepancy_source_rate (lam : ℝ) (hl : 0 < lam) (v : V)
    (w : V) (eta tau : ℝ) (heta : 0 ≤ eta) (htau : 1 ≤ tau)
    (hnoise : ‖A (A.adjoint w)-v‖ ≤ eta)
    (he : residual A v lam = tau*eta) :
    ‖regularized A lam hl v-A.adjoint w‖^2 ≤ 2*‖w‖*(tau+1)*eta := by
  have hn : ‖regularized A lam hl v‖ ≤ ‖A.adjoint w‖ := by
    apply norm_domination_of_residual A lam hl v (A.adjoint w)
    rw [he]; exact hnoise.trans (by nlinarith)
  have hb := source_distance_estimate A (A.adjoint w) (regularized A lam hl v) w hn
  simp only [sub_self, norm_zero, mul_zero, zero_add] at hb
  have hr := discrepancy_true_residual A lam hl v (A.adjoint w) eta tau hnoise he
  calc
    _ ≤ 2*‖w‖*‖A (regularized A lam hl v)-A (A.adjoint w)‖ := hb
    _ ≤ 2*‖w‖*((tau+1)*eta) := mul_le_mul_of_nonneg_left hr (by positivity)
    _ = _ := by ring

end Komorebi.SufficientResolution.DiscrepancyConvergence
