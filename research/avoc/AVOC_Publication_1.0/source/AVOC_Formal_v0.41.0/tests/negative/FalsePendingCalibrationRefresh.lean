import AVOC.CalibrationLog
open Komorebi.AVOC.CalibrationLog
/-- Must fail: in-flight intent prevents a quote refresh. -/
example : refresh true (7 : Nat) = some 7 := by decide
