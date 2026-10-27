import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : (∑ o, crossedBranches ((),o) 1) = (1 : ℝ) := by
  rw [independent_branch_mixing_breaks_mass]
  norm_num
