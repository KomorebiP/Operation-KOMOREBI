import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : ‖(1 : ℝ)-(-1)‖ ≤ 1 := by
  norm_num
