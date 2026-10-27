import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : ![(0 : ℝ),1] = 0 := by
  simp only [unobserved_ray_nonzero]
