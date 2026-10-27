import Komorebi.SufficientResolution.DiscrepancyConvergence

/-!
# A total certified discrepancy rule with a small-data branch

A positive parameter root is used only when the data exceed the requested noise
threshold. Approximate discrepancy bands are also sufficient for consistency.
The choice of the exact real root is noncomputable; no numerical parser is verified here.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.DiscrepancyRule

open TikhonovConstruction TikhonovBounds MinimumNormReconstruction
open DiscrepancyResidual DiscrepancySelection DiscrepancyConvergence
open Filter Topology

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

/-- Certified output: either small data give zero, or an actual Tikhonov solution
has discrepancy between the noise allowance and the upper discrepancy threshold. -/
def Accepted (v : V) (eta tau : ℝ) (x : G) : Prop :=
  (‖v‖ ≤ tau*eta ∧ x = 0) ∨
  ∃ (lam : ℝ) (hl : 0 < lam), x = regularized A lam hl v ∧
    eta ≤ residual A v lam ∧ residual A v lam ≤ tau*eta

 theorem accepted_norm (v : V) (eta tau : ℝ) (x g : G)
    (hnoise : ‖A g-v‖ ≤ eta) (hx : Accepted A v eta tau x) :
    ‖x‖ ≤ ‖A.kerᗮ.starProjection g‖ := by
  rcases hx with ⟨_, rfl⟩ | ⟨lam, hl, rfl, hlo, _⟩
  · simp only [norm_zero]; exact norm_nonneg _
  · apply norm_domination_of_residual A lam hl v (A.kerᗮ.starProjection g)
    rw [source_projection_image]
    exact hnoise.trans hlo

 theorem accepted_true_residual (v : V) (eta tau : ℝ) (x g : G)
    (hnoise : ‖A g-v‖ ≤ eta) (hx : Accepted A v eta tau x) :
    ‖A x-A g‖ ≤ (tau+1)*eta := by
  have hfit : ‖A x-v‖ ≤ tau*eta := by
    rcases hx with ⟨hs, rfl⟩ | ⟨lam, hl, rfl, _, hhi⟩
    · simpa using hs
    · simpa only [DiscrepancyResidual.residual, recoveryAt_pos A lam hl] using hhi
  calc
    _ ≤ ‖A x-v‖+‖v-A g‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ tau*eta+eta := add_le_add hfit (by simpa only [norm_sub_rev] using hnoise)
    _ = _ := by ring

 theorem accepted_identifiable (v : V) (eta tau : ℝ) (x : G)
    (hx : Accepted A v eta tau x) : x ∈ A.kerᗮ := by
  rcases hx with ⟨_, rfl⟩ | ⟨lam, hl, rfl, _, _⟩
  · exact Submodule.zero_mem _
  · exact source_kernel_orthogonal A lam hl v

 theorem accepted_consistent {ι : Type*} (f : Filter ι) (eta : ι → ℝ)
    (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hx : ∀ i, Accepted A (v i) (eta i) tau (x i))
    (heta0 : Tendsto eta f (𝓝 0)) :
    Tendsto x f (𝓝 (A.kerᗮ.starProjection g)) := by
  apply norm_control_residual_tendsto A f x (A.kerᗮ.starProjection g)
    (A.kerᗮ.starProjection_apply_mem g)
  · intro i; exact accepted_norm A (v i) (eta i) tau (x i) g (hnoise i) (hx i)
  · apply squeeze_zero (fun i => norm_nonneg _) (fun i => ?_)
      (by simpa only [mul_zero] using (tendsto_const_nhds (x := tau+1)).mul heta0)
    rw [source_projection_image]
    exact accepted_true_residual A (v i) (eta i) tau (x i) g (hnoise i) (hx i)

 theorem accepted_source_rate (v w : V) (eta tau : ℝ) (x : G)
    (hnoise : ‖A (A.adjoint w)-v‖ ≤ eta) (hx : Accepted A v eta tau x) :
    ‖x-A.adjoint w‖^2 ≤ 2*‖w‖*(tau+1)*eta := by
  have hn := (accepted_norm A v eta tau x (A.adjoint w) hnoise hx).trans
    (A.kerᗮ.norm_starProjection_apply_le _)
  have hb := source_distance_estimate A (A.adjoint w) x w hn
  simp only [sub_self, norm_zero, mul_zero, zero_add] at hb
  calc
    _ ≤ 2*‖w‖*‖A x-A (A.adjoint w)‖ := hb
    _ ≤ 2*‖w‖*((tau+1)*eta) := mul_le_mul_of_nonneg_left
      (accepted_true_residual A v eta tau x (A.adjoint w) hnoise hx) (by positivity)
    _ = _ := by ring

