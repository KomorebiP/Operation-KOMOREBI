import PaperXII.DerivedHeckeAction
import PaperXII.PerfectCohomology
import PaperXII.BaseChangeSupport

/-!
# Ordinary and derived Hecke carriers

The two carriers are an actual finite module and an actual perfect derived
object. Their fibers and operators are the tensor module and the specialized
derived cohomology, with operators induced by the original multiplication.
Support comparisons are literal inclusions of subsets of prime spectra.
-/

noncomputable section

open CategoryTheory CategoryTheory.Limits
open scoped TensorProduct

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.HeckeCarriers

/-- An ordinary carrier is an actual finite module. -/
structure FiniteModule (R : Type u) [CommRing R] where
  object : ModuleCat.{u} R
  finite : Module.Finite R object

attribute [instance] FiniteModule.finite

/-- The ordinary and perfect derived alternatives retain their actual objects. -/
def Carrier (R : Type u) [CommRing R] :=
  FiniteModule R ⊕ PerfectDerivedSupport.PerfectComplex R

variable {R S T E : Type u} [CommRing R] [CommRing S] [CommRing T] [Field E]

/-- Ordinary fibers have one degree; derived fibers have integer degrees. -/
def Carrier.Degree : Carrier R → Type
  | .inl _ => PUnit
  | .inr _ => ℤ

/-- The actual support of the underlying ordinary or perfect derived object. -/
def support : Carrier R → Set (PrimeSpectrum R)
  | .inl M => Module.support R M.object
  | .inr C => PerfectDerivedSupport.support C

/-- Full support is equality with the entire prime spectrum. -/
def FullSupport (C : Carrier R) : Prop := support C = Set.univ

/-- Ordinary tensor fibers and actual derived cohomology of specialized objects. -/
def fiberSpace (C : Carrier R) (y : R →+* E) : C.Degree → ModuleCat.{u} E :=
  match C with
  | .inl M => fun _ => (ModuleCat.extendScalars y).obj M.object
  | .inr P => fun n => PerfectCohomology.cohomology (P.baseChange y) n

/-- Literal nonvanishing of the tensor module or the specialized derived object. -/
def FiberNonzero (C : Carrier R) (y : R →+* E) : Prop :=
  match C with
  | .inl M => ¬IsZero ((ModuleCat.extendScalars y).obj M.object)
  | .inr P => ¬IsZero (P.baseChange y).object

/-- The operator is induced from multiplication on the original module or complex. -/
def heckeOperator (C : Carrier R) (y : R →+* E) :
    (n : C.Degree) → R → (fiberSpace C y n ⟶ fiberSpace C y n) :=
  match C with
  | .inl M => fun _ r => (ModuleCat.extendScalars y).map (r • 𝟙 M.object)
  | .inr P => fun n r => DerivedHeckeAction.perfectCohomologyOperator P y n r

/-- Both actual constructions satisfy the tensor scalar identity. -/
theorem heckeOperator_eq_scalar (C : Carrier R) (y : R →+* E)
    (n : C.Degree) (r : R) :
    heckeOperator C y n r = y r • 𝟙 (fiberSpace C y n) := by
  cases C with
  | inl M => exact DerivedHeckeAction.extendScalars_smul_id y M.object r
  | inr P => exact DerivedHeckeAction.perfectCohomologyOperator_eq_scalar P y n r

/-- The tensor scalar identity on each actual vector. -/
theorem heckeOperator_apply (C : Carrier R) (y : R →+* E)
    (n : C.Degree) (r : R) (z : fiberSpace C y n) :
    heckeOperator C y n r z = y r • z := by
  rw [heckeOperator_eq_scalar]
  rfl

/-- A common eigenvector is a nonzero vector with all prescribed eigenvalues. -/
def IsEigenvector (C : Carrier R) (y : R →+* E) (n : C.Degree)
    (z : fiberSpace C y n) : Prop :=
  z ≠ 0 ∧ ∀ r : R, heckeOperator C y n r z = y r • z

/-- Every nonzero vector has the eigenvalues of the specialized point. -/
theorem isEigenvector_of_ne_zero (C : Carrier R) (y : R →+* E)
    (n : C.Degree) (z : fiberSpace C y n) (hz : z ≠ 0) :
    IsEigenvector C y n z :=
  ⟨hz, fun r => heckeOperator_apply C y n r z⟩

