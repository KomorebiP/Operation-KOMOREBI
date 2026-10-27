import AVOC.ObservationRecorder
open Komorebi.AVOC.ObservationRecorder
/-- Must fail: a terminal outcome requires the matching previously recorded intent. -/
example : step (initial : State String) (.finish ⟨7, "warm", .success⟩) =
    some ⟨[], [⟨7, "warm", .success⟩]⟩ := by decide
