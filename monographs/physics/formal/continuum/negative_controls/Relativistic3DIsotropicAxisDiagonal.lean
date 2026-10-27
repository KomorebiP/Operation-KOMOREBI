import KomorebiPhysics.Relativistic3DContinuumExamples
open KomorebiPhysics.Relativistic3DAnisotropy
open KomorebiPhysics.Relativistic3DContinuumExamples
-- Intentionally false: the massless unit-radius anisotropy coefficient is nonzero.
example : (1 : ℝ)^4 / (18 * fixedRadiusEnergy 0 1) = 0 := by
  rw [massless_unit_axis_diagonal_coefficient]
