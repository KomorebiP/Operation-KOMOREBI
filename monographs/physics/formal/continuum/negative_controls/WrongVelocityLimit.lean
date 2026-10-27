import KomorebiPhysics.Relativistic1DContinuumExamples
example : (1 : ℝ) / Real.sqrt 2 = -(1 : ℝ) / Real.sqrt 2 := by
  have h : Real.sqrt 2 ≠ 0 := by positivity
  field_simp [h]
