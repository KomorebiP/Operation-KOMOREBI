import KomorebiPhysics.Relativistic3DContinuumExamples
open KomorebiPhysics.Relativistic3DContinuumLimit
open KomorebiPhysics.Relativistic3DContinuumExamples
-- Intentionally false: the leading lattice correction has the opposite sign.
example : correction3 1 1 0 0 = (1 : ℝ) / (6 * Real.sqrt 2) := by
  rw [correction3_one_one_zero_zero]
