import AVOC.RecorderReveal
open Komorebi.AVOC.RecorderReveal
/-- Must fail: an unresolved begun operation blocks issuance. -/
example :
    (run (fun _ : Unit => [true]) [.begin 0 ()]).map (fun s => issue s (7 : Nat)) =
      some (some 7) := by decide
