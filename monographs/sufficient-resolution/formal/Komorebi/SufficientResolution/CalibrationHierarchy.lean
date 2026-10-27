import Komorebi.SufficientResolution.CalibrationFrame

/-!
# Hierarchical split calibration

Split calibration frames compose.  The reconstruction norm of a hierarchical frame is
controlled by the product of the stage reconstruction norms.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.CalibrationHierarchy

open CalibrationFrame

variable {J K G V : Type*}
variable [NormedAddCommGroup J] [NormedSpace ℝ J]
variable [NormedAddCommGroup K] [NormedSpace ℝ K]
variable [NormedAddCommGroup G] [NormedSpace ℝ G]
variable [NormedAddCommGroup V] [NormedSpace ℝ V]

/-- Composition of two split calibration frames. -/
def comp (F : CalibrationFrame.Frame K G) (E : CalibrationFrame.Frame J K) :
    CalibrationFrame.Frame J G where
  synthesis := F.synthesis.comp E.synthesis
  analysis := E.analysis.comp F.analysis
  reconstruct := by
    apply ContinuousLinearMap.ext
    intro x
    simp only [ContinuousLinearMap.comp_apply, E.reconstruct_apply, F.reconstruct_apply,
      ContinuousLinearMap.id_apply]

@[simp] theorem comp_synthesis (F : CalibrationFrame.Frame K G)
    (E : CalibrationFrame.Frame J K) :
    (comp F E).synthesis = F.synthesis.comp E.synthesis := rfl

@[simp] theorem comp_analysis (F : CalibrationFrame.Frame K G)
    (E : CalibrationFrame.Frame J K) :
    (comp F E).analysis = E.analysis.comp F.analysis := rfl

 theorem comp_analysis_norm_le (F : CalibrationFrame.Frame K G)
    (E : CalibrationFrame.Frame J K) :
    ‖(comp F E).analysis‖ ≤ ‖E.analysis‖*‖F.analysis‖ := by
  exact ContinuousLinearMap.opNorm_comp_le _ _

 theorem hierarchical_operator_bound (F : CalibrationFrame.Frame K G)
    (E : CalibrationFrame.Frame J K) (A C : G →L[ℝ] V) (Y : J →L[ℝ] V)
    (etaCal fit : ℝ) (heta : 0 ≤ etaCal) (hfit : 0 ≤ fit)
    (hA : ‖Y-A.comp (comp F E).synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp (comp F E).synthesis‖ ≤ fit) :
    ‖C-A‖ ≤ (etaCal+fit)*(‖E.analysis‖*‖F.analysis‖) := by
  have h0 : 0 ≤ etaCal+fit := add_nonneg heta hfit
  calc
    ‖C-A‖ ≤ (etaCal+fit)*‖(comp F E).analysis‖ :=
      (comp F E).measured_operator_bound A C Y etaCal fit hA hC
    _ ≤ (etaCal+fit)*(‖E.analysis‖*‖F.analysis‖) :=
      mul_le_mul_of_nonneg_left (comp_analysis_norm_le F E) h0

 theorem hierarchical_allowance_monotone (F : CalibrationFrame.Frame K G)
    (E : CalibrationFrame.Frame J K) (etaCal fit : ℝ)
    (h0 : 0 ≤ etaCal+fit) :
    (etaCal+fit)*‖(comp F E).analysis‖ ≤
      (etaCal+fit)*(‖E.analysis‖*‖F.analysis‖) :=
  mul_le_mul_of_nonneg_left (comp_analysis_norm_le F E) h0

end Komorebi.SufficientResolution.CalibrationHierarchy
