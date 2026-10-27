import BealBlock47
open KomorebiBeal.Block47
example : ((freySexticModSeven 1 1) ^ 3).coeff 5 = 0 := by
  rw [frey_cube_coeff_five]
  decide
