import PresentedAlgebraTangentEquiv
import FixedRestrictionRelativeH1

/-!
# Presented fixed-restriction deformation tangents

An explicit first-jet identification of a polynomial presentation with the
fixed-restriction representation equations transports the presented tangent
fibre to cocycles vanishing on the fixed subgroup.  The kernel of the induced
map to global adjoint `H¹` is exactly the centralizer-gauge subspace.
-/

namespace Komorebi.StrongArtin.PresentedFixedRestrictionH1

open Representation
open groupCohomology
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PresentedAlgebraTangentEquiv
open Komorebi.StrongArtin.RepresentationTangentCocycles
open Komorebi.StrongArtin.FixedRestrictionTangent
open Komorebi.StrongArtin.FixedRestrictionRelativeH1

noncomputable section

universe u

variable {k G V ι κ : Type u} [CommRing k] [Group G]
  [AddCommGroup V] [Module k V]

/-- First-jet datum recognizing a finite presentation as the framed
fixed-restriction representation deformation problem. -/
structure Datum
    (system : System ι κ k) (x : ι → k)
    (rho : Representation k G V) (H : Subgroup G) where
  tangentEquiv :
    TangentSpace system x ≃ₗ[k] fixedRestrictionTangents rho H

namespace Datum

variable {system : System ι κ k} {x : ι → k}
  {rho : Representation k G V} {H : Subgroup G}
  (D : Datum system x rho H)

/-- The presented fixed-restriction tangent is the space of adjoint cocycles
vanishing on `H`. -/
def presentedTangentEquivRestrictionZeroCocycles :
    TangentSpace system x ≃ₗ[k] restrictionZeroCocycles rho H :=
  D.tangentEquiv.trans (fixedRestrictionTangentEquivCocycles rho H)

/-- Canonical map from the presented tangent to the intrinsic relative `H¹`
image. -/
def presentedTangentToRelativeH1Image :
    TangentSpace system x →ₗ[k] RelativeH1Image rho H :=
  (fixedRestrictionTangentToRelativeH1Image rho H).comp
    D.tangentEquiv.toLinearMap

/-- The centralizer gauge directions pulled back into presentation coordinates. -/
def presentedFixedGaugeDirections :
    Submodule k (TangentSpace system x) :=
  (fixedRestrictionGaugeRange rho H).comap D.tangentEquiv.toLinearMap

/-- Every relative cohomology-image class is represented by a presented
fixed-restriction tangent. -/
theorem presentedTangentToRelativeH1Image_surjective :
    Function.Surjective (presentedTangentToRelativeH1Image D) :=
  (fixedRestrictionTangentToRelativeH1Image_surjective rho H).comp
    D.tangentEquiv.surjective

/-- The kernel is exactly the pulled-back centralizer-gauge subspace. -/
theorem ker_presentedTangentToRelativeH1Image :
    LinearMap.ker (presentedTangentToRelativeH1Image D) =
      presentedFixedGaugeDirections D := by
  rw [presentedTangentToRelativeH1Image, LinearMap.ker_comp]
  rw [ker_fixedRestrictionTangentToRelativeH1Image rho H]
  rfl

/-- Exactness of the presented fixed-restriction deformation sequence. -/
theorem presentedFixedGauge_exact_relativeH1 :
    Function.Exact
      (Submodule.subtype (presentedFixedGaugeDirections D))
      (presentedTangentToRelativeH1Image D) := by
  rw [LinearMap.exact_iff]
  rw [Submodule.range_subtype]
  exact ker_presentedTangentToRelativeH1Image D

/-- At a genuine base solution, dual-number points of the presented algebra are
exactly framed fixed-restriction representation tangents. -/
def fixedRestrictionTangentEquivDualPoint
    (hx : evalSystem system x = 0) :
    fixedRestrictionTangents rho H ≃ DualPointOver system x :=
  D.tangentEquiv.symm.toEquiv.trans
    (tangentEquivDualPoint system x hx)

/-- Equivalently, dual-number points are exactly adjoint cocycles vanishing on
`H`. -/
def restrictionZeroCocyclesEquivDualPoint
    (hx : evalSystem system x = 0) :
    restrictionZeroCocycles rho H ≃ DualPointOver system x :=
  (fixedRestrictionTangentEquivCocycles rho H).symm.toEquiv.trans
    (fixedRestrictionTangentEquivDualPoint D hx)

end Datum

end

end Komorebi.StrongArtin.PresentedFixedRestrictionH1

#print axioms Komorebi.StrongArtin.PresentedFixedRestrictionH1.Datum.presentedFixedGauge_exact_relativeH1
#print axioms Komorebi.StrongArtin.PresentedFixedRestrictionH1.Datum.restrictionZeroCocyclesEquivDualPoint
