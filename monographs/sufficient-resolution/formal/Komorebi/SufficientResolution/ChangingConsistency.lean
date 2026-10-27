import Komorebi.SufficientResolution.ChangingDiscrepancy

/-!
# Strong consistency with uncertain operators and changing kernels

Only the limiting operator A defines the final identifiable source. Estimated
operators C_i may change rank and kernel. Positive source correction budgets
need to vanish, as do genuine data and operator uncertainty allowances.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ChangingConsistency

open OperatorUncertainty ChangingDiscrepancy DiscrepancyRule InexactDiscrepancy
open DiscrepancyConvergence MinimumNormReconstruction
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

 theorem accepted_consistent {ι : Type*} (f : Filter ι) (C : ι → G →L[ℝ] V)
    (eta delta : ι → ℝ) (v : ι → V) (x : ι → G) (p : G) (M tau : ℝ)
    (hp : p ∈ A.kerᗮ) (hM : ‖p‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hx : ∀ i, Accepted (C i) (v i) (effectiveNoise (eta i) (delta i) M) tau (x i))
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0)) :
    Tendsto x f (𝓝 p) := by
  apply norm_control_residual_tendsto A f x p hp
  · intro i; exact norm_control A (C i) p (x i) (v i) (eta i) (delta i) M tau
      (hd i) hM (he i) (hx i)
  · apply squeeze_zero (fun i => norm_nonneg _)
      (fun i => true_residual A (C i) p (x i) (v i) (eta i) (delta i) M tau
        (hd i) hM (he i) (hx i))
    simpa only [mul_zero] using (tendsto_const_nhds (x := tau+1)).mul
      (effective_tendsto f eta delta M heta hdelta)

 theorem near_consistent {ι : Type*} (f : Filter ι) (C : ι → G →L[ℝ] V)
    (eta delta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (p : G) (M tau : ℝ)
    (hp : p ∈ A.kerᗮ) (hM : ‖p‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hx : ∀ i, NearAccepted (C i) (v i) (effectiveNoise (eta i) (delta i) M)
      tau (kappa i) (x i))
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0))
    (hkappa : Tendsto kappa f (𝓝 0)) : Tendsto x f (𝓝 p) := by
  choose y hy hdxy using hx
  have hc : Tendsto (fun i => x i-y i) f (𝓝 0) := squeeze_zero_norm hdxy hkappa
  have hec := accepted_consistent A f C eta delta v y p M tau hp hM hd he hy heta hdelta
  simpa only [sub_add_cancel, zero_add] using hc.add hec

 theorem projected_consistent {ι : Type*} (f : Filter ι) (C : ι → G →L[ℝ] V)
    (eta delta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (g : G) (M tau : ℝ)
    (hM : ‖A.kerᗮ.starProjection g‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hx : ∀ i, NearAccepted (C i) (v i) (effectiveNoise (eta i) (delta i) M)
      tau (kappa i) (x i))
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0))
    (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) := by
  exact near_consistent A f C eta delta kappa v x (A.kerᗮ.starProjection g) M tau
    (A.kerᗮ.starProjection_apply_mem g) hM hd
    (fun i => by simpa only [source_projection_image] using he i) hx heta hdelta hkappa

 theorem source_error_limit {ι : Type*} (f : Filter ι) (C : ι → G →L[ℝ] V)
    (eta delta kappa : ι → ℝ) (v : ι → V) (x : ι → G) (g : G) (M tau : ℝ)
    (hM : ‖A.kerᗮ.starProjection g‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hx : ∀ i, NearAccepted (C i) (v i) (effectiveNoise (eta i) (delta i) M)
      tau (kappa i) (x i))
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0))
    (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto (fun i => ‖x i-g‖) f (𝓝 ‖A.ker.starProjection g‖) := by
  have h := ((projected_consistent A f C eta delta kappa v x g M tau
    hM hd he hx heta hdelta hkappa).sub (tendsto_const_nhds (x := g))).norm
  have heq : A.kerᗮ.starProjection g-g = -(A.ker.starProjection g) := by
    rw [Submodule.starProjection_orthogonal_val]; abel
  simpa only [heq, norm_neg] using h

 theorem true_kernel_leakage_tendsto_zero {ι : Type*} (f : Filter ι)
    (C : ι → G →L[ℝ] V) (eta delta kappa : ι → ℝ) (v : ι → V) (x : ι → G)
    (g : G) (M tau : ℝ) (hM : ‖A.kerᗮ.starProjection g‖ ≤ M)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hx : ∀ i, NearAccepted (C i) (v i) (effectiveNoise (eta i) (delta i) M)
      tau (kappa i) (x i))
    (heta : Tendsto eta f (𝓝 0)) (hdelta : Tendsto delta f (𝓝 0))
    (hkappa : Tendsto kappa f (𝓝 0)) :
    Tendsto (fun i => A.ker.starProjection (x i)) f (𝓝 0) := by
  have h := A.ker.starProjection.continuous.tendsto (A.kerᗮ.starProjection g) |>.comp
    (projected_consistent A f C eta delta kappa v x g M tau hM hd he hx heta hdelta hkappa)
  have hz : A.ker.starProjection (A.kerᗮ.starProjection g) = 0 :=
    (Submodule.starProjection_apply_eq_zero_iff A.ker).mpr
      (A.kerᗮ.starProjection_apply_mem g)
  simpa only [hz, Function.comp_def] using h

end Komorebi.SufficientResolution.ChangingConsistency
