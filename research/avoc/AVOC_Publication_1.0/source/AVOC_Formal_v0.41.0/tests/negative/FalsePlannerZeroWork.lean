import AVOC.ExecutablePlanner
open Komorebi.AVOC.ExecutablePlanner
example (m : Model Unit Unit Unit) : (evaluate m 0 ()).work = 0 := by
  change 1 = 0
  decide
