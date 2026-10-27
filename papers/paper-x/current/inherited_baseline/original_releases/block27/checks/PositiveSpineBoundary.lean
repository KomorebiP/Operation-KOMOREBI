import PaperX.SpineCompletionBoundary
open PaperX.RepresentationLimits PaperX.RepresentationClasses PaperX.ClassCompletion
open PaperX.InverseLimitLocalConditions PaperX.SpineCompletionBoundary

example : ∀ k, ∃ c, (allClasses (G := (ZMod 2)ˣ) (ι := Fin 1)
    (⊥ : Ideal (ZMod 3))).allowed k c :=
  allClasses_occupied (⊥ : Ideal (ZMod 3))

example (k : ℕ) : Finite {c // (allClasses (G := (ZMod 2)ˣ) (ι := Fin 1)
    (⊥ : Ideal (ZMod 3))).allowed k c} :=
  allClasses_finite (⊥ : Ideal (ZMod 3)) k

example : ∀ P : MatrixRep (ZMod 3) (ZMod 2)ˣ (Fin 1) → Prop,
    InverseLimitClosed (⊥ : Ideal (ZMod 3))
      (emptyClasses (⊥ : Ideal (ZMod 3))) P :=
  emptyClasses_closed (⊥ : Ideal (ZMod 3))

example : ¬ InverseLimitClosed (⊥ : Ideal (ZMod 3))
    (allClasses (G := (ZMod 2)ˣ) (ι := Fin 1) (⊥ : Ideal (ZMod 3)))
    (fun _ => False) :=
  allClasses_not_closed_false (⊥ : Ideal (ZMod 3))

example (ρ : MatrixRep (ZMod 3) (ZMod 2)ˣ (Fin 1)) :
    transitionClass (⊥ : Ideal (ZMod 3)) (by decide : 1 ≤ 3)
      ((classBranchOfRepresentation (⊥ : Ideal (ZMod 3)) ρ).value 3) =
        (classBranchOfRepresentation (⊥ : Ideal (ZMod 3)) ρ).value 1 :=
  classBranchOfRepresentation_compatible (⊥ : Ideal (ZMod 3)) ρ (by decide)
