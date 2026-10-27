import PaperXII.DenseFrobenius
import PaperXII.RepresentationData

set_option autoImplicit false

/-! Paper XII, Theorems 10.7 and 12.5. Two already existing families of actual
continuous matrix representations carry the same coefficient-field polynomial
spine. Density of the good Frobenius conjugacy classes gives equality of their
characteristic polynomials everywhere. The universally quantified algebraic
Brauer--Nesbitt input then gives actual invertible linear intertwiners.

The distinguished member and its ordinary or derived completion datum are
unnecessary after both families and the common spine have been supplied, as
the source statements explicitly assume. No missing companion is constructed,
and the derived completion theorem 12.4 is not asserted here. -/
namespace PaperXII.ExistingCompatibleSystems

open Matrix
open PaperXII.RepresentationData

variable {Λ Ω Γ ι L : Type*} [Group Γ] [TopologicalSpace Γ]
    [Fintype ι] [DecidableEq ι] [Field L]
    {E : Λ → Type*} [∀ l, Field (E l)] [∀ l, TopologicalSpace (E l)]
    [∀ l, IsTopologicalRing (E l)] [∀ l, T2Space (E l)]

/-- The common mapped spine determines all characteristic polynomials at every
declared coefficient place, even when the good set depends on that place. -/
theorem memberwise_charpoly_eq
    (ρ σ : ∀ l, Γ →ₜ* GL ι (E l)) (frob : Ω → Γ) (good : Λ → Ω → Prop)
    (hdense : ∀ l, Dense (PaperXII.DenseFrobenius.conjugacySaturation frob (good l)))
    (emb : ∀ l, L →+* E l) (P : Ω → Polynomial L)
    (hρ : ∀ l v, good l v → (ρ l (frob v)).val.charpoly = (P v).map (emb l))
    (hσ : ∀ l v, good l v → (σ l (frob v)).val.charpoly = (P v).map (emb l)) :
    ∀ l g, (ρ l g).val.charpoly = (σ l g).val.charpoly := by
  intro l
  exact PaperXII.DenseFrobenius.common_spine_charpoly_eq
    (ρ l) (σ l) frob (good l) (hdense l) (emb l) P (hρ l) (hσ l)

variable [∀ l, CharZero (E l)]

/-- Theorem 10.7: a semisimple existing family is isomorphic member by member
to the semisimplification of the supplied attached family with the same spine.
The attached family itself need not be semisimple. -/
theorem one_member_propagation
    (ρ σ : ∀ l, Γ →ₜ* GL ι (E l)) (frob : Ω → Γ) (good : Λ → Ω → Prop)
    (hdense : ∀ l, Dense (PaperXII.DenseFrobenius.conjugacySaturation frob (good l)))
    (emb : ∀ l, L →+* E l) (P : Ω → Polynomial L)
    (hρ : ∀ l v, good l v → (ρ l (frob v)).val.charpoly = (P v).map (emb l))
    (hσ : ∀ l v, good l v → (σ l (frob v)).val.charpoly = (P v).map (emb l))
    (hsemisimple : ∀ l, Representation.IsSemisimpleRepresentation
      (representation (ρ l).toMonoidHom))
    (ss : ∀ l, Semisimplification (σ l).toMonoidHom)
    (bn : ∀ l, BrauerNesbitt (E l) Γ ι) :
    ∀ l, Isomorphic (ρ l).toMonoidHom (ss l).rep := by
  intro l
  apply bn l (ρ l).toMonoidHom (ss l).rep (hsemisimple l) (ss l).semisimple
  intro g
  exact (memberwise_charpoly_eq ρ σ frob good hdense emb P hρ hσ l g).trans
    ((ss l).charpoly_eq g).symm

/-- Theorem 12.5, with actual memberwise intertwining equivalences selected
simultaneously. Both representation families already exist in the hypotheses.
The earlier completion at one member supplies its arithmetic interpretation;
it does not replace the common-spine or existence hypotheses used here. -/
theorem system_completion
    (ρ σ : ∀ l, Γ →ₜ* GL ι (E l)) (frob : Ω → Γ) (good : Λ → Ω → Prop)
    (hdense : ∀ l, Dense (PaperXII.DenseFrobenius.conjugacySaturation frob (good l)))
    (emb : ∀ l, L →+* E l) (P : Ω → Polynomial L)
    (hρ : ∀ l v, good l v → (ρ l (frob v)).val.charpoly = (P v).map (emb l))
    (hσ : ∀ l v, good l v → (σ l (frob v)).val.charpoly = (P v).map (emb l))
    (hsemisimple : ∀ l, Representation.IsSemisimpleRepresentation
      (representation (ρ l).toMonoidHom))
    (ss : ∀ l, Semisimplification (σ l).toMonoidHom)
    (bn : ∀ l, BrauerNesbitt (E l) Γ ι) :
    Nonempty (∀ l, Representation.Equiv (representation (ρ l).toMonoidHom)
      (representation (ss l).rep)) := by
  classical
  exact ⟨fun l => Classical.choice
    (one_member_propagation ρ σ frob good hdense emb P hρ hσ hsemisimple ss bn l)⟩

end PaperXII.ExistingCompatibleSystems
