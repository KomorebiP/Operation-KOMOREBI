import KomorebiPhysics.Relativistic3DCombinedDefect

open KomorebiPhysics.Relativistic3DCombinedDefect

/-- Deliberately false: an edge budget constantly equal to one is not summable. -/
example : Summable (combinedScaleBudget (fun _ : ℕ => 1) (fun _ : ℕ => 0)) := by
  simpa [combinedScaleBudget]
