import PaperX.SpineCompletionBoundary
open PaperX.InverseLimitLocalConditions PaperX.SpineCompletionBoundary

example : InverseLimitClosed (⊥ : Ideal (ZMod 3))
    (allClasses (G := (ZMod 2)ˣ) (ι := Fin 1) (⊥ : Ideal (ZMod 3)))
    (fun _ => False) := by
  rw [iff_false_intro (allClasses_not_closed_false
    (G := (ZMod 2)ˣ) (ι := Fin 1) (⊥ : Ideal (ZMod 3)))]
