import AVOC.RecorderReveal
open Komorebi.AVOC.RecorderReveal
/-- Must fail: a new report cannot fabricate an outcome after source exhaustion. -/
example :
    (run (fun _ : Unit => [true]) [.begin 0 (), .report 0 (), .begin 1 (), .report 1 ()]).map
      (fun _ => true) = some true := by decide
