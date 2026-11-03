import CoupledUniqueness
open Komorebi.SpecialFunctions.Coupled.Scales

-- Analyticity and zero initial values alone do not supply the differential equations.
example : workedScales.IsEntireSolution (fun _ : ℂ => 0) (fun _ => 0) := by
  refine ⟨rfl, rfl, ?_⟩
  intro z
  constructor <;> simpa using (hasDerivAt_const z (0 : ℂ))
