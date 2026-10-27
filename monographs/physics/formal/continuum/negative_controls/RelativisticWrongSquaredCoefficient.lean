import KomorebiPhysics.Relativistic1DAsymptoticExamples
open KomorebiPhysics.Relativistic1DShellAsymptotics
open KomorebiPhysics.Relativistic1DAsymptoticAlgebra
open KomorebiPhysics.Relativistic1DAsymptoticExamples
example : 2 * energy 1 1 * correction 1 1 = (1/3 : ℝ) := by
  rw [squared_coefficient_one_one]
  norm_num
