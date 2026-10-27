import PaperX.FiniteAvoidanceBoundary
import PaperX.IrreducibleCharacterRigidity

/-! Two limitations of passing through a quotient. Non-surjective restriction
can identify inequivalent irreducible representations. Coverage in one finite
quotient does not imply coverage in a larger group. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.SurjectivePullbackBoundary
open PaperX.CompletionExamples PaperX.QuadraticCharacters
open PaperX.FiniteAvoidanceBoundary PaperX.ProfiniteSeparation

/-- The actual one-dimensional sign representation over a characteristic-zero field. -/
def signRepresentation : Representation ℚ C2 ℚ :=
  (algebraMap ℚ (Module.End ℚ ℚ)).toMonoidHom.comp
    ((Units.coeHom ℚ).comp signCharacter)

def trivialRepresentation : Representation ℚ C2 ℚ := 1

/-- A homomorphism missing the nonidentity element. -/
def collapsedMap : C2 →* C2 := 1

theorem collapsedMap_not_surjective : ¬ Function.Surjective collapsedMap := by
  intro h
  obtain ⟨g, hg⟩ := h generator
  exact generator_ne_one hg.symm

/-- Every rational representation on the one-dimensional rational vector space
is irreducible, independently of its acting group. -/
theorem rational_line_irreducible {G : Type*} [Monoid G]
    (ρ : Representation ℚ G ℚ) : ρ.IsIrreducible := by
  change IsSimpleOrder (Subrepresentation ρ)
  refine { exists_pair_ne := ?_, eq_bot_or_eq_top := ?_ }
  · refine ⟨⊥, ⊤, ?_⟩
    intro h
    have hh := congrArg Subrepresentation.toSubmodule h
    exact bot_ne_top hh
  · intro W
    rcases eq_bot_or_eq_top W.toSubmodule with h | h
    · exact Or.inl (Subrepresentation.toSubmodule_injective h)
    · exact Or.inr (Subrepresentation.toSubmodule_injective h)

instance : signRepresentation.IsIrreducible := rational_line_irreducible _
instance : trivialRepresentation.IsIrreducible := rational_line_irreducible _

theorem representations_not_equivalent :
    ¬ Nonempty (signRepresentation.Equiv trivialRepresentation) := by
  intro h
  have hc := PaperX.IrreducibleCharacterRigidity.character_eq_of_equiv
    signRepresentation trivialRepresentation h
  have hg := congrFun hc generator
  norm_num [Representation.character, signRepresentation, trivialRepresentation,
    signCharacter, Algebra.algebraMap_eq_smul_one] at hg

theorem collapsed_pullbacks_equal :
    signRepresentation.comp collapsedMap = trivialRepresentation.comp collapsedMap := by
  ext g
  simp [collapsedMap]

/-- The actual restricted representations admit an equivariant linear isomorphism. -/
theorem collapsed_pullbacks_equivalent :
    Nonempty (Representation.Equiv (signRepresentation.comp collapsedMap)
      (trivialRepresentation.comp collapsedMap)) := by
  rw [collapsed_pullbacks_equal]
  exact ⟨Representation.Equiv.refl _⟩

/-- Samples chosen entirely in the first factor of a larger finite group. -/
def quotientSamples (g : C2) : C2 × C2 := (g, 1)

theorem projected_samples_surjective :
    Function.Surjective (fun g : C2 => (quotientSamples g).1) := by
  intro g
  exact ⟨g, rfl⟩

theorem projected_samples_coverage :
    QuotientCoverage (fun g : C2 => (quotientSamples g).1) := by
  intro H g
  exact ⟨g, 1, by simp [quotientSamples]⟩

theorem quotient_samples_not_conjugacy_dense :
    ¬ DenseRange (fun p : C2 × (C2 × C2) =>
      p.2 * quotientSamples p.1 * p.2⁻¹) := by
  intro hd
  obtain ⟨p, hp⟩ := denseRange_discrete.mp hd (1, generator)
  have hh := congrArg Prod.snd hp
  simp [quotientSamples] at hh
  exact generator_ne_one hh.symm

theorem quotient_samples_coverage_fails : ¬ QuotientCoverage quotientSamples := by
  intro hc
  exact quotient_samples_not_conjugacy_dense
    (dense_of_quotient_coverage quotientSamples hc)

end PaperX.SurjectivePullbackBoundary
