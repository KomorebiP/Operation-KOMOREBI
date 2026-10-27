import AVOC.RecorderReveal
open Komorebi.AVOC.RecorderReveal
/-- Must fail: a terminal fault cannot be replaced by a later report. -/
example :
    (run (fun _ : Unit => [true]) [.begin 0 (), .fault 0 (), .report 0 ()]).map
      (fun _ => true) = some true := by decide
