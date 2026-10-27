import KomorebiPhysics.Relativistic3DHilbertScalarDefect

/-- Deliberately false: a defect budget constantly equal to one is not summable. -/
example : Summable (fun _ : ℕ => (1 : ℝ)) := by
  simpa