/-- The actual bounded model interval, with the sole ordinary degree allowed. -/
def DegreeRange (C : Carrier R) : C.Degree → Prop :=
  match C with
  | .inl _ => fun _ => True
  | .inr P => fun (n : ℤ) => P.model.lower ≤ n ∧ n ≤ P.model.upper

/-- A supported point supplies a nonzero actual eigensystem in the model range. -/
theorem supported_point_eigensystem_in_range (C : Carrier R) (y : R →+* E)
    (hy : FieldFibers.pointPrime y ∈ support C) :
    ∃ n : C.Degree, DegreeRange C n ∧
      ∃ z : fiberSpace C y n, IsEigenvector C y n z := by
  cases C with
  | inl M =>
    let : Algebra R E := y.toAlgebra
    have : Nontrivial (E ⊗[R] M.object) :=
      (FieldFibers.nontrivial_fiber_iff_support (M := M.object) y).mpr hy
    obtain ⟨z, hz⟩ := exists_ne (0 : E ⊗[R] M.object)
    exact ⟨PUnit.unit, trivial, z, isEigenvector_of_ne_zero (.inl M) y _ z hz⟩
  | inr P =>
    have hP := (PerfectDerivedSupport.nonzero_fiber_iff_support P y).mpr hy
    obtain ⟨n, hlo, hhi, z, hz⟩ :=
      PerfectCohomology.exists_nonzero_vector_in_range P y hP
    exact ⟨n, ⟨hlo, hhi⟩, z, isEigenvector_of_ne_zero (.inr P) y n z hz⟩

/-- A supported point supplies an actual nonzero eigenvector. -/
theorem supported_point_eigensystem (C : Carrier R) (y : R →+* E)
    (hy : FieldFibers.pointPrime y ∈ support C) :
    ∃ n : C.Degree, ∃ z : fiberSpace C y n, IsEigenvector C y n z := by
  obtain ⟨n, _, z, hz⟩ := supported_point_eigensystem_in_range C y hy
  exact ⟨n, z, hz⟩

/-- Support implies literal nonvanishing of the actual ordinary or derived fiber. -/
theorem supported_point_fiber_nonzero (C : Carrier R) (y : R →+* E)
    (hy : FieldFibers.pointPrime y ∈ support C) : FiberNonzero C y := by
  cases C with
  | inl M =>
    obtain ⟨n, z, hz⟩ := supported_point_eigensystem (.inl M) y hy
    intro hzero
    have hsub : Subsingleton ((ModuleCat.extendScalars y).obj M.object) :=
      ModuleCat.isZero_iff_subsingleton.mp hzero
    exact hz.1 (hsub.elim z 0)
  | inr P => exact (PerfectDerivedSupport.nonzero_fiber_iff_support P y).mpr hy

/-- Full support provides an eigensystem at every field-valued point. -/
theorem fullSupport_eigensystem_in_range (C : Carrier R) (y : R →+* E)
    (hC : FullSupport C) :
    ∃ n : C.Degree, DegreeRange C n ∧
      ∃ z : fiberSpace C y n, IsEigenvector C y n z := by
  apply supported_point_eigensystem_in_range C y
  rw [hC]
  trivial

/-- The comparison hypothesis is the actual inverse-image support inclusion. -/
def SupportComparison (f : R →+* T) (M : Carrier R) (H : Carrier T) : Prop :=
  PrimeSpectrum.comap f ⁻¹' support M ⊆ support H

/-- Pullback of the prime kernel agrees with composition of field-valued points. -/
theorem pointPrime_comp (f : R →+* T) (y : T →+* E) :
    PrimeSpectrum.comap f (FieldFibers.pointPrime y) =
      FieldFibers.pointPrime (y.comp f) := by
  ext r
  rfl

