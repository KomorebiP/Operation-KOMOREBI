import AVOC.CalibrationLog
open Komorebi.AVOC.CalibrationLog
/-- Must fail at the proposition: a fault creates no binary sample. -/
example : samples "warm" [⟨1,"warm",.fault⟩] = [false] := by decide
