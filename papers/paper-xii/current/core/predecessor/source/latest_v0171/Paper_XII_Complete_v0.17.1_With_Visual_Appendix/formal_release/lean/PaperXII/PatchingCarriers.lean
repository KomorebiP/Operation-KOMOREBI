import PaperXII.HeckeCarriers
import PaperXII.OrdinaryCompletion
import PaperXII.DerivedPatching

/-!
# Actual ordinary and derived patched carriers

The ordinary branch retains the coefficient quotient and module control
isomorphism. The derived branch retains an actual isomorphism in the derived
category. Full support is assumed only for the patched object and is proved
for the finite-level carrier.
-/

set_option autoImplicit false

noncomputable section

open CategoryTheory

universe u

attribute [local instance] HasDerivedCategory.standard

namespace PaperXII.PatchingCarriers

open HeckeCarriers

variable {A R T : Type u} [CommRing A] [CommRing R] [CommRing T]

/-- The ordinary patching input uses the actual coefficient quotient and
the actual module quotient. Finite generation at finite level is not assumed. -/
structure OrdinaryDatum (A R : Type u) [CommRing A] [CommRing R] [Algebra A R] where
  noetherian : IsNoetherianRing A
  ideal : Ideal A
  coefficient : (A ⧸ ideal) ≃ₐ[A] R
  patched : FiniteModule A
  finiteLevel : ModuleCat.{u} R
  comparison : (patched.object ⧸ (ideal • ⊤ : Submodule A patched.object)) ≃ₗ[A]
    (ModuleCat.restrictScalars (algebraMap A R)).obj finiteLevel
  patchedSupport : ModuleSupport.FullSupport A patched.object

variable [Algebra A R]

/-- The finite-level object with its specified coefficient action restricted to A. -/
abbrev OrdinaryDatum.restricted (D : OrdinaryDatum A R) : ModuleCat.{u} A :=
  (ModuleCat.restrictScalars (algebraMap A R)).obj D.finiteLevel

/-- This scalar tower is induced by the actual coefficient algebra map. -/
instance OrdinaryDatum.restricted_scalarTower (D : OrdinaryDatum A R) :
    IsScalarTower A R D.restricted where
  smul_assoc a r m := by
    change (a • r) • m = algebraMap A R a • (r • m)
    rw [Algebra.smul_def, mul_smul]

/-- Finite generation is descended through the supplied module control map. -/
theorem OrdinaryDatum.finite_level_finite (D : OrdinaryDatum A R) :
    Module.Finite R D.finiteLevel := by
  change Module.Finite R D.restricted
  exact OrdinaryCompletion.finite_level_finite (R := R) (H := D.restricted)
    D.ideal D.comparison

/-- The finite-level ordinary carrier has the literal supplied module. -/
def OrdinaryDatum.finiteModule (D : OrdinaryDatum A R) : FiniteModule R where
  object := D.finiteLevel
  finite := D.finite_level_finite

/-- Quotient support descent proves finite-level full support. -/
theorem OrdinaryDatum.fullSupport (D : OrdinaryDatum A R) :
    FullSupport (.inl D.finiteModule) := by
  let : IsNoetherianRing A := D.noetherian
  change ModuleSupport.FullSupport R D.restricted
  exact OrdinaryCompletion.finite_level_fullSupport (H := D.restricted)
    D.ideal D.coefficient D.comparison D.patchedSupport

/-- The derived patching input retains the actual derived comparison and full
support of the patched complex. -/
structure DerivedDatum (A R : Type u) [CommRing A] [CommRing R] where
  datum : DerivedPatching.Datum A R
  patchedSupport : PerfectDerivedSupport.FullSupport datum.patched

omit [Algebra A R] in
/-- Derived quotient support descent proves finite-level full support. -/
theorem DerivedDatum.fullSupport (D : DerivedDatum A R) :
    FullSupport (.inr D.datum.finitePerfect) :=
  DerivedPatching.fullSupport_descends D.datum D.patchedSupport

/-- A patched carrier consists of one of the two actual patching constructions. -/
def PatchedCarrier (A R : Type u) [CommRing A] [CommRing R] [Algebra A R] :=
  OrdinaryDatum A R ⊕ DerivedDatum A R

/-- Recover the finite-level ordinary or perfect derived carrier. -/
def PatchedCarrier.finiteCarrier : PatchedCarrier A R → Carrier R
  | .inl D => .inl D.finiteModule
  | .inr D => .inr D.datum.finitePerfect

/-- Both branches derive the same precise finite-level support conclusion. -/
theorem PatchedCarrier.fullSupport (D : PatchedCarrier A R) :
    FullSupport D.finiteCarrier := by
  cases D with
  | inl D => exact D.fullSupport
  | inr D => exact D.fullSupport

/-- An actual support comparison carries the descended support to a Hecke carrier. -/
theorem PatchedCarrier.comparison_fullSupport (D : PatchedCarrier A R)
    (f : R →+* T) (H : Carrier T)
    (comparison : SupportComparison f D.finiteCarrier H) : FullSupport H :=
  supportComparison_fullSupport f D.finiteCarrier H comparison D.fullSupport

end PaperXII.PatchingCarriers
