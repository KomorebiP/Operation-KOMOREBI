import KomorebiPhysics
open KomorebiPhysics
example : pairCurrent (1 : ℂ →L[ℂ] ℂ) 1 1 = 0 := by
  norm_num [pairCurrent]
