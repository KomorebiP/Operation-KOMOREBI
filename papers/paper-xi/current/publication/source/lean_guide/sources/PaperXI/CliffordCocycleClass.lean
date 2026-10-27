import PaperXI.CocycleClass
import PaperXI.CliffordCocycleChoices
import PaperXI.CliffordTransport
import PaperXI.CliffordSource

/-! The class of the actual Clifford multiplicity cocycle in the explicit
quotient of normalized cocycles by normalized scalar coboundaries. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CliffordCocycleClass

open CliffordDatum CliffordMultiplicity CocycleCommutator
open scoped IsMulCommutative
variable {G W X : Type*} [Group G]
  [AddCommGroup W] [Module ℂ W] [AddCommGroup X] [Module ℂ X]
  (N : Subgroup G) [N.Normal] [IsMulCommutative (G ⧸ N)]
  (ρ : Representation ℂ N W) [Representation.IsIrreducible ρ] [FiniteDimensional ℂ W]
  (π : Representation ℂ G X) (hρ : Invariant N ρ) [Nontrivial (Space N ρ π)]

/-- The cohomological class of the actual Clifford multiplicity action. -/
def value : CocycleClass.Class (G ⧸ N) ℂˣ :=
  CocycleClass.of (CliffordCocycle.cocycle N ρ π hρ) (CliffordCocycle.normalized N ρ π hρ)

@[simp] theorem commutator_value (a b : G ⧸ N) :
    CocycleClass.commutator (value N ρ π hρ) a b =
      commutator (CliffordCocycle.cocycle N ρ π hρ) a b := rfl

@[simp] theorem radical_value :
    CocycleClass.radical (value N ρ π hρ) = radical (CliffordCocycle.cocycle N ρ π hρ) := rfl

/-- Any normalized actual section/intertwiner choice has precisely the same class. -/
theorem choice_class (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a)))
    (hI : (operator N ρ π (s 1) (I 1)).toLinearMap = 1) :
    CocycleClass.of (CliffordCocycleChoices.choiceCocycle N ρ π hρ s hs I)
      (CliffordCocycleChoices.choiceCocycle_normalized N ρ π hρ s hs I hI) = value N ρ π hρ :=
  CocycleClass.of_rescale (CliffordCocycle.cocycle N ρ π hρ)
    (CliffordCocycle.normalized N ρ π hρ) (CliffordChoices.choiceCochain N ρ hρ s hs I)
    (CliffordCocycleChoices.choiceCochain_one N ρ π hρ s hs I hI)

/-- Class independence also holds for any independently supplied actual multiplication coefficients. -/
theorem class_of_multiplication (s : G ⧸ N → G) (hs : ∀ a, QuotientGroup.mk' N (s a) = a)
    (I : ∀ a, Representation.Equiv ρ (conjugate N ρ (s a)))
    (hI : (operator N ρ π (s 1) (I 1)).toLinearMap = 1)
    (d : Cocycle (G ⧸ N) ℂˣ) (hd : Normalized d)
    (hmul : ∀ a b, (operator N ρ π (s a) (I a)).toLinearMap *
      (operator N ρ π (s b) (I b)).toLinearMap =
        (d.coeff a b : ℂ) • (operator N ρ π (s (a * b)) (I (a * b))).toLinearMap) :
    CocycleClass.of d hd = value N ρ π hρ := by
  have he := CliffordCocycleChoices.choiceCocycle_unique N ρ π hρ s hs I d hmul
  subst d
  exact choice_class N ρ π hρ s hs I hI

section Transport
variable {G' W' X' : Type*} [Group G']
  [AddCommGroup W'] [Module ℂ W'] [AddCommGroup X'] [Module ℂ X']
  (N' : Subgroup G') [N'.Normal] [IsMulCommutative (G' ⧸ N')]
  (e : G ≃* G') (hN : N.map e.toMonoidHom = N')
  (ρ' : Representation ℂ N' W') [Representation.IsIrreducible ρ'] [FiniteDimensional ℂ W']
  (π' : Representation ℂ G' X') [Nontrivial (Space N' ρ' π')]
  (E : Representation.Equiv ρ (ρ'.comp (CliffordTransport.subgroupEquiv N N' e hN).toMonoidHom))
  (F : Representation.Equiv π (π'.comp e.toMonoidHom)) (hρ' : Invariant N' ρ')

include E F

/-- Actual isomorphisms of the original data preserve the cocycle class under quotient pullback. -/
theorem value_transport :
    CocycleClass.pullback (CliffordTransport.quotientEquiv N N' e hN).toMonoidHom
      (value N' ρ' π' hρ') = value N ρ π hρ := by
  unfold value
  rw [CocycleClass.pullback_of]
  symm
  apply CocycleClass.of_eq_of_rescale _ _ _ _ (CliffordTransport.cochain N N' e hN ρ ρ' E hρ hρ')
    (CliffordTransport.cochain_one N N' e hN ρ ρ' π π' E F hρ hρ')
  apply CocycleClass.cocycle_ext
  intro a b
  exact CliffordTransport.cocycle_transport N N' e hN ρ ρ' π π' E F hρ hρ' a b

end Transport

/-- The class for a finite source datum, with dimension and nonzero multiplicity derived. -/
def sourceValue [Finite G] [Representation.IsIrreducible π]
    (h : CliffordIrreducible.Isotypic N ρ π) : CocycleClass.Class (G ⧸ N) ℂˣ :=
  CocycleClass.of (CliffordSource.cocycle N ρ π h hρ) (CliffordSource.normalized N ρ π h hρ)

section SourceTransport
variable {G' W' X' : Type*} [Group G'] [Finite G] [Finite G']
  [AddCommGroup W'] [Module ℂ W'] [AddCommGroup X'] [Module ℂ X']
  (N' : Subgroup G') [N'.Normal] [IsMulCommutative (G' ⧸ N')]
  (e : G ≃* G') (hN : N.map e.toMonoidHom = N')
  (ρ' : Representation ℂ N' W') [Representation.IsIrreducible ρ']
  (π' : Representation ℂ G' X') [Representation.IsIrreducible π] [Representation.IsIrreducible π']
  (E : Representation.Equiv ρ (ρ'.comp (CliffordTransport.subgroupEquiv N N' e hN).toMonoidHom))
  (F : Representation.Equiv π (π'.comp e.toMonoidHom)) (hρ' : Invariant N' ρ')
  (h : CliffordIrreducible.Isotypic N ρ π) (h' : CliffordIrreducible.Isotypic N' ρ' π')

include E F

omit [FiniteDimensional ℂ W] [Nontrivial (Space N ρ π)] in
/-- Source 9.7 cocycle-class invariance from actual finite group and representation isomorphisms. -/
theorem source_transport :
    CocycleClass.pullback (CliffordTransport.quotientEquiv N N' e hN).toMonoidHom
      (sourceValue N' ρ' π' hρ' h') = sourceValue N ρ π hρ h := by
  let : FiniteDimensional ℂ W := FiniteRepresentation.finiteDimensional ρ
  let : FiniteDimensional ℂ W' := FiniteRepresentation.finiteDimensional ρ'
  let : Nontrivial (Space N ρ π) := CliffordIrreducible.multiplicity_nontrivial N ρ π h
  let : Nontrivial (Space N' ρ' π') := CliffordIrreducible.multiplicity_nontrivial N' ρ' π' h'
  exact value_transport N ρ π hρ N' e hN ρ' π' E F hρ'

end SourceTransport
end PaperXI.CliffordCocycleClass
