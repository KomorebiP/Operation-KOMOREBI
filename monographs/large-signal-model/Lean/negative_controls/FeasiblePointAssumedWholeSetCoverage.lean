import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : ValidFamily (Set.Ici (0 : ℝ)) LinearMap.id (coinFamily (3/2)) := by
  simp only [feasible_member_is_not_whole_set_valid.2]
