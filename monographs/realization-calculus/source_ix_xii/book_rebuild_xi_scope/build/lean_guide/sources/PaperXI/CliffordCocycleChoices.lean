import PaperXI.CliffordCocycle

/-! Explicit cocycle and commutator comparisons for all actual section and
intertwiner choices in the Clifford construction. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordCocycleChoices
open CliffordDatum CliffordMultiplicity CliffordChoices CocycleCommutator
open scoped IsMulCommutative

variable {G W X : Type*} [Group G]
variable [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
variable (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
variable (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
variable (π : Representation ℂ G X) (hρ : Invariant N ρ) [Nontrivial (Space N ρ π)]

/-- The cocycle for arbitrary actual choices, with its explicit constructed coboundary. -/
def choiceCocycle (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a))) : Cocycle (G ⧸ N) ℂˣ :=
  rescale (CliffordCocycle.cocycle N ρ π hρ) (choiceCochain N ρ hρ s hs I)

/-- The displayed coboundary is the multiplication cocycle of the actual chosen operators. -/
theorem choiceOperator_mul (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a))) (a b : G ⧸ N) :
    (operator N ρ π (s a) (I a)).toLinearMap * (operator N ρ π (s b) (I b)).toLinearMap =
      ((choiceCocycle N ρ π hρ s hs I).coeff a b : ℂ) •
        (operator N ρ π (s (a * b)) (I (a * b))).toLinearMap :=
  ProjectiveCocycle.rescaledFamily_mul
    (fun a => (sectionOperator N ρ π hρ a).toLinearMap)
    (fun a => (operator N ρ π (s a) (I a)).toLinearMap)
    (CliffordCocycle.cocycle N ρ π hρ) (CliffordCocycle.sectionOperator_mul N ρ π hρ)
    (choiceCochain N ρ hρ s hs I) (arbitrary_choices N ρ π hρ s hs I) a b

/-- Every other coefficient family with the actual multiplication law is this cocycle. -/
theorem choiceCocycle_unique (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a))) (d : Cocycle (G ⧸ N) ℂˣ)
    (hd : ∀ a b, (operator N ρ π (s a) (I a)).toLinearMap *
      (operator N ρ π (s b) (I b)).toLinearMap =
        (d.coeff a b : ℂ) • (operator N ρ π (s (a * b)) (I (a * b))).toLinearMap) :
    d = choiceCocycle N ρ π hρ s hs I := by
  have he (a b : G ⧸ N) : d.coeff a b = (choiceCocycle N ρ π hρ s hs I).coeff a b := by
    apply ProjectiveCocycle.scalar_injective (operator N ρ π (s (a * b)) (I (a * b))).toLinearMap
    · intro h
      obtain ⟨f, hf⟩ := exists_ne (0 : Space N ρ π)
      have hz := LinearMap.congr_fun h f
      exact hf ((operator N ρ π (s (a * b)) (I (a * b))).injective
        (hz.trans (operator N ρ π (s (a * b)) (I (a * b))).map_zero.symm))
    · exact (hd a b).symm.trans (choiceOperator_mul N ρ π hρ s hs I a b)
  have hcoeff := funext (fun a => funext (he a))
  cases d
  unfold choiceCocycle rescale
  congr 1

/-- The intrinsic commutator is unchanged by any section and intertwiner choices. -/
theorem commutator_choice (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a))) (a b : G ⧸ N) :
    commutator (choiceCocycle N ρ π hρ s hs I) a b =
      commutator (CliffordCocycle.cocycle N ρ π hρ) a b :=
  commutator_rescale _ _ a b

/-- Consequently the actual radical subgroup is choice independent. -/
theorem radical_choice (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a))) :
    radical (choiceCocycle N ρ π hρ s hs I) = radical (CliffordCocycle.cocycle N ρ π hρ) :=
  radical_rescale _ _

/-- If the alternative actual identity operator is normalized, its comparing cochain is too. -/
theorem choiceCochain_one (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a)))
    (hI : (operator N ρ π (s 1) (I 1)).toLinearMap = 1) :
    choiceCochain N ρ hρ s hs I 1 = 1 := by
  apply ProjectiveCocycle.cochain_one
    (fun a => (sectionOperator N ρ π hρ a).toLinearMap)
    (fun a => (operator N ρ π (s a) (I a)).toLinearMap)
    (CliffordCocycle.sectionOperator_ne_zero N ρ π hρ 1)
    _ hI (choiceCochain N ρ hρ s hs I) (arbitrary_choices N ρ π hρ s hs I)
  exact congrArg LinearEquiv.toLinearMap (sectionOperator_one N ρ π hρ)

/-- The actual cocycle of normalized choices is normalized. -/
theorem choiceCocycle_normalized (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a)))
    (hI : (operator N ρ π (s 1) (I 1)).toLinearMap = 1) :
    Normalized (choiceCocycle N ρ π hρ s hs I) :=
  normalized_rescale _ (CliffordCocycle.normalized N ρ π hρ) _
    (choiceCochain_one N ρ π hρ s hs I hI)

end PaperXI.CliffordCocycleChoices
