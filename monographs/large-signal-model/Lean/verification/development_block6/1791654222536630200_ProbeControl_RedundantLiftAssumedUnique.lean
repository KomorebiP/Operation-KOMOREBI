import KomorebiLSM.Block6Examples

open scoped BigOperators
open Komorebi.LSM.TestDomains Komorebi.LSM.PositiveLift Komorebi.LSM.RobustDomains Komorebi.LSM.Block6Examples

example : (1 : Matrix (Fin 2) (Fin 2) ℝ) = swapLift := by
  simp only [distinct_positive_lifts.1]
