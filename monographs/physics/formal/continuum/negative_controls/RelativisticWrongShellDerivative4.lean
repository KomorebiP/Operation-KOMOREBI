import KomorebiPhysics.Relativistic1DAsymptoticExamples
open KomorebiPhysics.Dispersion1D
open KomorebiPhysics.Relativistic1DShellAsymptotics
example : iteratedDeriv 4 (fun ε => shell 1 1 ε) 0 = 4 := by
  norm_num [shell_deriv4_zero]