/-- A compatible point inherits support through the literal support comparison. -/
theorem supportComparison_pointwise (f : R →+* T) (M : Carrier R) (H : Carrier T)
    (comparison : SupportComparison f M H) (x : R →+* E) (y : T →+* E)
    (hcomp : y.comp f = x) (hx : FieldFibers.pointPrime x ∈ support M) :
    FieldFibers.pointPrime y ∈ support H := by
  apply comparison
  change PrimeSpectrum.comap f (FieldFibers.pointPrime y) ∈ support M
  rw [pointPrime_comp, hcomp]
  exact hx

/-- The actual support inclusion transports literal fiber nonvanishing. -/
theorem supportComparison_pointwise_fiber_nonzero
    (f : R →+* T) (M : Carrier R) (H : Carrier T)
    (comparison : SupportComparison f M H) (x : R →+* E) (y : T →+* E)
    (hcomp : y.comp f = x) (hx : FieldFibers.pointPrime x ∈ support M) :
    FiberNonzero H y :=
  supported_point_fiber_nonzero H y
    (supportComparison_pointwise f M H comparison x y hcomp hx)

/-- Full support transports through the actual comparison. -/
theorem supportComparison_fullSupport (f : R →+* T) (M : Carrier R) (H : Carrier T)
    (comparison : SupportComparison f M H) (hM : FullSupport M) : FullSupport H := by
  apply Set.eq_univ_of_forall
  intro q
  apply comparison
  change PrimeSpectrum.comap f q ∈ support M
  rw [hM]
  trivial

/-- The comparison gives a nonzero actual Hecke eigenvector at every compatible point. -/
theorem supportComparison_pointwise_eigensystem
    (f : R →+* T) (M : Carrier R) (H : Carrier T)
    (comparison : SupportComparison f M H) (x : R →+* E) (y : T →+* E)
    (hcomp : y.comp f = x) (hx : FieldFibers.pointPrime x ∈ support M) :
    ∃ n : H.Degree, DegreeRange H n ∧
      ∃ z : fiberSpace H y n, IsEigenvector H y n z :=
  supported_point_eigensystem_in_range H y
    (supportComparison_pointwise f M H comparison x y hcomp hx)

/-- Actual scalar extension of a finite ordinary module. -/
def FiniteModule.baseChange (M : FiniteModule R) (f : R →+* S) : FiniteModule S :=
  ⟨(ModuleCat.extendScalars f).obj M.object,
    PerfectModels.finite_extendScalars f M.object⟩

/-- Actual ordinary or derived scalar extension, preserving the carrier kind. -/
def Carrier.baseChange (C : Carrier R) (f : R →+* S) : Carrier S :=
  match C with
  | .inl M => .inl (M.baseChange f)
  | .inr P => .inr (P.baseChange f)

/-- Both actual scalar extensions have exactly the spectral inverse-image support. -/
theorem support_baseChange (C : Carrier R) (f : R →+* S) :
    support (C.baseChange f) = PrimeSpectrum.comap f ⁻¹' support C := by
  cases C with
  | inl M =>
    let : Algebra R S := f.toAlgebra
    exact BaseChangeSupport.support_baseChange (R := R) (S := S) (M := M.object)
  | inr P => exact PerfectDerivedSupport.support_baseChange P f

/-- Actual scalar extension constructs the required support comparison. -/
theorem supportComparison_baseChange (C : Carrier R) (f : R →+* S) :
    SupportComparison f C (C.baseChange f) := by
  unfold SupportComparison
  rw [support_baseChange]

/-- Full support is preserved by either actual scalar extension. -/
theorem fullSupport_baseChange (C : Carrier R) (f : R →+* S) (hC : FullSupport C) :
    FullSupport (C.baseChange f) :=
  supportComparison_fullSupport f C (C.baseChange f) (supportComparison_baseChange C f) hC

/-- Ring identification transports the actual support by its induced spectrum map. -/
theorem support_ringEquiv (C : Carrier R) (e : R ≃+* S) :
    PrimeSpectrum.comap e.toRingHom '' support (C.baseChange e.toRingHom) = support C := by
  rw [support_baseChange, Set.image_preimage_eq_inter_range]
  have hsurj : Function.Surjective (PrimeSpectrum.comap e.toRingHom) :=
    (PrimeSpectrum.isHomeomorph_comap_of_bijective e.bijective).surjective
  rw [Set.range_eq_univ.mpr hsurj, Set.inter_univ]

end PaperXII.HeckeCarriers
