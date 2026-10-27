import Komorebi.SufficientResolution.GeneralizedInexact

/-!
# Checkable relative-error sufficient conditions

A source-norm cap is not part of the generalized acceptance rule.  For theorem-level
feasibility, model error can instead be compared to the data-noise scale.  These
lemmas isolate a simple sufficient ratio condition and keep it separate from acceptance.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.GeneralizedFeasibility

open Filter Topology
open GeneralizedDiscrepancy GeneralizedDiscrepancySelection
open GeneralizedDiscrepancyConsistency

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]

omit [InnerProductSpace ℝ G] [CompleteSpace G] in
 theorem relative_accuracy_of_scaled_error (p : G) (eta delta gamma tau : ℝ)
    (heta : 0 < eta) (hscale : delta ≤ gamma*eta)
    (hmargin : gamma*‖p‖ < tau-1) :
    delta*‖p‖ < (tau-1)*eta := by
  have h1 : delta*‖p‖ ≤ (gamma*eta)*‖p‖ :=
    mul_le_mul_of_nonneg_right hscale (norm_nonneg p)
  have h2 : gamma*‖p‖*eta < (tau-1)*eta :=
    mul_lt_mul_of_pos_right hmargin heta
  nlinarith

 theorem exists_accepted_of_scaled_error (A C : G →L[ℝ] V) (p : G) (v : V)
    (eta delta gamma tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hd : ‖C-A‖ ≤ delta) (he : ‖A p-v‖ ≤ eta)
    (hscale : delta ≤ gamma*eta) (hmargin : gamma*‖p‖ < tau-1) :
    ∃ x : G, Accepted C v eta delta tau x ∧ ‖x‖ ≤ ‖p‖ := by
  apply exists_accepted A C p v eta delta tau heta htau hd he
  exact relative_accuracy_of_scaled_error p eta delta gamma tau heta hscale hmargin

 theorem selected_consistent_of_scaled_error {ι : Type*} (f : Filter ι)
    (A : G →L[ℝ] V) (C : ι → G →L[ℝ] V) (v : ι → V)
    (eta delta gamma : ι → ℝ) (p : G) (tau : ℝ) (hp : p ∈ A.kerᗮ)
    (heta : ∀ i, 0 < eta i) (htau : 1 < tau)
    (hd : ∀ i, ‖C i-A‖ ≤ delta i) (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hscale : ∀ i, delta i ≤ gamma i*eta i)
    (hmargin : ∀ i, gamma i*‖p‖ < tau-1)
    (heta0 : Tendsto eta f (𝓝 0)) (hdelta0 : Tendsto delta f (𝓝 0)) :
    Tendsto (fun i => selectedSource A (C i) p (v i) (eta i) (delta i) tau
      (heta i) htau (hd i) (he i)
      (relative_accuracy_of_scaled_error p (eta i) (delta i) (gamma i) tau
        (heta i) (hscale i) (hmargin i))) f (𝓝 p) := by
  exact selected_consistent f A C v eta delta p tau hp heta htau hd he
    (fun i => relative_accuracy_of_scaled_error p (eta i) (delta i) (gamma i) tau
      (heta i) (hscale i) (hmargin i)) heta0 hdelta0

omit [InnerProductSpace ℝ G] [CompleteSpace G] in
 theorem fixed_ratio_margin (p : G) (gamma tau : ℝ)
    (hmargin : gamma*‖p‖ < tau-1) :
    ∀ eta delta : ℝ, 0 < eta → delta ≤ gamma*eta →
      delta*‖p‖ < (tau-1)*eta := by
  intro eta delta heta hscale
  exact relative_accuracy_of_scaled_error p eta delta gamma tau heta hscale hmargin

omit [InnerProductSpace ℝ G] [CompleteSpace G] in
 theorem zero_source_relative_accuracy (eta delta tau : ℝ)
    (heta : 0 < eta) (htau : 1 < tau) :
    delta*‖(0:G)‖ < (tau-1)*eta := by
  simp only [norm_zero, mul_zero]
  exact mul_pos (sub_pos.mpr htau) heta

end Komorebi.SufficientResolution.GeneralizedFeasibility
