import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : 0 < firstMass ![(0 : ℝ),1] := by
  rw [unobserved_cone_mass_zero]
  norm_num
