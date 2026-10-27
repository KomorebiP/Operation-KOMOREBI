import PaperXII.PerfectDerivedSupport
import Mathlib.RingTheory.Noetherian.Basic

/-!
# Derived patching support and surviving cohomology

The input is exactly an ideal quotient ring identification and an actual
isomorphism in the derived category. No pointwise fiber identification,
nonvanishing conclusion, or cohomology comparison is assumed.
-/

noncomputable section

open CategoryTheory CategoryTheory.Limits

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.DerivedPatching

open PerfectDerivedSupport

variable {A R : Type u} [CommRing A] [CommRing R]

/-- The actual coefficient specialization determined by the quotient identification. -/
def quotientScalar (I : Ideal A) (e : (A ⧸ I) ≃+* R) : A →+* R :=
  e.toRingHom.comp (Ideal.Quotient.mk I)

/-- The specialization is surjective. -/
theorem quotientScalar_surjective (I : Ideal A) (e : (A ⧸ I) ≃+* R) :
    Function.Surjective (quotientScalar I e) :=
  e.surjective.comp Ideal.Quotient.mk_surjective

/-- Its kernel is the declared patching ideal, not an additional condition. -/
theorem quotientScalar_ker (I : Ideal A) (e : (A ⧸ I) ≃+* R) :
    RingHom.ker (quotientScalar I e) = I := by
  ext a
  change e (Ideal.Quotient.mk I a) = 0 ↔ a ∈ I
  rw [map_eq_zero_iff e e.injective, Ideal.Quotient.eq_zero_iff_mem]

/-- Original Definition 6.17, with an arbitrary finite-level derived object. -/
structure Datum (A R : Type u) [CommRing A] [CommRing R] where
  noetherian : IsNoetherianRing A
  ideal : Ideal A
  coefficient : (A ⧸ ideal) ≃+* R
  patched : PerfectComplex A
  finiteLevel : DerivedCategory (ModuleCat.{u} R)
  comparison : finiteLevel ≅ (patched.baseChange (quotientScalar ideal coefficient)).object

/-- The finite-level perfect model is constructed from the supplied derived identification. -/
def Datum.finitePerfect (D : Datum A R) : PerfectComplex R where
  object := D.finiteLevel
  model := D.patched.model.baseChange (quotientScalar D.ideal D.coefficient)
  modelIso := D.comparison.symm

/-- The constructed perfect object has the literal finite-level derived object. -/
theorem finitePerfect_object (D : Datum A R) : D.finitePerfect.object = D.finiteLevel := rfl

/-- Full patched support descends using the actual derived comparison. -/
theorem fullSupport_descends (D : Datum A R) (h : FullSupport D.patched) :
    FullSupport D.finitePerfect := by
  unfold FullSupport
  rw [support_eq_of_iso D.comparison]
  exact fullSupport_baseChange D.patched (quotientScalar D.ideal D.coefficient) h

/-- Every field-valued finite-level fiber is nonzero in the actual derived category. -/
theorem derived_fiber_nonzero {K : Type u} [Field K] (D : Datum A R)
    (h : FullSupport D.patched) (x : R →+* K) :
    ¬IsZero (D.finitePerfect.baseChange x).object :=
  nonzero_fiber_of_fullSupport D.finitePerfect x (fullSupport_descends D h)

/-- Original Theorem 6.18: full finite-level support and all nonzero field fibers. -/
theorem derived_support_descent (D : Datum A R) (h : FullSupport D.patched) :
    FullSupport D.finitePerfect ∧
      ∀ (K : Type u) [Field K] (x : R →+* K), ¬IsZero (D.finitePerfect.baseChange x).object := by
  exact ⟨fullSupport_descends D h, fun _ _ x => derived_fiber_nonzero D h x⟩

/-- Original Corollary 6.19, using Mathlib's actual derived cohomology functor. -/
theorem derived_degree_survives {K : Type u} [Field K] (D : Datum A R)
    (h : FullSupport D.patched) (x : R →+* K) :
    ∃ n : ℤ, ¬IsZero ((DerivedCategory.homologyFunctor (ModuleCat K) n).obj
      (D.finitePerfect.baseChange x).object) :=
  exists_nonzero_cohomology D.finitePerfect x (derived_fiber_nonzero D h x)

/-- The surviving cohomology can also be read in the actual specialized projective model. -/
theorem model_degree_survives {K : Type u} [Field K] (D : Datum A R)
    (h : FullSupport D.patched) (x : R →+* K) :
    ∃ n : ℤ, ¬IsZero ((D.finitePerfect.baseChange x).model.complex.homology n) :=
  exists_nonzero_model_cohomology D.finitePerfect x (derived_fiber_nonzero D h x)

end PaperXII.DerivedPatching
