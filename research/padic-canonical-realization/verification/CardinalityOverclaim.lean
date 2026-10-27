import KomorebiPadic.ObservabilityExamples
open KomorebiPadic.LinearObservability
example : Nat.card (State twiceIdentity) = 4 := by
  rw [twiceIdentity_quotient_card]
  decide
