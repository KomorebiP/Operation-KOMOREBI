import KomorebiSpace.ProtectedHilbertRepair
-- The identity observable forbids changing the nonzero identity defect.
example : KomorebiSpace.ProtectedHilbertRepair.Feasible (ContinuousLinearMap.id ℝ ℝ)
    (ContinuousLinearMap.id ℝ ℝ) 1 := by
  refine ⟨⟨0, by simp⟩, ?_⟩
  norm_num [KomorebiSpace.ProtectedHilbertRepair.restricted]