omit [CompleteSpace G] [CompleteSpace V] in
 theorem feasible_strict (v : V) (eta tau : ℝ) (he : 0 < eta) (ht : 1 < tau)
    (hf : ∃ g : G, ‖A g-v‖ ≤ eta) : ∃ g : G, ‖A g-v‖ < tau*eta := by
  obtain ⟨g, hg⟩ := hf
  exact ⟨g, hg.trans_lt (by nlinarith)⟩

/-- A total rule on data with a certified positive noise allowance. -/
def selectedSource (v : V) (eta tau : ℝ) (he : 0 < eta) (ht : 1 < tau)
    (hf : ∃ g : G, ‖A g-v‖ ≤ eta) : G :=
  if hs : ‖v‖ ≤ tau*eta then 0 else
    regularized A (parameter A v (tau*eta) (feasible_strict A v eta tau he ht hf)
      (lt_of_not_ge hs))
      (parameter_pos A v (tau*eta) (feasible_strict A v eta tau he ht hf)
        (lt_of_not_ge hs)) v

 theorem selectedSource_accepted (v : V) (eta tau : ℝ) (he : 0 < eta) (ht : 1 < tau)
    (hf : ∃ g : G, ‖A g-v‖ ≤ eta) :
    Accepted A v eta tau (selectedSource A v eta tau he ht hf) := by
  unfold selectedSource
  split_ifs with hs
  · exact Or.inl ⟨hs, rfl⟩
  · apply Or.inr
    refine ⟨_, parameter_pos A v (tau*eta) _ (lt_of_not_ge hs), rfl, ?_, ?_⟩
    · rw [parameter_hits_target]; nlinarith
    · exact (parameter_hits_target A v (tau*eta) _ _).le

 theorem selectedSource_small (v : V) (eta tau : ℝ) (he : 0 < eta) (ht : 1 < tau)
    (hf : ∃ g : G, ‖A g-v‖ ≤ eta) (hs : ‖v‖ ≤ tau*eta) :
    selectedSource A v eta tau he ht hf = 0 := by simp [selectedSource, hs]

 theorem selectedSource_consistent {ι : Type*} (f : Filter ι) (eta : ι → ℝ)
    (v : ι → V) (g : G) (tau : ℝ) (he : ∀ i, 0 < eta i) (ht : 1 < tau)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i) (heta0 : Tendsto eta f (𝓝 0)) :
    Tendsto (fun i => selectedSource A (v i) (eta i) tau (he i) ht ⟨g, hnoise i⟩)
      f (𝓝 (A.kerᗮ.starProjection g)) := by
  exact accepted_consistent A f eta v _ g tau hnoise
    (fun i => selectedSource_accepted A (v i) (eta i) tau (he i) ht ⟨g, hnoise i⟩) heta0

 theorem accepted_error_norm_limit {ι : Type*} (f : Filter ι) (eta : ι → ℝ)
    (v : ι → V) (x : ι → G) (g : G) (tau : ℝ)
    (hnoise : ∀ i, ‖A g-v i‖ ≤ eta i)
    (hx : ∀ i, Accepted A (v i) (eta i) tau (x i))
    (heta0 : Tendsto eta f (𝓝 0)) :
    Tendsto (fun i => ‖x i-g‖) f (𝓝 ‖A.ker.starProjection g‖) := by
  have h := ((accepted_consistent A f eta v x g tau hnoise hx heta0).sub
    (tendsto_const_nhds (x := g))).norm
  have he : A.kerᗮ.starProjection g-g = -(A.ker.starProjection g) := by
    rw [Submodule.starProjection_orthogonal_val]; abel
  simpa only [he, norm_neg] using h

end Komorebi.SufficientResolution.DiscrepancyRule
