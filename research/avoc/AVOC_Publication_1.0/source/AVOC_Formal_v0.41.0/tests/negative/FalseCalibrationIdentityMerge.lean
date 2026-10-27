import AVOC.CalibrationLog
open Komorebi.AVOC.CalibrationLog
/-- Must fail: a different identity does not contribute a sample. -/
example : samples "cold" [⟨1,"warm",.success⟩] = [true] := by decide
