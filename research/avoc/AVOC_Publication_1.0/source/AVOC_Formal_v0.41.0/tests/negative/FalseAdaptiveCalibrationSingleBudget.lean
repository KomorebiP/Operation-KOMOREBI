import AVOC.CalibrationSchedule
open Komorebi.AVOC.CalibrationSchedule
/-- Must fail: selecting the observed index turns error 1/2 into error one. -/
example : eventMass fairBoolLaw (fun ω => ω = (fun x : Bool => x) ω) ≤ 1/2 := by
  rw [fairBool_adaptive_failure]
  norm_num
