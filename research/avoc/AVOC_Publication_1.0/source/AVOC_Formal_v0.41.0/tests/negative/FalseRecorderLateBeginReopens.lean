import AVOC.ObservationRecorder
open Komorebi.AVOC.ObservationRecorder
/-- Must fail: exact begin replay after completion leaves the operation terminal. -/
example : (run [.begin 7 "warm", .finish ⟨7, "warm", .success⟩,
    .begin 7 "warm"]).map State.pending = some [(7, "warm")] := by decide
