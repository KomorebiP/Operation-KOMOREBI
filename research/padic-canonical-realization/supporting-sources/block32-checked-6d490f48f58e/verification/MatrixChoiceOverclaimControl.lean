import KomorebiPadic.PresentationExamples
open KomorebiPadic.FiniteModulePresentation
example : entry identityFivePresentation nilpotentFive (0 : Fin 2) (1 : Fin 2) =
    entry swappedFivePresentation nilpotentFive (0 : Fin 2) (1 : Fin 2) := by
  rw [signature_does_not_choose_matrix.2.1, signature_does_not_choose_matrix.2.2]
  change (1 : ZMod 5) = 0
  decide +kernel
