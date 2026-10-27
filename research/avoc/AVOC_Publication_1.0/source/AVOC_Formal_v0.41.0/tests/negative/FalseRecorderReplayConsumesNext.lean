import AVOC.RecorderReveal
open Komorebi.AVOC.RecorderReveal
/-- Must fail: replay of the same report consumes no second source outcome. -/
example :
    (run (fun _ : Unit => [false, true]) [.begin 0 (), .report 0 (), .report 0 ()]).map
      (fun s => Komorebi.AVOC.CalibrationLog.samples () s.recorder.log) =
        some [false, true] := by decide
