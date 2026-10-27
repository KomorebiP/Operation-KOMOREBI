import KomorebiPhysics.Relativistic1DAsymptoticExamples
open KomorebiPhysics.Dispersion1D
open KomorebiPhysics.Relativistic1DShellAsymptotics
example : iteratedDeriv 6 (fun ε => shell 1 1 ε) 0 = 32 := by
  norm_num [shell_deriv6_zero]
