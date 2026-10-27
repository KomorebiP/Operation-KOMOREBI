import KomorebiPadic.ReachabilityExamples
open KomorebiPadic LinearReachability
example : ∃ ds : List (Fin 1), run constantOrbit ds constantOrbit.initial = 0 := by
  change ∃ ds : List (Fin 1), run constantOrbit ds 1 = (0 : ZMod 5)
  simp only [constantOrbit_run, exists_const]
  decide
