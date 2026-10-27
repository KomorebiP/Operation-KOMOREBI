import PaperXII.PerfectCohomology
import PaperXII.DerivedHeckeAction
import PaperXII.DerivedPatching
import PaperXII.HeckeFibers
import PaperXII.GaloisRealization

/-!
# Derived eigensystems and conditional automorphic realization

Cohomology, the induced Hecke action, and the representation intertwiners are
actual mathematical objects. The classicality input is applied to a nonzero
vector in a proved degree range. Arithmetic occurrence, attached representations,
Frobenius density, semisimplification, and general Brauer--Nesbitt remain explicit
external inputs. No final representation comparison is assumed.
-/

noncomputable section

open CategoryTheory CategoryTheory.Limits

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.DerivedRealization

open PerfectDerivedSupport PerfectCohomology DerivedHeckeAction HeckeFibers

variable {R T E : Type u} [CommRing R] [CommRing T] [Field E]

/-- A nonzero vector with the eigenvalues of the actual induced Hecke operators. -/
def IsEigenvector (C : PerfectComplex T) (y : T →+* E) (n : ℤ)
    (z : cohomology (C.baseChange y) n) : Prop :=
  z ≠ 0 ∧ ∀ t : T, perfectCohomologyOperator C y n t z = y t • z

/-- The tensor relation on the original complex supplies every eigenvalue. -/
theorem isEigenvector_of_ne_zero (C : PerfectComplex T) (y : T →+* E) (n : ℤ)
    (z : cohomology (C.baseChange y) n) (hz : z ≠ 0) : IsEigenvector C y n z :=
  ⟨hz, fun t => perfectCohomologyOperator_apply C y n t z⟩

/-- Full support produces an actual eigensystem within the projective model's bounds. -/
theorem derived_pointwise_eigensystem (C : PerfectComplex T) (e : R ≃+* T)
    (x : R →+* E) (hC : FullSupport C) :
    ¬IsZero (C.baseChange (transportedPoint e x)).object ∧
      ∃ n : ℤ, C.model.lower ≤ n ∧ n ≤ C.model.upper ∧
        ∃ z : cohomology (C.baseChange (transportedPoint e x)) n,
          IsEigenvector C (transportedPoint e x) n z := by
  refine ⟨nonzero_fiber_of_fullSupport C (transportedPoint e x) hC, ?_⟩
  obtain ⟨n, hlo, hhi, z, hz⟩ :=
    exists_nonzero_fiber_vector_in_range C (transportedPoint e x) hC
  exact ⟨n, hlo, hhi, z, isEigenvector_of_ne_zero C _ n z hz⟩

variable {A : Type u} [CommRing A]

/-- The Hecke-side complex is compared by an actual derived isomorphism to
scalar transport of the patched finite-level complex. -/
theorem completion_hecke_fullSupport (D : DerivedPatching.Datum A R)
    (e : R ≃+* T) (C : PerfectComplex T)
    (comparison : C.object ≅ (D.finitePerfect.baseChange e.toRingHom).object)
    (hD : FullSupport D.patched) : FullSupport C := by
  unfold FullSupport
  rw [support_eq_of_iso comparison]
  exact fullSupport_baseChange D.finitePerfect e.toRingHom
    (DerivedPatching.fullSupport_descends D hD)

/-- The unconditional part of original Theorem 12.4: actual fiber nonvanishing
and an actual nonzero Hecke cohomology vector with bounded integer degree. -/
theorem derived_completion_eigensystem (D : DerivedPatching.Datum A R)
    (e : R ≃+* T) (C : PerfectComplex T)
    (comparison : C.object ≅ (D.finitePerfect.baseChange e.toRingHom).object)
    (hD : FullSupport D.patched) (x : R →+* E) :
    ¬IsZero (C.baseChange (transportedPoint e x)).object ∧
      ∃ n : ℤ, C.model.lower ≤ n ∧ n ≤ C.model.upper ∧
        ∃ z : cohomology (C.baseChange (transportedPoint e x)) n,
          IsEigenvector C (transportedPoint e x) n z :=
  derived_pointwise_eigensystem C e x (completion_hecke_fullSupport D e C comparison hD)

section Realization

open Matrix RepresentationData DenseFrobenius GaloisRealization

variable {Γ Ω ι Auto : Type u} [CharZero E]
    [TopologicalSpace E] [IsTopologicalRing E] [T2Space E]
    [Group Γ] [TopologicalSpace Γ] [Fintype ι] [DecidableEq ι]

