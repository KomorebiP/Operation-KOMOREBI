import Komorebi.SufficientResolution.GeneralizedDiscrepancyConsistency

/-!
# Split calibration frames

A calibration synthesis need not be injective or square. It is enough to admit a
bounded right inverse, so every source can be reconstructed from calibration
coordinates. This includes redundant calibration frames.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.CalibrationFrame

variable {K G V : Type*}
variable [NormedAddCommGroup K] [NormedSpace ℝ K]
variable [NormedAddCommGroup G] [NormedSpace ℝ G]
variable [NormedAddCommGroup V] [NormedSpace ℝ V]

/-- A split calibration frame. `synthesis` generates physical source states from
calibration coordinates; `analysis` reconstructs coordinates for every source. -/
structure Frame (K G : Type*) [NormedAddCommGroup K] [NormedSpace ℝ K]
    [NormedAddCommGroup G] [NormedSpace ℝ G] where
  synthesis : K →L[ℝ] G
  analysis : G →L[ℝ] K
  reconstruct : synthesis.comp analysis = ContinuousLinearMap.id ℝ G

namespace Frame

variable (F : Frame K G)

@[simp] theorem reconstruct_apply (x : G) : F.synthesis (F.analysis x) = x := by
  have h := congrArg (fun T : G →L[ℝ] G => T x) F.reconstruct
  simpa using h

 theorem synthesis_surjective : Function.Surjective F.synthesis := by
  intro x
  exact ⟨F.analysis x, F.reconstruct_apply x⟩

/-- Every operator is recovered from its action on the calibration frame. -/
 theorem factor_through_frame (T : G →L[ℝ] V) :
    T = (T.comp F.synthesis).comp F.analysis := by
  ext x
  simp only [ContinuousLinearMap.comp_apply, F.reconstruct_apply]

/-- The difference of two operators is recovered from their calibrated difference. -/
 theorem difference_factorization (A C : G →L[ℝ] V) :
    A-C = ((A.comp F.synthesis)-(C.comp F.synthesis)).comp F.analysis := by
  ext x
  simp only [ContinuousLinearMap.comp_apply, sub_apply, F.reconstruct_apply]

/-- Frame conditioning converts calibration-space operator error into whole-source error. -/
 theorem difference_norm_le (A C : G →L[ℝ] V) :
    ‖A-C‖ ≤ ‖(A.comp F.synthesis)-(C.comp F.synthesis)‖ * ‖F.analysis‖ := by
  rw [F.difference_factorization A C]
  exact ContinuousLinearMap.opNorm_comp_le _ _

/-- Calibration against a measured response operator `Y` generates a whole-operator
error allowance. -/
 theorem measured_operator_bound (A C : G →L[ℝ] V) (Y : K →L[ℝ] V)
    (etaCal fit : ℝ)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit) :
    ‖C-A‖ ≤ (etaCal+fit)*‖F.analysis‖ := by
  have hframe : ‖(C.comp F.synthesis)-(A.comp F.synthesis)‖ ≤ etaCal+fit := by
    calc
      _ ≤ ‖C.comp F.synthesis-Y‖ + ‖Y-A.comp F.synthesis‖ :=
        norm_sub_le_norm_sub_add_norm_sub _ _ _
      _ = ‖Y-C.comp F.synthesis‖ + ‖Y-A.comp F.synthesis‖ := by
        rw [norm_sub_rev (C.comp F.synthesis) Y]
      _ ≤ fit+etaCal := add_le_add hC hA
      _ = etaCal+fit := add_comm _ _
  calc
    ‖C-A‖ ≤ ‖(C.comp F.synthesis)-(A.comp F.synthesis)‖*‖F.analysis‖ :=
      F.difference_norm_le C A
    _ ≤ (etaCal+fit)*‖F.analysis‖ :=
      mul_le_mul_of_nonneg_right hframe (norm_nonneg _)

 theorem generated_allowance_nonneg (A C : G →L[ℝ] V) (Y : K →L[ℝ] V)
    (etaCal fit : ℝ)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit) :
    0 ≤ (etaCal+fit)*‖F.analysis‖ := by
  exact (norm_nonneg (C-A)).trans (F.measured_operator_bound A C Y etaCal fit hA hC)

 theorem measured_operator_bound_of_analysis_bound (A C : G →L[ℝ] V) (Y : K →L[ℝ] V)
    (etaCal fit kappa : ℝ)
    (hA : ‖Y-A.comp F.synthesis‖ ≤ etaCal)
    (hC : ‖Y-C.comp F.synthesis‖ ≤ fit)
    (hR : ‖F.analysis‖ ≤ kappa) :
    ‖C-A‖ ≤ (etaCal+fit)*kappa := by
  have heta : 0 ≤ etaCal := (norm_nonneg _).trans hA
  have hfit : 0 ≤ fit := (norm_nonneg _).trans hC
  calc
    ‖C-A‖ ≤ (etaCal+fit)*‖F.analysis‖ :=
      F.measured_operator_bound A C Y etaCal fit hA hC
    _ ≤ (etaCal+fit)*kappa :=
      mul_le_mul_of_nonneg_left hR (add_nonneg heta hfit)

 theorem exact_calibration_identifies (A C : G →L[ℝ] V) (Y : K →L[ℝ] V)
    (hA : Y = A.comp F.synthesis) (hC : Y = C.comp F.synthesis) : A = C := by
  have hcal : A.comp F.synthesis = C.comp F.synthesis := hA.symm.trans hC
  calc
    A = (A.comp F.synthesis).comp F.analysis := F.factor_through_frame A
    _ = (C.comp F.synthesis).comp F.analysis := by rw [hcal]
    _ = C := (F.factor_through_frame C).symm

end Frame

/-- An invertible calibration coordinate system is a special split frame. -/
def ofEquiv (U : K ≃L[ℝ] G) : Frame K G where
  synthesis := U.toContinuousLinearMap
  analysis := U.symm.toContinuousLinearMap
  reconstruct := by
    ext x
    simp

@[simp] theorem ofEquiv_synthesis (U : K ≃L[ℝ] G) :
    (ofEquiv U).synthesis = U.toContinuousLinearMap := rfl

@[simp] theorem ofEquiv_analysis (U : K ≃L[ℝ] G) :
    (ofEquiv U).analysis = U.symm.toContinuousLinearMap := rfl

 theorem equiv_calibration_bound (U : K ≃L[ℝ] G) (A C : G →L[ℝ] V)
    (Y : K →L[ℝ] V) (etaCal fit : ℝ)
    (hA : ‖Y-A.comp U.toContinuousLinearMap‖ ≤ etaCal)
    (hC : ‖Y-C.comp U.toContinuousLinearMap‖ ≤ fit) :
    ‖C-A‖ ≤ (etaCal+fit)*‖U.symm.toContinuousLinearMap‖ := by
  exact (ofEquiv U).measured_operator_bound A C Y etaCal fit hA hC

end Komorebi.SufficientResolution.CalibrationFrame
