import AVOC.ObservationRecorder
open Komorebi.AVOC.ObservationRecorder
open Komorebi.AVOC.CalibrationLog
/-- Must fail: exact terminal replay cannot duplicate the checked statistical sample. -/
example : (run [.begin 7 "warm", .finish ⟨7, "warm", .success⟩,
    .finish ⟨7, "warm", .success⟩]).map (fun s => samples "warm" s.log) =
    some [true, true] := by decide