/-- Revised Theorem 9.6. Every degree in the model interval belongs to the
specified classicality range. The input supplies an attached representation,
its occurrence and its Frobenius polynomials, not the resulting isomorphism. -/
theorem derived_pointwise (C : PerfectComplex T) (e : R ≃+* T)
    (x : R →+* E) (hC : FullSupport C) (degrees : Set ℤ)
    (hdegrees : ∀ n, C.model.lower ≤ n → n ≤ C.model.upper → n ∈ degrees)
    (bn : BrauerNesbitt E Γ ι) (ρR : Γ →* GL ι R)
    (hx : Continuous (specialize ρR x)) (s : Semisimplification (specialize ρR x))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good)) (P : Ω → Polynomial T)
    (hρP : ∀ v, good v → (specialize ρR x (frob v)).val.charpoly =
      (P v).map (transportedPoint e x))
    (occurs : ℤ → Auto → Prop) (attached : Auto → Γ →ₜ* GL ι E)
    (classicality : ∀ n, n ∈ degrees →
      ∀ z : cohomology (C.baseChange (transportedPoint e x)) n,
        IsEigenvector C (transportedPoint e x) n z →
          ∃ π : Auto, occurs n π ∧
            Representation.IsSemisimpleRepresentation (representation (attached π).toMonoidHom) ∧
            ∀ v, good v → (attached π (frob v)).val.charpoly =
              (P v).map (transportedPoint e x)) :
    ¬IsZero (C.baseChange (transportedPoint e x)).object ∧
      ∃ n : ℤ, C.model.lower ≤ n ∧ n ≤ C.model.upper ∧ n ∈ degrees ∧
        ∃ z : cohomology (C.baseChange (transportedPoint e x)) n,
          IsEigenvector C (transportedPoint e x) n z ∧
          ∃ π : Auto, occurs n π ∧ Isomorphic s.rep (attached π).toMonoidHom ∧
            (Representation.IsIrreducible (representation (specialize ρR x)) →
              Isomorphic (specialize ρR x) (attached π).toMonoidHom) := by
  obtain ⟨hne, n, hlo, hhi, z, hz⟩ := derived_pointwise_eigensystem C e x hC
  have hn := hdegrees n hlo hhi
  obtain ⟨π, hocc, hsemi, hpoly⟩ := classicality n hn z hz
  exact ⟨hne, n, hlo, hhi, hn, z, hz, π, hocc,
    universal_pointwise_realization bn ρR x hx s (attached π) hsemi frob good hdense
      (transportedPoint e x) P hρP hpoly⟩

/-- Realization may instead be assumed only for the particular nonzero
cohomology eigensystem under consideration, as in Theorem 12.4. -/
theorem realize_eigensystem (C : PerfectComplex T) (e : R ≃+* T) (x : R →+* E)
    (n : ℤ) (z : cohomology (C.baseChange (transportedPoint e x)) n)
    (hz : IsEigenvector C (transportedPoint e x) n z)
    (bn : BrauerNesbitt E Γ ι) (ρR : Γ →* GL ι R)
    (hx : Continuous (specialize ρR x)) (s : Semisimplification (specialize ρR x))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good)) (P : Ω → Polynomial T)
    (hρP : ∀ v, good v → (specialize ρR x (frob v)).val.charpoly =
      (P v).map (transportedPoint e x))
    (occurs : ℤ → Auto → Prop) (attached : Auto → Γ →ₜ* GL ι E)
    (classicality : IsEigenvector C (transportedPoint e x) n z →
      ∃ π : Auto, occurs n π ∧
        Representation.IsSemisimpleRepresentation (representation (attached π).toMonoidHom) ∧
        ∀ v, good v → (attached π (frob v)).val.charpoly =
          (P v).map (transportedPoint e x)) :
    ∃ π : Auto, occurs n π ∧ Isomorphic s.rep (attached π).toMonoidHom ∧
      (Representation.IsIrreducible (representation (specialize ρR x)) →
        Isomorphic (specialize ρR x) (attached π).toMonoidHom) := by
  obtain ⟨π, hocc, hsemi, hpoly⟩ := classicality hz
  exact ⟨π, hocc, universal_pointwise_realization bn ρR x hx s (attached π) hsemi
    frob good hdense (transportedPoint e x) P hρP hpoly⟩

/-- Revised Theorem 12.4, retaining its pointwise applicability condition.
The nonzero eigensystem is constructed first. If the declared realization
input supplies an attached object for that eigensystem, comparison follows. -/
theorem derived_conditional_completion (D : DerivedPatching.Datum A R)
    (e : R ≃+* T) (C : PerfectComplex T)
    (comparison : C.object ≅ (D.finitePerfect.baseChange e.toRingHom).object)
    (hD : FullSupport D.patched) (x : R →+* E)
    (bn : BrauerNesbitt E Γ ι) (ρR : Γ →* GL ι R)
    (hx : Continuous (specialize ρR x)) (s : Semisimplification (specialize ρR x))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good)) (P : Ω → Polynomial T)
    (hρP : ∀ v, good v → (specialize ρR x (frob v)).val.charpoly =
      (P v).map (transportedPoint e x))
    (occurs : ℤ → Auto → Prop) (attached : Auto → Γ →ₜ* GL ι E) :
    ¬IsZero (C.baseChange (transportedPoint e x)).object ∧
      ∃ n : ℤ, C.model.lower ≤ n ∧ n ≤ C.model.upper ∧
        ∃ z : cohomology (C.baseChange (transportedPoint e x)) n,
          IsEigenvector C (transportedPoint e x) n z ∧
          ((∃ π : Auto, occurs n π ∧
            Representation.IsSemisimpleRepresentation (representation (attached π).toMonoidHom) ∧
            ∀ v, good v → (attached π (frob v)).val.charpoly =
              (P v).map (transportedPoint e x)) →
            ∃ π : Auto, occurs n π ∧ Isomorphic s.rep (attached π).toMonoidHom ∧
              (Representation.IsIrreducible (representation (specialize ρR x)) →
                Isomorphic (specialize ρR x) (attached π).toMonoidHom)) := by
  obtain ⟨hne, n, hlo, hhi, z, hz⟩ := derived_completion_eigensystem D e C comparison hD x
  refine ⟨hne, n, hlo, hhi, z, hz, ?_⟩
  intro hclassical
  exact realize_eigensystem C e x n z hz bn ρR hx s frob good hdense P hρP
    occurs attached (fun _ => hclassical)

end Realization

end PaperXII.DerivedRealization
