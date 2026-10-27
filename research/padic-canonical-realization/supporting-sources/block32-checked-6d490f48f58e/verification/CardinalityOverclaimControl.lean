import KomorebiPadic.PresentationExamples
open KomorebiPadic.FiniteModulePresentation
example : Nonempty (ZMod 4 ≃+ (Fin 2 → ZMod 2)) := by
  have h := equal_cardinality_not_isomorphic.2
  rw [iff_false_intro h]
  decide +kernel
