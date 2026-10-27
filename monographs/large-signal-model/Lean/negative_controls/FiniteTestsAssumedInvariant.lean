import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : delayedState ∈ allTests delayedBranch firstMass := by
  simp only [delayed_not_all_tests]
