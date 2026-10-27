import PaperXI.AtomicReconstruction
import PaperXI.CharacterProjector

/-! Explicit realization and factor-characterization interfaces for the last
arithmetic step. Realizers need not be unique. Their isomorphism class becomes
unique by equality on a genuinely characterizing test family. No reference
comparison map or final equality is stored in either input interface. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.LocalFactorIdentification

/-- All normalization choices and the admissible comparison range must be part
of the concrete instantiation. `separates` is the external local converse input. -/
structure FactorSystem {Atom : Type*} (s : Setoid Atom) (Test Value : Type*) where
  admissible : Atom → Prop
  profile : Atom → Test → Value
  invariant : ∀ a b, s.r a b → profile a = profile b
  separates : ∀ a b, admissible a → admissible b → profile a = profile b → s.r a b

variable {Atom Test Value D : Type*} {s : Setoid Atom}
variable (S : FactorSystem s Test Value)

/-- Existence of an atom realizing a finite datum is a distinct arithmetic input.
Neither uniqueness nor agreement with a reference atom is assumed here. -/
structure Realization (D : Type*) where
  realizes : D → Atom → Prop
  exists_atom : ∀ d, ∃ a, realizes d a
  admissible : ∀ d a, realizes d a → S.admissible a

variable (R : Realization S D)

def chosenAtom (d : D) : Atom := Classical.choose (R.exists_atom d)

theorem chosenAtom_realizes (d : D) : R.realizes d (chosenAtom S R d) :=
  Classical.choose_spec (R.exists_atom d)

def candidate (d : D) : Quotient s := Quotient.mk s (chosenAtom S R d)

/-- Matching factors characterize equality of isomorphism classes on the declared range. -/
theorem class_eq_iff {a b : Atom} (ha : S.admissible a) (hb : S.admissible b) :
    Quotient.mk s a = Quotient.mk s b ↔ S.profile a = S.profile b := by
  constructor
  · intro h
    exact S.invariant a b (Quotient.exact h)
  · intro h
    exact Quotient.sound (S.separates a b ha hb h)

/-- The reference map and factor identity enter here, not in the finite construction. -/
theorem candidate_eq_reference (d : D) (reference : Atom)
    (hr : S.admissible reference) (expected : Test → Value)
    (hreal : ∀ a, R.realizes d a → S.profile a = expected)
    (href : S.profile reference = expected) :
    candidate S R d = Quotient.mk s reference := by
  apply (class_eq_iff S (R.admissible d _ (chosenAtom_realizes S R d)) hr).mpr
  exact (hreal _ (chosenAtom_realizes S R d)).trans href.symm

/-- A stronger non-vacuous statement: all realized atoms belong to one class.
Existence comes from Realization; separation is used only for uniqueness. -/
theorem unique_realized_class (d : D) (expected : Test → Value)
    (hreal : ∀ a, R.realizes d a → S.profile a = expected) :
    ∃! c : Quotient s, ∃ a, R.realizes d a ∧ Quotient.mk s a = c := by
  refine ⟨candidate S R d, ⟨chosenAtom S R d, chosenAtom_realizes S R d, rfl⟩, ?_⟩
  rintro c ⟨a, ha, rfl⟩
  apply (class_eq_iff S (R.admissible d a ha)
    (R.admissible d _ (chosenAtom_realizes S R d))).mpr
  exact (hreal a ha).trans (hreal _ (chosenAtom_realizes S R d)).symm

/-- Two realization mechanisms give the same class when the tested factor
profile agrees; finite data alone are not a uniqueness theorem. -/
theorem realization_independence (R' : Realization S D) (d : D)
    (expected : Test → Value)
    (h : ∀ a, R.realizes d a → S.profile a = expected)
    (h' : ∀ a, R'.realizes d a → S.profile a = expected) :
    candidate S R d = candidate S R' d := by
  apply candidate_eq_reference S R d (chosenAtom S R' d)
    (R'.admissible d _ (chosenAtom_realizes S R' d)) expected h
  exact h' _ (chosenAtom_realizes S R' d)

