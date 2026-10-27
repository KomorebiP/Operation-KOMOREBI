import Komorebi.SufficientResolution.CalibrationRecovery
import Komorebi.SufficientResolution.GeneralizedDiscrepancySelection
import Komorebi.SufficientResolution.GeneralizedFeasibility

/-!
# Feasibility and selection from calibration-generated uncertainty
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.CalibrationSelection

open Filter Topology
open CalibrationFrame CalibrationRecovery GeneralizedDiscrepancy
open GeneralizedDiscrepancySelection GeneralizedFeasibility
open MinimumNormReconstruction

variable {K G V : Type*}
variable [NormedAddCommGroup K] [NormedSpace ℝ K]
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]

omit [CompleteSpace G] [CompleteSpace V] in
 theorem calibration_relative_accuracy (F : CalibrationFrame.Frame K G)
    (A C : G →L[ℝ] V) (Y : K →L[ℝ] V) (p : G)
    (eta etaCal fit tau : ℝ)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit)
    (hrel : generatedDelta F etaCal fit * ‖p‖ < (tau-1)*eta) :
    ‖C-A‖*‖p‖ < (tau-1)*eta := by
  have hd := generated_operator_bound F A C Y etaCal fit hA hC
  have hn : 0 ≤ ‖p‖ := norm_nonneg p
  exact lt_of_le_of_lt (mul_le_mul_of_nonneg_right hd hn) hrel

 theorem exists_accepted_from_calibration (F : CalibrationFrame.Frame K G)
    (A C : G →L[ℝ] V) (Y : K →L[ℝ] V) (p : G) (v : V)
    (eta etaCal fit tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit)
    (he : ‖A p-v‖ ≤ eta)
    (hrel : generatedDelta F etaCal fit * ‖p‖ < (tau-1)*eta) :
    ∃ x : G, Accepted C v eta (generatedDelta F etaCal fit) tau x ∧ ‖x‖ ≤ ‖p‖ := by
  exact exists_accepted A C p v eta (generatedDelta F etaCal fit) tau heta htau
    (generated_operator_bound F A C Y etaCal fit hA hC) he hrel

/-- Noncomputable source selected using only the calibration-generated allowance. -/
def selectedSource (F : CalibrationFrame.Frame K G)
    (A C : G →L[ℝ] V) (Y : K →L[ℝ] V) (p : G) (v : V)
    (eta etaCal fit tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit)
    (he : ‖A p-v‖ ≤ eta)
    (hrel : generatedDelta F etaCal fit * ‖p‖ < (tau-1)*eta) : G :=
  GeneralizedDiscrepancySelection.selectedSource A C p v eta
    (generatedDelta F etaCal fit) tau heta htau
    (generated_operator_bound F A C Y etaCal fit hA hC) he hrel

 theorem selectedSource_accepted (F : CalibrationFrame.Frame K G)
    (A C : G →L[ℝ] V) (Y : K →L[ℝ] V) (p : G) (v : V)
    (eta etaCal fit tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit)
    (he : ‖A p-v‖ ≤ eta)
    (hrel : generatedDelta F etaCal fit * ‖p‖ < (tau-1)*eta) :
    Accepted C v eta (generatedDelta F etaCal fit) tau
      (selectedSource F A C Y p v eta etaCal fit tau heta htau hA hC he hrel) := by
  exact GeneralizedDiscrepancySelection.selectedSource_accepted A C p v eta
    (generatedDelta F etaCal fit) tau heta htau
    (generated_operator_bound F A C Y etaCal fit hA hC) he hrel

 theorem selectedSource_norm (F : CalibrationFrame.Frame K G)
    (A C : G →L[ℝ] V) (Y : K →L[ℝ] V) (p : G) (v : V)
    (eta etaCal fit tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit)
    (he : ‖A p-v‖ ≤ eta)
    (hrel : generatedDelta F etaCal fit * ‖p‖ < (tau-1)*eta) :
    ‖selectedSource F A C Y p v eta etaCal fit tau heta htau hA hC he hrel‖ ≤ ‖p‖ := by
  exact GeneralizedDiscrepancySelection.selectedSource_norm A C p v eta
    (generatedDelta F etaCal fit) tau heta htau
    (generated_operator_bound F A C Y etaCal fit hA hC) he hrel

 theorem exists_accepted_of_calibration_ratio (F : CalibrationFrame.Frame K G)
    (A C : G →L[ℝ] V) (Y : K →L[ℝ] V) (p : G) (v : V)
    (eta etaCal fit gamma tau : ℝ) (heta : 0 < eta) (htau : 1 < tau)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit)
    (he : ‖A p-v‖ ≤ eta)
    (hscale : generatedDelta F etaCal fit ≤ gamma*eta)
    (hmargin : gamma*‖p‖ < tau-1) :
    ∃ x : G, Accepted C v eta (generatedDelta F etaCal fit) tau x ∧ ‖x‖ ≤ ‖p‖ := by
  apply exists_accepted_of_scaled_error A C p v eta (generatedDelta F etaCal fit) gamma tau
    heta htau (generated_operator_bound F A C Y etaCal fit hA hC) he hscale hmargin

 theorem calibrated_selected_consistent {ι : Type*} (f : Filter ι)
    (F : CalibrationFrame.Frame K G) (A : G →L[ℝ] V)
    (C : ι → G →L[ℝ] V) (Y : ι → K →L[ℝ] V)
    (v : ι → V) (eta etaCal fit : ι → ℝ) (p : G) (tau : ℝ)
    (hp : p ∈ A.kerᗮ) (heta : ∀ i, 0 < eta i) (htau : 1 < tau)
    (hA : ∀ i, ‖Y i-A.comp F.synthesis‖ ≤ etaCal i)
    (hC : ∀ i, ‖Y i-(C i).comp F.synthesis‖ ≤ fit i)
    (he : ∀ i, ‖A p-v i‖ ≤ eta i)
    (hrel : ∀ i, generatedDelta F (etaCal i) (fit i)*‖p‖ < (tau-1)*eta i)
    (heta0 : Tendsto eta f (𝓝 0))
    (hcal0 : Tendsto etaCal f (𝓝 0)) (hfit0 : Tendsto fit f (𝓝 0)) :
    Tendsto (fun i => selectedSource F A (C i) (Y i) p (v i)
      (eta i) (etaCal i) (fit i) tau (heta i) htau (hA i) (hC i) (he i) (hrel i))
      f (𝓝 p) := by
  exact GeneralizedDiscrepancyConsistency.selected_consistent f A C v eta
    (fun j => generatedDelta F (etaCal j) (fit j)) p tau hp heta htau
    (fun j => generated_operator_bound F A (C j) (Y j) (etaCal j) (fit j) (hA j) (hC j))
    he hrel heta0 (generatedDelta_tendsto_zero f F etaCal fit hcal0 hfit0)

end Komorebi.SufficientResolution.CalibrationSelection
