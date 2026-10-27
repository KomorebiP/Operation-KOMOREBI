import PaperXII.OrdinaryPatching
import PaperXII.HeckeFibers
import PaperXII.GaloisRealization

/-! Paper XII, revised Corollary 9.5 and Theorem 12.2.
The inputs are the printed patched module, quotient identifications, patched
full support, and Hecke identification. Finite-level support is derived.
The arithmetic occurrence and attached-representation statements remain declared
classicality inputs. Hausdorff coefficient topology and representation continuity
are explicit, as in the revised pointwise realization theorem. -/
set_option autoImplicit false
namespace PaperXII.OrdinaryCompletion

open scoped TensorProduct
open ModuleSupport FieldFibers HeckeFibers

section Support

variable {A R T E P H : Type*}
    [CommRing A] [IsNoetherianRing A] [CommRing R] [CommRing T] [Field E]
    [Algebra A R] [Algebra R T]
    [AddCommGroup P] [Module A P] [Module.Finite A P]
    [AddCommGroup H] [Module A H] [Module R H] [Module T H]
    [IsScalarTower A R H] [IsScalarTower R T H]

omit [IsNoetherianRing A] in
/-- Finite generation at finite level follows from the actual control isomorphism. -/
theorem finite_level_finite (I : Ideal A)
    (eM : (P ⧸ (I • ⊤ : Submodule A P)) ≃ₗ[A] H) : Module.Finite R H := by
  let : Module.Finite A H := Module.Finite.equiv eM
  exact Module.Finite.of_restrictScalars_finite A R H

/-- The full finite-level support needed by completion is a conclusion of the
patched support and actual quotient identifications. -/
theorem finite_level_fullSupport (I : Ideal A)
    (eR : (A ⧸ I) ≃ₐ[A] R)
    (eM : (P ⧸ (I • ⊤ : Submodule A P)) ≃ₗ[A] H)
    (hP : FullSupport A P) : FullSupport R H :=
  (OrdinaryPatching.conclusions_of_quotient_identifications I eR eM hP).1

/-- Full Hecke support is transported along the supplied ring identification. -/
theorem hecke_fullSupport (I : Ideal A)
    (eR : (A ⧸ I) ≃ₐ[A] R)
    (eM : (P ⧸ (I • ⊤ : Submodule A P)) ≃ₗ[A] H)
    (eT : R ≃ₐ[R] T) (hP : FullSupport A P) : FullSupport T H := by
  have he : eT.toRingHom = algebraMap R T := by
    ext r
    exact eT.commutes r
  have hbij : Function.Bijective (algebraMap R T) := by
    rw [← he]
    exact eT.bijective
  exact (SupportTransport.fullSupport_iff hbij).mp
    (finite_level_fullSupport I eR eM hP)

/-- The ordinary completion datum produces a nonzero actual Hecke tensor fiber
and the prescribed action of every Hecke operator. -/
theorem ordinary_hecke_eigensystem (I : Ideal A)
    (eR : (A ⧸ I) ≃ₐ[A] R)
    (eM : (P ⧸ (I • ⊤ : Submodule A P)) ≃ₗ[A] H)
    (eT : R ≃ₐ[R] T) (hP : FullSupport A P) (x : R →+* E) :
    letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
    Nontrivial (E ⊗[T] H) ∧
      ∀ t : T, heckeOperator (H := H) (transportedPoint eT.toRingEquiv x) t =
        transportedPoint eT.toRingEquiv x t •
          (LinearMap.id : Module.End E (E ⊗[T] H)) := by
  let : Module.Finite R H := finite_level_finite (R := R) I eM
  let : Module.Finite T H := Module.Finite.of_restrictScalars_finite R T H
  apply support_gives_hecke_eigensystem eT x
  exact (fullSupport_iff_localizations R H).mp
    (finite_level_fullSupport I eR eM hP) _

/-- The tensor order displayed in the manuscript is nonzero as well. -/
theorem ordinary_right_hecke_fiber (I : Ideal A)
    (eR : (A ⧸ I) ≃ₐ[A] R)
    (eM : (P ⧸ (I • ⊤ : Submodule A P)) ≃ₗ[A] H)
    (eT : R ≃ₐ[R] T) (hP : FullSupport A P) (x : R →+* E) :
    letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
    Nontrivial (H ⊗[T] E) := by
  let : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
  exact (TensorProduct.comm T H E).nontrivial_congr.mpr
    (ordinary_hecke_eigensystem I eR eM eT hP x).1

