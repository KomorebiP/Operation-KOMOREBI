import PaperXII.CompletionBoundaryChecks
example {O : Type*} [CommRing O] [Nontrivial O] :
    PaperXII.FiniteTensor.definingIdeal (O := O) (fun (_ : Fin 0) ↦ O) ⊤ (fun _ ↦ ⊥) = ⊥ := by
  simp [PaperXII.FiniteTensor.definingIdeal, PaperXII.FiniteTensor.conditions]
