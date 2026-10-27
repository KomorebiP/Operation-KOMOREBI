import Komorebi.SufficientResolution.CalibrationSelection
import Mathlib.Analysis.Normed.Operator.Prod

/-!
# Calibration examples and the unobserved-direction boundary
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.CalibrationExamples

open CalibrationFrame

/-- A redundant two-coordinate calibration frame for a one-dimensional source. -/
def redundantFrame : CalibrationFrame.Frame (ℝ × ℝ) ℝ where
  synthesis := ContinuousLinearMap.fst ℝ ℝ ℝ
  analysis := ContinuousLinearMap.inl ℝ ℝ ℝ
  reconstruct := by
    apply ContinuousLinearMap.ext
    intro x
    simp

@[simp] theorem redundant_reconstruct (x : ℝ) :
    redundantFrame.synthesis (redundantFrame.analysis x) = x := by simp [redundantFrame]

@[simp] theorem redundant_analysis_norm : ‖redundantFrame.analysis‖ = 1 := by
  simp [redundantFrame, ContinuousLinearMap.norm_inl]

@[simp] theorem redundant_synthesis_norm : ‖redundantFrame.synthesis‖ = 1 := by
  simp [redundantFrame, ContinuousLinearMap.norm_fst]

/-- Calibration of only the first coordinate in a two-dimensional source. -/
def partialCalibration : ℝ →L[ℝ] (ℝ × ℝ) := ContinuousLinearMap.inl ℝ ℝ ℝ

/-- An operator acting only in the direction unseen by `partialCalibration`. -/
def unseen (t : ℝ) : (ℝ × ℝ) →L[ℝ] ℝ :=
  t • ContinuousLinearMap.snd ℝ ℝ ℝ

@[simp] theorem partialCalibration_apply (x : ℝ) : partialCalibration x = (x,0) := rfl

@[simp] theorem unseen_apply (t : ℝ) (x : ℝ × ℝ) : unseen t x = t*x.2 := by
  simp [unseen]

 theorem unseen_comp_partial (t : ℝ) : (unseen t).comp partialCalibration = 0 := by
  apply ContinuousLinearMap.ext
  intro x
  simp [unseen, partialCalibration]

 theorem partial_not_surjective : ¬ Function.Surjective partialCalibration := by
  intro h
  obtain ⟨x, hx⟩ := h (0,1)
  have hs := congrArg Prod.snd hx
  simp [partialCalibration] at hs

 theorem unseen_norm (t : ℝ) (ht : 0 ≤ t) : ‖unseen t‖ = t := by
  simp [unseen, norm_smul, ContinuousLinearMap.norm_snd, Real.norm_eq_abs, abs_of_nonneg ht]

/-- Exact agreement on a proper calibration subspace permits arbitrarily large
operator error on an untested direction. -/
 theorem arbitrarily_large_unseen_error (M : ℝ) :
    ∃ C : (ℝ × ℝ) →L[ℝ] ℝ,
      C.comp partialCalibration = 0 ∧ M < ‖C‖ := by
  let t : ℝ := |M|+1
  have ht : 0 < t := by dsimp [t]; linarith [abs_nonneg M]
  refine ⟨unseen t, unseen_comp_partial t, ?_⟩
  rw [unseen_norm t ht.le]
  dsimp [t]
  linarith [le_abs_self M]

/-- Even zero calibration residual for both truth and model does not control the
whole operator when the calibration synthesis misses a source direction. -/
 theorem perfect_partial_calibration_unbounded (M : ℝ) :
    ∃ C : (ℝ × ℝ) →L[ℝ] ℝ,
      ‖(0 : ℝ →L[ℝ] ℝ) - (0 : (ℝ × ℝ) →L[ℝ] ℝ).comp partialCalibration‖ = 0 ∧
      ‖(0 : ℝ →L[ℝ] ℝ) - C.comp partialCalibration‖ = 0 ∧
      M < ‖C-(0 : (ℝ × ℝ) →L[ℝ] ℝ)‖ := by
  obtain ⟨C, hC, hM⟩ := arbitrarily_large_unseen_error M
  refine ⟨C, by simp, ?_, ?_⟩
  · rw [hC]
    simp
  · simpa using hM

end Komorebi.SufficientResolution.CalibrationExamples