/-- A genuine nonzero vector in the fiber carries all prescribed Hecke values. -/
theorem ordinary_eigenvector (I : Ideal A)
    (eR : (A ⧸ I) ≃ₐ[A] R)
    (eM : (P ⧸ (I • ⊤ : Submodule A P)) ≃ₗ[A] H)
    (eT : R ≃ₐ[R] T) (hP : FullSupport A P) (x : R →+* E) :
    letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
    ∃ z : E ⊗[T] H, z ≠ 0 ∧
      ∀ t : T, heckeOperator (H := H) (transportedPoint eT.toRingEquiv x) t z =
        transportedPoint eT.toRingEquiv x t • z := by
  let : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
  obtain ⟨hne, haction⟩ := ordinary_hecke_eigensystem I eR eM eT hP x
  let : Nontrivial (E ⊗[T] H) := hne
  obtain ⟨z, hz⟩ := exists_ne (0 : E ⊗[T] H)
  refine ⟨z, hz, fun t ↦ ?_⟩
  rw [haction t]
  rfl

end Support

section Realization

open Matrix RepresentationData DenseFrobenius GaloisRealization

variable {R T E H Γ Ω ι Auto : Type*} [CommRing R] [CommRing T]
    [Field E] [CharZero E] [TopologicalSpace E] [IsTopologicalRing E] [T2Space E]
    [Group Γ] [TopologicalSpace Γ] [Fintype ι] [DecidableEq ι]
    [Algebra R T] [AddCommGroup H] [Module R H] [Module T H]
    [IsScalarTower R T H]

/-- The declared classicality input produces an actual attached representation
at the supported point. `occurs x π` is the external arithmetic assertion that
the classical automorphic object `π` occurs in the Hecke fiber at `x`.
The input is conditional on nonvanishing; it contains no final isomorphism. -/
theorem supported_pointwise_realization [Module.Finite T H]
    (eT : R ≃ₐ[R] T) (x : R →+* E)
    (hxSupport : pointPrime x ∈ Module.support R H)
    (bn : BrauerNesbitt E Γ ι) (ρR : Γ →* GL ι R)
    (hx : Continuous (specialize ρR x)) (s : Semisimplification (specialize ρR x))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good)) (P : Ω → Polynomial T)
    (hρP : ∀ v, good v → (specialize ρR x (frob v)).val.charpoly =
      (P v).map (transportedPoint eT.toRingEquiv x))
    (occurs : (R →+* E) → Auto → Prop) (attached : Auto → Γ →ₜ* GL ι E)
    (classicality :
      letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
      Nontrivial (E ⊗[T] H) → ∃ π : Auto, occurs x π ∧
        Representation.IsSemisimpleRepresentation (representation (attached π).toMonoidHom) ∧
        ∀ v, good v → (attached π (frob v)).val.charpoly =
          (P v).map (transportedPoint eT.toRingEquiv x)) :
    letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
    Nontrivial (H ⊗[T] E) ∧ ∃ π : Auto, occurs x π ∧
      Isomorphic s.rep (attached π).toMonoidHom ∧
      (Representation.IsIrreducible (representation (specialize ρR x)) →
        Isomorphic (specialize ρR x) (attached π).toMonoidHom) := by
  let : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
  have hne := supported_hecke_fiber eT x hxSupport
  obtain ⟨π, hoccurs, hsemi, hpoly⟩ := classicality hne
  exact ⟨(TensorProduct.comm T H E).nontrivial_congr.mpr hne, π, hoccurs,
    universal_pointwise_realization bn ρR x hx s (attached π) hsemi frob good hdense
      (transportedPoint eT.toRingEquiv x) P hρP hpoly⟩

