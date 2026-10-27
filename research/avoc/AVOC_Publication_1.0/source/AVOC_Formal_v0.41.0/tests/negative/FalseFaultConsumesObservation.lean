import AVOC.ObservationReveal
open Komorebi.AVOC.ObservationReveal

/-- A fault leaves the next latent outcome available; it cannot consume it. -/
example :
    (run (fun _ : Unit => [false, true]) [none]).remaining () = [true] := by
  decide
