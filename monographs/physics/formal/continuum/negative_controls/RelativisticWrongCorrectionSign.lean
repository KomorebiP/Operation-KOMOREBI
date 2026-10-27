import KomorebiPhysics.Relativistic1DAsymptoticExamples
open KomorebiPhysics.Relativistic1DShellAsymptotics
open KomorebiPhysics.Relativistic1DAsymptoticAlgebra
open KomorebiPhysics.Relativistic1DAsymptoticExamples
example : correction 1 1 = 1 / (6 * Real.sqrt 2) := by
  rw [correction_one_one]
  have hs : Real.sqrt 2 ≠ 0 := by positivity
  field_simp [hs]