/-- Revised Corollary 9.5: full support supplies nonzero fibers throughout the
declared locus, and the pointwise arithmetic inputs give each attached witness.
Continuity and semisimplification are required only at points of that locus. -/
theorem full_support_pointwise_realization [Module.Finite T H]
    (eT : R ≃ₐ[R] T) (hH : FullSupport R H) (U : Set (PrimeSpectrum R))
    (bn : BrauerNesbitt E Γ ι) (ρR : Γ →* GL ι R)
    (hx : ∀ x : R →+* E, pointPrime x ∈ U → Continuous (specialize ρR x))
    (s : ∀ x : R →+* E, pointPrime x ∈ U → Semisimplification (specialize ρR x))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good)) (P : Ω → Polynomial T)
    (hρP : ∀ x : R →+* E, pointPrime x ∈ U → ∀ v, good v →
      (specialize ρR x (frob v)).val.charpoly =
        (P v).map (transportedPoint eT.toRingEquiv x))
    (occurs : (R →+* E) → Auto → Prop) (attached : Auto → Γ →ₜ* GL ι E)
    (classicality : ∀ x : R →+* E, pointPrime x ∈ U →
      letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
      Nontrivial (E ⊗[T] H) → ∃ π : Auto, occurs x π ∧
        Representation.IsSemisimpleRepresentation (representation (attached π).toMonoidHom) ∧
        ∀ v, good v → (attached π (frob v)).val.charpoly =
          (P v).map (transportedPoint eT.toRingEquiv x)) :
    ∀ (x : R →+* E) (hxU : pointPrime x ∈ U),
      letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
      Nontrivial (H ⊗[T] E) ∧ ∃ π : Auto, occurs x π ∧
        Isomorphic (s x hxU).rep (attached π).toMonoidHom ∧
        (Representation.IsIrreducible (representation (specialize ρR x)) →
          Isomorphic (specialize ρR x) (attached π).toMonoidHom) := by
  intro x hxU
  exact supported_pointwise_realization eT x
    ((fullSupport_iff_localizations R H).mp hH _) bn ρR (hx x hxU) (s x hxU)
    frob good hdense P (hρP x hxU) occurs attached (classicality x hxU)

variable {A Pinf : Type*} [CommRing A] [IsNoetherianRing A] [Algebra A R]
    [AddCommGroup Pinf] [Module A Pinf] [Module.Finite A Pinf]
    [Module A H] [IsScalarTower A R H]

/-- Revised Theorem 12.2, including its actual nonzero tensor fiber, the supplied
classical object's occurrence, semisimplified identification, and irreducible
identification. Finite-level support and finite generation are derived from
the printed patched quotient datum; classicality is used only after this. -/
theorem ordinary_conditional_completion (I : Ideal A)
    (eR : (A ⧸ I) ≃ₐ[A] R)
    (eM : (Pinf ⧸ (I • ⊤ : Submodule A Pinf)) ≃ₗ[A] H)
    (eT : R ≃ₐ[R] T) (hP : FullSupport A Pinf) (x : R →+* E)
    (bn : BrauerNesbitt E Γ ι) (ρR : Γ →* GL ι R)
    (hx : Continuous (specialize ρR x)) (s : Semisimplification (specialize ρR x))
    (frob : Ω → Γ) (good : Ω → Prop)
    (hdense : Dense (conjugacySaturation frob good)) (P : Ω → Polynomial T)
    (hρP : ∀ v, good v → (specialize ρR x (frob v)).val.charpoly =
      (P v).map (transportedPoint eT.toRingEquiv x))
    (occurs : (R →+* E) → Auto → Prop) (attached : Auto → Γ →ₜ* GL ι E)
    (classicality :
      letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
      Nontrivial (E ⊗[T] H) → ∃ π : Auto, occurs x π ∧
        Representation.IsSemisimpleRepresentation (representation (attached π).toMonoidHom) ∧
        ∀ v, good v → (attached π (frob v)).val.charpoly =
          (P v).map (transportedPoint eT.toRingEquiv x)) :
    letI : Algebra T E := (transportedPoint eT.toRingEquiv x).toAlgebra
    Nontrivial (H ⊗[T] E) ∧ ∃ π : Auto, occurs x π ∧
      Isomorphic s.rep (attached π).toMonoidHom ∧
      (Representation.IsIrreducible (representation (specialize ρR x)) →
        Isomorphic (specialize ρR x) (attached π).toMonoidHom) := by
  let : Module.Finite R H := finite_level_finite (R := R) I eM
  let : Module.Finite T H := Module.Finite.of_restrictScalars_finite R T H
  exact supported_pointwise_realization eT x
    ((fullSupport_iff_localizations R H).mp (finite_level_fullSupport I eR eM hP) _)
    bn ρR hx s frob good hdense P hρP occurs attached classicality

end Realization

end PaperXII.OrdinaryCompletion
