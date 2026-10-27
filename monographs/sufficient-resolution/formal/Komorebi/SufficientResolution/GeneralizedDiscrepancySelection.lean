import Komorebi.SufficientResolution.GeneralizedDiscrepancy

/-!
# Feasibility-aware candidate-dependent discrepancy selection

A generalized acceptance rule can remove a supplied source-norm cap, but an acceptable
positive parameter need not exist for a poor model. This module proves existence under
an explicit relative model-accuracy condition and retains a small-data branch.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.GeneralizedDiscrepancySelection

open TikhonovConstruction DiscrepancyResidual DiscrepancySelection DiscrepancyConvergence
open OperatorUncertainty GeneralizedDiscrepancy

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]

omit [CompleteSpace G] [CompleteSpace V] in
 theorem relative_accuracy_gives_strict_fit (A C : G →L[ℝ] V) (p : G) (v : V)
    (eta delta tau : ℝ) (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hrel : delta*‖p‖ < (tau-1)*eta) :
    ‖C p-v‖ < tau*eta := by
  have hb := effective_data_noise A C p v eta delta ‖p‖ hd le_rfl he
  simp only [effectiveNoise] at hb
  nlinarith

omit [CompleteSpace G] [CompleteSpace V] in
 theorem relative_accuracy_requires_positive_margin (A C : G →L[ℝ] V) (p : G)
    (eta delta tau : ℝ) (hd : ‖C-A‖ ≤ delta) (he : 0 ≤ eta)
    (hrel : delta*‖p‖ < (tau-1)*eta) : 0 < eta ∨ ‖p‖ = 0 := by
  have hdelta : 0 ≤ delta := operator_allowance_nonneg A C delta hd
  by_cases hp : ‖p‖ = 0
  · exact Or.inr hp
  · left
    have hpn : 0 < ‖p‖ := lt_of_le_of_ne (norm_nonneg p) (Ne.symm hp)
    by_contra hz
    have he0 : eta = 0 := le_antisymm (le_of_not_gt hz) he
    rw [he0] at hrel
    simp only [mul_zero] at hrel
    have : 0 ≤ delta*‖p‖ := mul_nonneg hdelta (norm_nonneg p)
    linarith

 theorem positive_parameter_source (A C : G →L[ℝ] V) (p : G) (v : V)
    (eta delta tau : ℝ) (_heta : 0 < eta) (htau : 1 < tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hrel : delta*‖p‖ < (tau-1)*eta) (hlarge : tau*eta < ‖v‖) :
    ∃ (lam : ℝ) (hl : 0 < lam),
      let x := regularized C lam hl v
      residual C v lam = tau*eta ∧
      Accepted C v eta delta tau x ∧ ‖x‖ ≤ ‖p‖ := by
  have hfit : ‖C p-v‖ < tau*eta :=
    relative_accuracy_gives_strict_fit A C p v eta delta tau hd he hrel
  obtain ⟨lam, hl, hres⟩ := exists_parameter C v (tau*eta) ⟨p, hfit⟩ hlarge
  refine ⟨lam, hl, ?_⟩
  dsimp
  have hn : ‖regularized C lam hl v‖ ≤ ‖p‖ := by
    apply norm_domination_of_residual C lam hl v p
    rw [hres]
    exact hfit.le
  have hdelta : 0 ≤ delta := operator_allowance_nonneg A C delta hd
  have hcand : candidateNoise eta delta (regularized C lam hl v) < tau*eta := by
    calc
      candidateNoise eta delta (regularized C lam hl v)
          ≤ candidateNoise eta delta p := candidateNoise_mono_norm eta delta hdelta hn
      _ < eta + (tau-1)*eta := by
        simp only [candidateNoise]
        simpa only [add_comm] using add_lt_add_left hrel eta
      _ = tau*eta := by ring
  have hu : tau*eta ≤ tau*candidateNoise eta delta (regularized C lam hl v) := by
    have hcn : eta ≤ candidateNoise eta delta (regularized C lam hl v) := by
      simp only [candidateNoise]
      exact le_add_of_nonneg_right (mul_nonneg hdelta (norm_nonneg _))
    exact mul_le_mul_of_nonneg_left hcn (le_of_lt (lt_trans (by norm_num) htau))
  refine ⟨hres, Or.inr ⟨lam, hl, rfl, ?_, ?_⟩, hn⟩
  · rw [hres]; exact hcand.le
  · rw [hres]; exact hu

 theorem exists_accepted (A C : G →L[ℝ] V) (p : G) (v : V)
    (eta delta tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hrel : delta*‖p‖ < (tau-1)*eta) :
    ∃ x : G, Accepted C v eta delta tau x ∧ ‖x‖ ≤ ‖p‖ := by
  by_cases hs : ‖v‖ ≤ tau*eta
  · refine ⟨0, Or.inl ⟨hs, rfl⟩, ?_⟩
    simpa only [norm_zero] using norm_nonneg p
  · have hlarge : tau*eta < ‖v‖ := lt_of_not_ge hs
    obtain ⟨lam, hl, _, hx, hn⟩ :=
      positive_parameter_source A C p v eta delta tau heta htau hd he hrel hlarge
    exact ⟨regularized C lam hl v, hx, hn⟩

/-- Noncomputable source selected from the proved feasible generalized rule.  The scalar
source-norm cap from block 14 is not an argument. -/
def selectedSource (A C : G →L[ℝ] V) (p : G) (v : V)
    (eta delta tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hrel : delta*‖p‖ < (tau-1)*eta) : G :=
  Classical.choose (exists_accepted A C p v eta delta tau heta htau hd he hrel)

 theorem selectedSource_accepted (A C : G →L[ℝ] V) (p : G) (v : V)
    (eta delta tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hrel : delta*‖p‖ < (tau-1)*eta) :
    Accepted C v eta delta tau
      (selectedSource A C p v eta delta tau heta htau hd he hrel) :=
  (Classical.choose_spec (exists_accepted A C p v eta delta tau heta htau hd he hrel)).1

 theorem selectedSource_norm (A C : G →L[ℝ] V) (p : G) (v : V)
    (eta delta tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hrel : delta*‖p‖ < (tau-1)*eta) :
    ‖selectedSource A C p v eta delta tau heta htau hd he hrel‖ ≤ ‖p‖ :=
  (Classical.choose_spec (exists_accepted A C p v eta delta tau heta htau hd he hrel)).2

end Komorebi.SufficientResolution.GeneralizedDiscrepancySelection
