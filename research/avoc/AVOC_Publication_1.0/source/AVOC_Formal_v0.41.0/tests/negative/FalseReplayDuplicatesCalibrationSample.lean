import AVOC.CalibrationLog
open Komorebi.AVOC.CalibrationLog
/-- Must fail: exact replay preserves the existing log. -/
example : record [⟨1,"warm",.success⟩] ⟨1,"warm",.success⟩ =
    some [⟨1,"warm",.success⟩,⟨1,"warm",.success⟩] := by decide
