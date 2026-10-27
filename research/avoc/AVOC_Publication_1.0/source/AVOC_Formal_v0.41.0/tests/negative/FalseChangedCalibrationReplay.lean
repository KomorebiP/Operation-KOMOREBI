import AVOC.CalibrationLog
open Komorebi.AVOC.CalibrationLog
/-- Must fail: a changed outcome under an existing operation id is rejected. -/
example : record [⟨1,"warm",.success⟩] ⟨1,"warm",.rejection⟩ =
    some [⟨1,"warm",.success⟩,⟨1,"warm",.rejection⟩] := by decide
