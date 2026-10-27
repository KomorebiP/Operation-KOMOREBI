import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : testLevel delayedBranch firstMass 2 = testLevel delayedBranch firstMass 1 := by
  simp only [delayed_level_one_not_stable]
