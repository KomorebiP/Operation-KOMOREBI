import AVOC.ObservationReveal
open Komorebi.AVOC.ObservationReveal

/-- The first checked report must include the rejection, not skip to success. -/
example :
    (run (fun _ : Unit => [false, true]) [some ()]).reports () = [true] := by
  decide
