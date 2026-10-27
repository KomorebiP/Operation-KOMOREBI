import Mathlib.RepresentationTheory.Semisimple
import Mathlib.RepresentationTheory.Irreducible
import Mathlib.LinearAlgebra.Matrix.GeneralLinearGroup.Defs
import Mathlib.LinearAlgebra.Matrix.Charpoly.Basic

/-! Actual matrix actions and explicit standard finite-dimensional algebra inputs.
Semisimplification is specified by a semisimple representative with the same
characteristic polynomials. Its existence and the general Brauer–Nesbitt theorem
are external inputs; no particular comparison is supplied as an assumption. -/
set_option autoImplicit false
namespace PaperXII.RepresentationData

open Matrix

variable {E Γ ι : Type*} [Field E] [Group Γ] [Fintype ι] [DecidableEq ι]

/-- The actual linear action associated with an invertible matrix representation. -/
def representation (ρ : Γ →* GL ι E) : Representation E Γ (ι → E) :=
  (Units.coeHom (Module.End E (ι → E))).comp
    (GeneralLinearGroup.toLin.toMonoidHom.comp ρ)

/-- This action applies the original matrix to the original coordinate vector. -/
theorem representation_apply (ρ : Γ →* GL ι E) (g : Γ) (v : ι → E) :
    representation ρ g v = (ρ g).val.mulVec v := rfl

/-- Isomorphism means an actual invertible linear intertwiner. -/
abbrev Isomorphic (ρ σ : Γ →* GL ι E) :=
  Nonempty (Representation.Equiv (representation ρ) (representation σ))

/-- A supplied semisimplification representative, characterized in characteristic zero
by actual semisimplicity and preservation of all characteristic polynomials.
No chosen automorphic representation or comparison is part of this datum. -/
structure Semisimplification (ρ : Γ →* GL ι E) where
  rep : Γ →* GL ι E
  semisimple : Representation.IsSemisimpleRepresentation (representation rep)
  charpoly_eq : ∀ g, (rep g).val.charpoly = (ρ g).val.charpoly

/-- The general algebraic Brauer–Nesbitt input from Fact 9.2. This universally
quantifies over representations, independently of points or automorphic data. -/
def BrauerNesbitt (E Γ ι : Type*) [Field E] [CharZero E] [Group Γ]
    [Fintype ι] [DecidableEq ι] : Prop :=
  ∀ (ρ σ : Γ →* GL ι E),
    Representation.IsSemisimpleRepresentation (representation ρ) →
    Representation.IsSemisimpleRepresentation (representation σ) →
    (∀ g, (ρ g).val.charpoly = (σ g).val.charpoly) → Isomorphic ρ σ

/-- An irreducible representation is semisimple in the actual subrepresentation lattice. -/
theorem irreducible_semisimple (ρ : Γ →* GL ι E)
    (hρ : Representation.IsIrreducible (representation ρ)) :
    Representation.IsSemisimpleRepresentation (representation ρ) := by
  let := hρ
  infer_instance

/-- A semisimple representation is itself a valid semisimplification representative. -/
def selfSemisimplification (ρ : Γ →* GL ι E)
    (hρ : Representation.IsSemisimpleRepresentation (representation ρ)) :
    Semisimplification ρ := ⟨ρ, hρ, fun _ ↦ rfl⟩

variable [CharZero E]

/-- Any two supplied semisimplifications are isomorphic; choice of representative is harmless. -/
theorem semisimplification_unique (bn : BrauerNesbitt E Γ ι) (ρ : Γ →* GL ι E)
    (s t : Semisimplification ρ) : Isomorphic s.rep t.rep := by
  exact bn s.rep t.rep s.semisimple t.semisimple
    (fun g ↦ (s.charpoly_eq g).trans (t.charpoly_eq g).symm)

/-- Semisimplification fixes any semisimple representation up to an actual intertwiner. -/
theorem semisimplification_of_semisimple (bn : BrauerNesbitt E Γ ι)
    (ρ : Γ →* GL ι E) (s : Semisimplification ρ)
    (hρ : Representation.IsSemisimpleRepresentation (representation ρ)) :
    Isomorphic ρ s.rep :=
  bn ρ s.rep hρ s.semisimple (fun g ↦ (s.charpoly_eq g).symm)

/-- The irreducible conclusion is derived, rather than included in the supplied choice. -/
theorem semisimplification_of_irreducible (bn : BrauerNesbitt E Γ ι)
    (ρ : Γ →* GL ι E) (s : Semisimplification ρ)
    (hρ : Representation.IsIrreducible (representation ρ)) : Isomorphic ρ s.rep :=
  semisimplification_of_semisimple bn ρ s (irreducible_semisimple ρ hρ)

/-- Applying semisimplification twice does not change its isomorphism class. -/
theorem semisimplification_idempotent (bn : BrauerNesbitt E Γ ι)
    (ρ : Γ →* GL ι E) (s : Semisimplification ρ) (t : Semisimplification s.rep) :
    Isomorphic s.rep t.rep :=
  semisimplification_of_semisimple bn s.rep t s.semisimple

end PaperXII.RepresentationData
