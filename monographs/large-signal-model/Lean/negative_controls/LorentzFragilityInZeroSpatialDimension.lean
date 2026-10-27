import KomorebiLSM.LorentzBoundaryFragility

/-! Zero boundary images are covered in positive dimension. Zero spatial
dimension, however, admits no nonzero mass-row-zero perturbation. -/
open Komorebi.LSM LorentzCylinder LorentzBoundaryFragility

example : ∃ Delta : State ℝ →L[ℝ] State ℝ,
    (ContinuousLinearMap.fst ℝ ℝ ℝ).comp Delta=0 ∧
    Module.finrank ℝ (LinearMap.range Delta.toLinearMap)=1 ∧
    normalizedSize Delta=1 ∧ ((0 : State ℝ →L[ℝ] State ℝ)+Delta) (1,0)∉cone := by
  apply boundary_fragility 0 _ 0 (by norm_num) (by simp) 1 (by norm_num)
  intro z _
  simp only [zero_apply]
  exact probabilityCone.zero_mem

example : ∃ Delta : State (EuclideanSpace ℝ (Fin 0)) →L[ℝ] State (EuclideanSpace ℝ (Fin 0)),
    (ContinuousLinearMap.fst ℝ ℝ (EuclideanSpace ℝ (Fin 0))).comp Delta=0 ∧ normalizedSize Delta=1 := by
  have h := zero_dimensional_impossibility (V := EuclideanSpace ℝ (Fin 0)) 1 (by norm_num)
  rw [iff_false_intro h]
