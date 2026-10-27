import PaperX.SpineCompletionBoundary
open PaperX.SpineCompletionBoundary

example : ∃ c, (emptyClasses (G := (ZMod 2)ˣ) (ι := Fin 1)
    (⊥ : Ideal (ZMod 3))).allowed 1 c := by
  rw [iff_false_intro (emptyClasses_unoccupied
    (G := (ZMod 2)ˣ) (ι := Fin 1) (⊥ : Ideal (ZMod 3)) 1)]
