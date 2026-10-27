import Komorebi.SufficientResolution.GeneralizedDiscrepancyConsistency

/-!
# Inexact candidate-dependent discrepancy

Computed sources may lie near an exact generalized-discrepancy source.  Solver error
is kept separate from data and operator error, while no prior source-norm cap is supplied.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.GeneralizedInexact

open Filter Topology
open GeneralizedDiscrepancy MinimumNormReconstruction

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]

/-- An inexact source lies within `kappa` of an exact generalized accepted source. -/
def NearAccepted (C : G →L[ℝ] V) (v : V) (eta delta tau kappa : ℝ) (x : G) : Prop :=
  ∃ y : G, Accepted C v eta delta tau y ∧ ‖x-y‖ ≤ kappa

 theorem exact_is_near (C : G →L[ℝ] V) (v : V) (eta delta tau : ℝ) (x : G)
    (hx : Accepted C v eta delta tau x) : NearAccepted C v eta delta tau 0 x := by
  exact ⟨x, hx, by simp⟩

 theorem near_allowance_nonneg (C : G →L[ℝ] V) (v : V) (eta delta tau kappa : ℝ)
    (x : G) (hx : NearAccepted C v eta delta tau kappa x) : 0 ≤ kappa := by
  obtain ⟨y, _, hxy⟩ := hx
  exact (norm_nonneg (x-y)).trans hxy

 theorem near_norm_control (A C : G →L[ℝ] V) (p x : G) (v : V)
    (eta delta tau kappa : ℝ) (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hx : NearAccepted C v eta delta tau kappa x) :
    ‖x‖ ≤ ‖p‖+kappa := by
  obtain ⟨y, hy, hxy⟩ := hx
  calc
    ‖x‖ ≤ ‖x-y‖+‖y‖ := norm_le_norm_sub_add x y
    _ ≤ kappa+‖p‖ := add_le_add hxy (accepted_norm_control A C p y v eta delta tau hd he hy)
    _ = ‖p‖+kappa := add_comm _ _

 theorem near_true_residual (A C : G →L[ℝ] V) (p x : G) (v : V)
    (eta delta tau kappa : ℝ) (ht : 0 ≤ tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hx : NearAccepted C v eta delta tau kappa x) :
    ‖A x-A p‖ ≤ ‖A‖*kappa+(tau+1)*candidateNoise eta delta p := by
  obtain ⟨y, hy, hxy⟩ := hx
  have hxyA : ‖A x-A y‖ ≤ ‖A‖*kappa := by
    rw [← map_sub]
    exact (A.le_opNorm (x-y)).trans
      (mul_le_mul_of_nonneg_left hxy (norm_nonneg A))
  exact (norm_sub_le_norm_sub_add_norm_sub (A x) (A y) (A p)).trans
    (add_le_add hxyA (accepted_true_residual A C p y v eta delta tau ht hd he hy))

 theorem near_consistent {ι : Type*} (f : Filter ι) (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (v : ι → V) (eta delta kappa : ι → ℝ)
    (x : ι → G) (p : G) (tau : ℝ) (hp : p ∈ A.kerᗮ) (ht : 0 ≤ tau)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hx : ∀ i, NearAccepted (C i) (v i) (eta i) (delta i) tau (kappa i) (x i))
    (heta0 : Tendsto eta f (𝓝 0)) (hdelta0 : Tendsto delta f (𝓝 0))
    (hkappa0 : Tendsto kappa f (𝓝 0)) : Tendsto x f (𝓝 p) := by
  let y : ι → G := fun i => Classical.choose (hx i)
  have hy : ∀ i, Accepted (C i) (v i) (eta i) (delta i) tau (y i) := by
    intro i
    exact (Classical.choose_spec (hx i)).1
  have hxy : ∀ i, ‖x i-y i‖ ≤ kappa i := by
    intro i
    exact (Classical.choose_spec (hx i)).2
  have hyconv : Tendsto y f (𝓝 p) :=
    accepted_consistent f A C v eta delta y p tau hp ht hd he hy heta0 hdelta0
  have hnorm : Tendsto (fun i => ‖x i-y i‖) f (𝓝 0) :=
    squeeze_zero (fun i => norm_nonneg _) hxy hkappa0
  have hdiff : Tendsto (fun i => x i-y i) f (𝓝 0) :=
    tendsto_zero_iff_norm_tendsto_zero.mpr hnorm
  have hadd := hdiff.add hyconv
  simpa only [sub_add_cancel, zero_add] using hadd

 theorem near_source_condition_rate (A C : G →L[ℝ] V) (w : V) (x : G) (v : V)
    (eta delta tau kappa : ℝ) (ht : 0 ≤ tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A (A.adjoint w)-v‖ ≤ eta)
    (hx : NearAccepted C v eta delta tau kappa x) :
    ‖x-A.adjoint w‖^2 ≤
      2*kappa^2+4*‖w‖*(tau+1)*candidateNoise eta delta (A.adjoint w) := by
  obtain ⟨y, hy, hxy⟩ := hx
  have hk : 0 ≤ kappa := (norm_nonneg (x-y)).trans hxy
  have hxy2 := (sq_le_sq₀ (norm_nonneg _) hk).mpr hxy
  have hn := accepted_norm_control A C (A.adjoint w) y v eta delta tau hd he hy
  have hb := DiscrepancyConvergence.source_distance_estimate A (A.adjoint w) y w hn
  simp only [sub_self, norm_zero, mul_zero, zero_add] at hb
  have hr := accepted_true_residual A C (A.adjoint w) y v eta delta tau ht hd he hy
  have hy2 : ‖y-A.adjoint w‖^2 ≤
      2*‖w‖*(tau+1)*candidateNoise eta delta (A.adjoint w) := by
    calc
      _ ≤ 2*‖w‖*‖A y-A (A.adjoint w)‖ := hb
      _ ≤ 2*‖w‖*((tau+1)*candidateNoise eta delta (A.adjoint w)) :=
        mul_le_mul_of_nonneg_left hr (by positivity)
      _ = _ := by ring
  have htxy := norm_sub_le_norm_sub_add_norm_sub x y (A.adjoint w)
  have hs := (sq_le_sq₀ (norm_nonneg _) (add_nonneg (norm_nonneg _) (norm_nonneg _))).mpr htxy
  nlinarith [sq_nonneg (‖x-y‖-‖y-A.adjoint w‖)]

end Komorebi.SufficientResolution.GeneralizedInexact
