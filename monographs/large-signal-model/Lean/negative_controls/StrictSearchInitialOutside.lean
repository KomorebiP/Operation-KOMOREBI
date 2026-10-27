import KomorebiLSM.RationalTransform

open Komorebi.LSM.RationalTransform

-- Mass one alone does not pass the independent strict initial-state check.
example : StrictVector ![1,2,0] := by
  change (0 : ℚ)<1 ∧ (2 : ℚ)^2+0^2<1^2
  norm_num
