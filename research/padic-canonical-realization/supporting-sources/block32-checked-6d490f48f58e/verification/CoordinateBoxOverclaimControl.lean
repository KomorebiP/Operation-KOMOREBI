import KomorebiPadic.ReachabilityExamples
open KomorebiPadic LinearReachability
example : Nat.card (State correlated) = 125 := by
  rw [correlated_reachable_card]
  decide
