import KomorebiPadic.ObservabilityExamples
open KomorebiPadic.LinearObservability
example : (1 : ZMod 4) ∈ unobservable twiceIdentity := by
  rw [twiceIdentity_unobservable_mem]
  decide +kernel