/-- Pointwise equality of factor profiles on raw data makes the candidate descend
through any declared source equivalence relation. -/
theorem candidate_congr {d e : D} (expected : D → Test → Value)
    (hreal : ∀ d a, R.realizes d a → S.profile a = expected d)
    (h : expected d = expected e) : candidate S R d = candidate S R e := by
  apply (class_eq_iff S (R.admissible d _ (chosenAtom_realizes S R d))
    (R.admissible e _ (chosenAtom_realizes S R e))).mpr
  exact (hreal d _ (chosenAtom_realizes S R d)).trans
    (h.trans (hreal e _ (chosenAtom_realizes S R e)).symm)

def onClasses (sD : Setoid D) (expected : D → Test → Value)
    (hreal : ∀ d a, R.realizes d a → S.profile a = expected d)
    (hinv : ∀ d e, sD.r d e → expected d = expected e) : Quotient sD → Quotient s :=
  Quotient.lift (candidate S R) (fun d e h => candidate_congr S R expected hreal (hinv d e h))

/-- The factor comparison need only be proved for the actual constructed datum. -/
theorem constructed_comparison {Input : Type*} (build : Input → D) (x : Input)
    (reference : Input → Atom) (hr : S.admissible (reference x))
    (expected : Input → Test → Value)
    (hreal : ∀ a, R.realizes (build x) a → S.profile a = expected x)
    (href : S.profile (reference x) = expected x) :
    candidate S R (build x) = Quotient.mk s (reference x) :=
  candidate_eq_reference S R (build x) (reference x) hr (expected x) hreal href

/-- Conditional atomic agreement propagates through the already constructed
monodromy/multiset reconstruction. This is equality of candidates, not bijectivity. -/
theorem reconstructed_comparison {P A B Target : Type*} {sP : Setoid P}
    (f g : A → B) (D0 : AtomicReconstruction.Decomposition sP A)
    (L : AtomicReconstruction.OrderedQuotient B Target) (h : ∀ a, f a = g a) :
    AtomicReconstruction.candidate f D0 L = AtomicReconstruction.candidate g D0 L := by
  have he : f = g := funext h
  rw [he]

section FiniteCharacterInstance
variable {G V : Type*} [Group G] [Fintype G]
variable [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]

/-- A concrete isomorphism relation, not an arbitrary stand-in for a representation. -/
def representationSetoid : Setoid (Representation ℂ G V) where
  r ρ σ := Nonempty (Representation.Equiv ρ σ)
  iseqv := ⟨fun ρ => ⟨Representation.Equiv.refl ρ⟩,
    fun ⟨e⟩ => ⟨e.symm⟩, fun ⟨e⟩ ⟨f⟩ => ⟨e.trans f⟩⟩

/-- All actual finite-group character values separate irreducibles. This gives a
concrete instance of the interface; it is NOT a local-Weil converse theorem. -/
theorem finite_character_separates (ρ σ : Representation ℂ G V)
    [Representation.IsIrreducible ρ] [Representation.IsIrreducible σ]
    (h : ρ.character = σ.character) : Nonempty (Representation.Equiv ρ σ) := by
  classical
  by_contra hn
  let := CharacterProjector.nontrivial_space σ
  have he : CharacterProjector.element ρ = CharacterProjector.element σ := by
    simp only [CharacterProjector.element, h]
  have hz := CharacterProjector.irreducible_action ρ σ
  have hi := CharacterProjector.irreducible_action σ σ
  have hself : Nonempty (Representation.Equiv σ σ) := ⟨Representation.Equiv.refl σ⟩
  simp only [ite_eq_right hn] at hz
  simp only [ite_eq_left hself] at hi
  rw [he, hi] at hz
  exact one_ne_zero hz

def finiteCharacterSystem : FactorSystem (representationSetoid (G := G) (V := V)) G ℂ where
  admissible ρ := Representation.IsIrreducible ρ
  profile ρ := ρ.character
  invariant ρ σ h := by obtain ⟨e⟩ := h; exact Representation.char_iso e
  separates ρ σ hρ hσ h := by
    let := hρ
    let := hσ
    exact finite_character_separates ρ σ h

end FiniteCharacterInstance
end PaperXI.LocalFactorIdentification
