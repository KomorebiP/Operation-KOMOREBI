import LogicalBoundaries
open Komorebi.ModelTheory
example : existsTrueObservation.Sat oneObservedState (fun i => nomatch i) := by decide
