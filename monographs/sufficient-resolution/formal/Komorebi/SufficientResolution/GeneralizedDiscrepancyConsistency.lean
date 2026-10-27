import Komorebi.SufficientResolution.GeneralizedDiscrepancySelection

/-!
# Consistency for source-bound-free generalized discrepancy

The selected candidate-dependent rule converges under vanishing data and operator error.
The algorithmic acceptance rule has no externally supplied source-norm cap; the fixed
true identifiable source appears only in the proof of feasibility and convergence.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.GeneralizedDiscrepancyConsistency

open Filter Topology MinimumNormReconstruction
open GeneralizedDiscrepancy GeneralizedDiscrepancySelection

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]

 theorem selected_consistent {ι : Type*} (f : Filter ι) (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (v : ι → V) (eta delta : ι → ℝ)
    (p : G) (tau : ℝ) (hp : p ∈ A.kerᗮ)
    (heta : ∀ i, 0 < eta i) (htau : 1 < tau)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i)
    (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hrel : ∀ i, delta i*‖p‖ < (tau-1)*eta i)
    (heta0 : Tendsto eta f (𝓝 0)) (hdelta0 : Tendsto delta f (𝓝 0)) :
    Tendsto (fun i => selectedSource A (C i) p (v i) (eta i) (delta i) tau
      (heta i) htau (hd i) (he i) (hrel i)) f (𝓝 p) := by
  apply accepted_consistent f A C v eta delta _ p tau hp (le_of_lt (lt_trans (by norm_num) htau))
    hd he _ heta0 hdelta0
  intro i
  exact selectedSource_accepted A (C i) p (v i) (eta i) (delta i) tau
    (heta i) htau (hd i) (he i) (hrel i)

 theorem selected_norm_control {ι : Type*} (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (v : ι → V) (eta delta : ι → ℝ)
    (p : G) (tau : ℝ) (heta : ∀ i, 0 < eta i) (htau : 1 < tau)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i)
    (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hrel : ∀ i, delta i*‖p‖ < (tau-1)*eta i) :
    ∀ i, ‖selectedSource A (C i) p (v i) (eta i) (delta i) tau
      (heta i) htau (hd i) (he i) (hrel i)‖ ≤ ‖p‖ := by
  intro i
  exact selectedSource_norm A (C i) p (v i) (eta i) (delta i) tau
    (heta i) htau (hd i) (he i) (hrel i)

 theorem selected_true_residual_tendsto_zero {ι : Type*} (f : Filter ι)
    (A : G →L[ℝ] V) (C : ι → G →L[ℝ] V) (v : ι → V)
    (eta delta : ι → ℝ) (p : G) (tau : ℝ)
    (heta : ∀ i, 0 < eta i) (htau : 1 < tau)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i)
    (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hrel : ∀ i, delta i*‖p‖ < (tau-1)*eta i)
    (heta0 : Tendsto eta f (𝓝 0)) (hdelta0 : Tendsto delta f (𝓝 0)) :
    Tendsto (fun i => ‖A (selectedSource A (C i) p (v i) (eta i) (delta i) tau
      (heta i) htau (hd i) (he i) (hrel i))-A p‖) f (𝓝 0) := by
  have ht : 0 ≤ tau := le_of_lt (lt_trans (by norm_num) htau)
  have hub : ∀ i, ‖A (selectedSource A (C i) p (v i) (eta i) (delta i) tau
      (heta i) htau (hd i) (he i) (hrel i))-A p‖ ≤
      (tau+1)*candidateNoise (eta i) (delta i) p := by
    intro i
    apply accepted_true_residual A (C i) p _ (v i) (eta i) (delta i) tau ht (hd i) (he i)
    exact selectedSource_accepted A (C i) p (v i) (eta i) (delta i) tau
      (heta i) htau (hd i) (he i) (hrel i)
  have hcand : Tendsto (fun i => candidateNoise (eta i) (delta i) p) f (𝓝 0) := by
    simpa only [candidateNoise, zero_mul, zero_add] using
      heta0.add (hdelta0.mul (tendsto_const_nhds (x := ‖p‖)))
  have hu : Tendsto (fun i => (tau+1)*candidateNoise (eta i) (delta i) p) f (𝓝 0) := by
    simpa only [mul_zero] using (tendsto_const_nhds (x := tau+1)).mul hcand
  exact squeeze_zero (fun i => norm_nonneg _) hub hu

 theorem selected_from_true_source_consistent {ι : Type*} (f : Filter ι)
    (A : G →L[ℝ] V) (C : ι → G →L[ℝ] V) (v : ι → V)
    (eta delta : ι → ℝ) (g : G) (tau : ℝ)
    (heta : ∀ i, 0 < eta i) (htau : 1 < tau)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i)
    (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hrel : ∀ i, delta i*‖A.kerᗮ.starProjection g‖ < (tau-1)*eta i)
    (heta0 : Tendsto eta f (𝓝 0)) (hdelta0 : Tendsto delta f (𝓝 0)) :
    Tendsto (fun i => selectedSource A (C i) (A.kerᗮ.starProjection g) (v i)
      (eta i) (delta i) tau (heta i) htau (hd i)
      (by simpa only [source_projection_image] using he i) (hrel i)) f
      (𝓝 (A.kerᗮ.starProjection g)) := by
  exact selected_consistent f A C v eta delta (A.kerᗮ.starProjection g) tau
    (A.kerᗮ.starProjection_apply_mem g) heta htau hd
    (fun i => by simpa only [source_projection_image] using he i) hrel heta0 hdelta0

 theorem selected_error_norm_limit {ι : Type*} (f : Filter ι)
    (A : G →L[ℝ] V) (C : ι → G →L[ℝ] V) (v : ι → V)
    (eta delta : ι → ℝ) (g : G) (tau : ℝ)
    (heta : ∀ i, 0 < eta i) (htau : 1 < tau)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i)
    (he : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hrel : ∀ i, delta i*‖A.kerᗮ.starProjection g‖ < (tau-1)*eta i)
    (heta0 : Tendsto eta f (𝓝 0)) (hdelta0 : Tendsto delta f (𝓝 0)) :
    Tendsto (fun i => ‖selectedSource A (C i) (A.kerᗮ.starProjection g) (v i)
      (eta i) (delta i) tau (heta i) htau (hd i)
      (by simpa only [source_projection_image] using he i) (hrel i)-g‖) f
      (𝓝 ‖A.ker.starProjection g‖) := by
  have h := (selected_from_true_source_consistent f A C v eta delta g tau heta htau hd he hrel
    heta0 hdelta0).sub (tendsto_const_nhds (x := g))
  have hn := h.norm
  have hid : A.kerᗮ.starProjection g-g = -(A.ker.starProjection g) := by
    rw [Submodule.starProjection_orthogonal_val]
    abel
  simpa only [hid, norm_neg] using hn

end Komorebi.SufficientResolution.GeneralizedDiscrepancyConsistency
