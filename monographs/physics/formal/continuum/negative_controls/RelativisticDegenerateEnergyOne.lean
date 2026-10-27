import KomorebiPhysics.Relativistic1DAsymptoticExamples
open KomorebiPhysics.Relativistic1DShellAsymptotics
example : energy 0 0 = 1 := by
  norm_num [energy]
