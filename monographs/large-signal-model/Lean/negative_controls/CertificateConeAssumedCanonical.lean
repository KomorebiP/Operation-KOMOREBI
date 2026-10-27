import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : ![(1 : ℝ),0] ∈ hull intervalSynthesis := by
  simp only [certified_subcone_can_be_strict.2]
