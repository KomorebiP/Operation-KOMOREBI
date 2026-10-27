import PaperXII.ComplexFieldFibers
import PaperXII.FieldFibers
import Mathlib.RingTheory.Spectrum.Prime.RingHom

/-!
# Residue-field support of scalar-extended cochain models

The fibers are objects in Mathlib's actual derived category. For bounded
projective models the construction is derived scalar extension, with model
independence established separately in `PerfectDerivedSupport`.
-/

noncomputable section

open CategoryTheory CategoryTheory.Limits

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.ComplexSupport

open ComplexBaseChange ComplexFieldFibers FieldFibers

variable {R S T : Type u} [CommRing R] [CommRing S] [CommRing T]

/-- The actual derived-category object of the specialized cochain model. -/
def fiber (f : R →+* S) (C : CochainComplex (ModuleCat.{u} R) ℤ) :
    DerivedCategory (ModuleCat.{u} S) := DerivedCategory.Q.obj (baseChange f C)

/-- Fiber composition is induced by the actual cochain tensor associator. -/
def fiberCompIso (f : R →+* S) (g : S →+* T)
    (C : CochainComplex (ModuleCat.{u} R) ℤ) :
    fiber g (baseChange f C) ≅ fiber (g.comp f) C :=
  DerivedCategory.Q.mapIso (baseChangeCompIso f g C)

/-- Nonvanishing of the actual residue-field specialization. -/
def support (C : CochainComplex (ModuleCat.{u} R) ℤ) : Set (PrimeSpectrum R) :=
  {p | ¬IsZero (fiber (algebraMap R p.asIdeal.ResidueField) C)}

/-- The support fills the spectrum of the coefficient ring. -/
def FullSupport (C : CochainComplex (ModuleCat.{u} R) ℤ) : Prop := support C = Set.univ

/-- Every field-valued point detects precisely the residue-field support at its kernel. -/
theorem nonzero_fiber_iff_support {K : Type u} [Field K] (x : R →+* K)
    (C : CochainComplex (ModuleCat.{u} R) ℤ) :
    ¬IsZero (fiber x C) ↔ pointPrime x ∈ support C := by
  let p := pointPrime x
  let h := residueFieldLift x
  have e := fiberCompIso (algebraMap R p.asIdeal.ResidueField) h C
  have hx : h.comp (algebraMap R p.asIdeal.ResidueField) = x := residueFieldLift_comp x
  rw [hx] at e
  change ¬IsZero (fiber x C) ↔ ¬IsZero (fiber (algebraMap R p.asIdeal.ResidueField) C)
  exact not_congr (e.isZero_iff.symm.trans
    (isZero_baseChange_iff h (baseChange (algebraMap R p.asIdeal.ResidueField) C)))

/-- The kernel of the residue-field point after a scalar map is the actual inverse-image prime. -/
theorem pointPrime_residue_comp (f : R →+* S) (q : PrimeSpectrum S) :
    pointPrime ((algebraMap S q.asIdeal.ResidueField).comp f) = PrimeSpectrum.comap f q := by
  ext r
  change algebraMap S q.asIdeal.ResidueField (f r) = 0 ↔ f r ∈ q.asIdeal
  exact Ideal.algebraMap_residueField_eq_zero

/-- Support under arbitrary scalar extension, on actual corresponding primes. -/
theorem mem_support_baseChange_iff (f : R →+* S)
    (C : CochainComplex (ModuleCat.{u} R) ℤ) (q : PrimeSpectrum S) :
    q ∈ support (baseChange f C) ↔ PrimeSpectrum.comap f q ∈ support C := by
  change ¬IsZero (fiber (algebraMap S q.asIdeal.ResidueField) (baseChange f C)) ↔ _
  rw [(fiberCompIso f (algebraMap S q.asIdeal.ResidueField) C).isZero_iff]
  rw [nonzero_fiber_iff_support, pointPrime_residue_comp]

/-- Set form of the scalar-extension support identity. -/
theorem support_baseChange (f : R →+* S)
    (C : CochainComplex (ModuleCat.{u} R) ℤ) :
    support (baseChange f C) = PrimeSpectrum.comap f ⁻¹' support C := by
  ext q
  exact mem_support_baseChange_iff f C q

/-- The ambient-spectrum equality for the actual ideal quotient. -/
theorem image_support_quotient (I : Ideal R)
    (C : CochainComplex (ModuleCat.{u} R) ℤ) :
    PrimeSpectrum.comap (Ideal.Quotient.mk I) '' support (baseChange (Ideal.Quotient.mk I) C) =
      support C ∩ PrimeSpectrum.zeroLocus I := by
  rw [support_baseChange, Set.image_preimage_eq_inter_range,
    range_comap_of_surjective (R ⧸ I) (Ideal.Quotient.mk I)
      Ideal.Quotient.mk_surjective, Ideal.mk_ker]

/-- Full support survives arbitrary scalar extension. -/
theorem fullSupport_baseChange (f : R →+* S)
    (C : CochainComplex (ModuleCat.{u} R) ℤ) (h : FullSupport C) :
    FullSupport (baseChange f C) := by
  unfold FullSupport at h ⊢
  rw [support_baseChange, h, Set.preimage_univ]

/-- Every field specialization of a full-support model is nonzero in the derived category. -/
theorem nonzero_fiber_of_fullSupport {K : Type u} [Field K] (x : R →+* K)
    (C : CochainComplex (ModuleCat.{u} R) ℤ) (h : FullSupport C) :
    ¬IsZero (fiber x C) := by
  apply (nonzero_fiber_iff_support x C).mpr
  rw [show support C = Set.univ from h]
  trivial

end PaperXII.ComplexSupport
