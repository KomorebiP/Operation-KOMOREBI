import PaperXII.RepresentationData
import PaperXII.DenseFrobenius

/-! Paper XII 9.4, conditional Galois identification with the arithmetic topology
made explicit. Frobenius density, semisimplification existence and algebraic
Brauer–Nesbitt remain supplied standard inputs. Dense extension and all actual
representation comparisons are derived. -/
set_option autoImplicit false
namespace PaperXII.GaloisRealization

open Matrix RepresentationData DenseFrobenius

variable {E Γ Ω ι : Type*} [Field E] [CharZero E] [Group Γ]
    [TopologicalSpace E] [IsTopologicalRing E] [T2Space E]
    [TopologicalSpace Γ] [Fintype ι] [DecidableEq ι]

/-- The semisimplification of a continuous representation is identified with a
semisimple attached representation using only the general standard input. -/
theorem pointwise_semisimple_identification (bn : BrauerNesbitt E Γ ι)
    (ρ σ : Γ →ₜ* GL ι E) (s : Semisimplification ρ.toMonoidHom)
    (hσ : Representation.IsSemisimpleRepresentation (representation σ.toMonoidHom))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good))
    (hpoly : ∀ v, good v → (ρ (frob v)).val.charpoly = (σ (frob v)).val.charpoly) :
    Isomorphic s.rep σ.toMonoidHom := by
  have hall := charpoly_eq_of_dense_frobenius ρ σ frob good hdense hpoly
  exact bn s.rep σ.toMonoidHom s.semisimple hσ
    (fun g ↦ (s.charpoly_eq g).trans (hall g))

/-- The irreducible case gives an isomorphism of the original representations. -/
theorem pointwise_irreducible_identification (bn : BrauerNesbitt E Γ ι)
    (ρ σ : Γ →ₜ* GL ι E)
    (hρ : Representation.IsIrreducible (representation ρ.toMonoidHom))
    (hσ : Representation.IsSemisimpleRepresentation (representation σ.toMonoidHom))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good))
    (hpoly : ∀ v, good v → (ρ (frob v)).val.charpoly = (σ (frob v)).val.charpoly) :
    Isomorphic ρ.toMonoidHom σ.toMonoidHom :=
  bn ρ.toMonoidHom σ.toMonoidHom (irreducible_semisimple _ hρ) hσ
    (charpoly_eq_of_dense_frobenius ρ σ frob good hdense hpoly)

/-- Both printed conclusions for an arbitrary mapped Hecke polynomial spine. -/
theorem common_spine_identification {B : Type*} [CommRing B]
    (bn : BrauerNesbitt E Γ ι) (ρ σ : Γ →ₜ* GL ι E)
    (s : Semisimplification ρ.toMonoidHom)
    (hσ : Representation.IsSemisimpleRepresentation (representation σ.toMonoidHom))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good)) (x : B →+* E)
    (P : Ω → Polynomial B)
    (hρP : ∀ v, good v → (ρ (frob v)).val.charpoly = (P v).map x)
    (hσP : ∀ v, good v → (σ (frob v)).val.charpoly = (P v).map x) :
    Isomorphic s.rep σ.toMonoidHom ∧
      (Representation.IsIrreducible (representation ρ.toMonoidHom) →
        Isomorphic ρ.toMonoidHom σ.toMonoidHom) := by
  have heq : ∀ v, good v →
      (ρ (frob v)).val.charpoly = (σ (frob v)).val.charpoly :=
    fun v hv ↦ (hρP v hv).trans (hσP v hv).symm
  exact ⟨pointwise_semisimple_identification bn ρ σ s hσ frob good hdense heq,
    fun hρ ↦ pointwise_irreducible_identification bn ρ σ hρ hσ frob good hdense heq⟩

variable {R : Type*} [CommRing R]

/-- Actual coefficient specialization of the universal matrix representation. -/
def specialize (ρR : Γ →* GL ι R) (x : R →+* E) : Γ →* GL ι E :=
  (GeneralLinearGroup.map x).comp ρR

omit [CharZero E] [TopologicalSpace E] [IsTopologicalRing E] [T2Space E]
    [TopologicalSpace Γ] in
/-- Specialization maps every coefficient of the universal characteristic polynomial. -/
theorem specialize_charpoly (ρR : Γ →* GL ι R) (x : R →+* E) (g : Γ) :
    (specialize ρR x g).val.charpoly = ((ρR g).val.charpoly).map x :=
  Matrix.charpoly_map _ _

/-- Continuity of the specialization under consideration is explicit. -/
def continuousSpecialization (ρR : Γ →* GL ι R) (x : R →+* E)
    (hx : Continuous (specialize ρR x)) : Γ →ₜ* GL ι E :=
  { __ := specialize ρR x, continuous_toFun := hx }

/-- Source-shaped pointwise realization: the compared representation is literally
x composed with the supplied universal representation. -/
theorem universal_pointwise_realization {T : Type*} [CommRing T]
    (bn : BrauerNesbitt E Γ ι) (ρR : Γ →* GL ι R) (x : R →+* E)
    (hx : Continuous (specialize ρR x))
    (s : Semisimplification (specialize ρR x))
    (σ : Γ →ₜ* GL ι E)
    (hσ : Representation.IsSemisimpleRepresentation (representation σ.toMonoidHom))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good))
    (y : T →+* E) (P : Ω → Polynomial T)
    (hρP : ∀ v, good v → (specialize ρR x (frob v)).val.charpoly = (P v).map y)
    (hσP : ∀ v, good v → (σ (frob v)).val.charpoly = (P v).map y) :
    Isomorphic s.rep σ.toMonoidHom ∧
      (Representation.IsIrreducible (representation (specialize ρR x)) →
        Isomorphic (specialize ρR x) σ.toMonoidHom) :=
  common_spine_identification bn (continuousSpecialization ρR x hx) σ s hσ
    frob good hdense y P hρP hσP

end PaperXII.GaloisRealization
