import KomorebiPhysics
open KomorebiPhysics
example : pairCurrent ((-Complex.I) • (1 : ℂ →L[ℂ] ℂ)) 1 Complex.I = -2 := by
  norm_num [pairCurrent]
