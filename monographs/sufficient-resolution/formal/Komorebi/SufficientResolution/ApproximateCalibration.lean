import Komorebi.SufficientResolution.CalibrationFrame

/-!
# Approximate calibration reconstruction

Exact split reconstruction can be relaxed. If synthesis followed by analysis is within
rho<1 of the identity, calibrated operator error still controls the whole operator,
with the expected factor 1/(1-rho).
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.ApproximateCalibration

variable {K G V : Type*}
variable [NormedAddCommGroup K] [NormedSpace ℝ K]
variable [NormedAddCommGroup G] [NormedSpace ℝ G]
variable [NormedAddCommGroup V] [NormedSpace ℝ V]

 theorem approximate_factorization (U : K →L[ℝ] G) (R : G →L[ℝ] K)
    (T : G →L[ℝ] V) :
    T = (T.comp U).comp R + T.comp (ContinuousLinearMap.id ℝ G-U.comp R) := by
  apply ContinuousLinearMap.ext
  intro x
  simp only [ContinuousLinearMap.comp_apply, add_apply, sub_apply,
    ContinuousLinearMap.id_apply, map_sub]
  abel

 theorem approximate_frame_bound (U : K →L[ℝ] G) (R : G →L[ℝ] K)
    (T : G →L[ℝ] V) (rho : ℝ) (hrho : rho < 1)
    (hrec : ‖ContinuousLinearMap.id ℝ G-U.comp R‖ ≤ rho) :
    ‖T‖ ≤ (‖T.comp U‖*‖R‖)/(1-rho) := by
  have hsum : ‖T‖ ≤ ‖T.comp U‖*‖R‖ + ‖T‖*rho := by
    calc
      ‖T‖ = ‖(T.comp U).comp R + T.comp (ContinuousLinearMap.id ℝ G-U.comp R)‖ :=
        congrArg norm (approximate_factorization U R T)
      _ ≤ ‖(T.comp U).comp R‖ + ‖T.comp (ContinuousLinearMap.id ℝ G-U.comp R)‖ :=
        norm_add_le _ _
      _ ≤ (‖T.comp U‖*‖R‖) + (‖T‖*‖ContinuousLinearMap.id ℝ G-U.comp R‖) :=
        add_le_add (ContinuousLinearMap.opNorm_comp_le _ _) (ContinuousLinearMap.opNorm_comp_le _ _)
      _ ≤ (‖T.comp U‖*‖R‖) + (‖T‖*rho) :=
        add_le_add le_rfl (mul_le_mul_of_nonneg_left hrec (norm_nonneg T))
  rw [le_div_iff₀ (sub_pos.mpr hrho)]
  nlinarith

 theorem measured_approximate_operator_bound (U : K →L[ℝ] G) (R : G →L[ℝ] K)
    (A C : G →L[ℝ] V) (Y : K →L[ℝ] V) (etaCal fit rho : ℝ)
    (hrho : rho < 1)
    (hrec : ‖ContinuousLinearMap.id ℝ G-U.comp R‖ ≤ rho)
    (hA : ‖Y-A.comp U‖ ≤ etaCal) (hC : ‖Y-C.comp U‖ ≤ fit) :
    ‖C-A‖ ≤ ((etaCal+fit)*‖R‖)/(1-rho) := by
  have hcal : ‖(C-A).comp U‖ ≤ etaCal+fit := by
    have hident : (C-A).comp U = C.comp U-A.comp U := by
      apply ContinuousLinearMap.ext
      intro x
      simp
    rw [hident]
    calc
      _ ≤ ‖C.comp U-Y‖+‖Y-A.comp U‖ := norm_sub_le_norm_sub_add_norm_sub _ _ _
      _ = ‖Y-C.comp U‖+‖Y-A.comp U‖ := by rw [norm_sub_rev (C.comp U) Y]
      _ ≤ fit+etaCal := add_le_add hC hA
      _ = etaCal+fit := add_comm _ _
  calc
    ‖C-A‖ ≤ (‖(C-A).comp U‖*‖R‖)/(1-rho) :=
      approximate_frame_bound U R (C-A) rho hrho hrec
    _ ≤ ((etaCal+fit)*‖R‖)/(1-rho) := by
      apply div_le_div_of_nonneg_right _ (sub_pos.mpr hrho).le
      exact mul_le_mul_of_nonneg_right hcal (norm_nonneg R)

 theorem exact_reconstruction_specialization (U : K →L[ℝ] G) (R : G →L[ℝ] K)
    (T : G →L[ℝ] V) (hrec : U.comp R = ContinuousLinearMap.id ℝ G) :
    ‖T‖ ≤ ‖T.comp U‖*‖R‖ := by
  have hz : ‖ContinuousLinearMap.id ℝ G-U.comp R‖ ≤ (0:ℝ) := by simp [hrec]
  have h := approximate_frame_bound U R T 0 (by norm_num) hz
  simpa using h

end Komorebi.SufficientResolution.ApproximateCalibration
