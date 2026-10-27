import PaperX.FamilyExamples
open PaperX.FamilyExamples PaperX.OrthogonalProjectors PaperX.PrecisionExamples
example : ∃ E : Family tau3 (Fin 3), ∀ i : Fin 3,
    (E.projector i).matrix.map modFour = (pAdicProjectors i).map modFour := by
  rw [iff_false_intro no_exact_family_retains_mod_four]
