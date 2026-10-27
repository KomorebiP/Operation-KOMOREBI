import FirstOrderLiftGaugeClassification
import PresentedRepresentationTangentH1
import PresentedFixedRestrictionH1
import SelmerPresentationComparison

/-!
# Representation-deformation resolution capstone

This module records the reconciled first-order architecture:

* actual square-zero representation lifts are adjoint cocycles;
* strict-equivalence fibres are adjoint `H¹` classes;
* a correctly differentiated presented algebra has the same dual-number tangent;
* fixing a subgroup restriction replaces the tangent by cocycles vanishing on
  that subgroup and the gauge group by its centralizer;
* presentation-dependent obstruction kernels map onto intrinsic cotangent `H₁`
  with exactly the relation-syzygy kernel.

The arithmetic comparison between cotangent `H₁` and global dual Selmer remains
an explicit input.
-/

namespace Komorebi.StrongArtin.RepresentationDeformationResolutionCapstone

open Representation
open groupCohomology
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PresentedAlgebraTangentEquiv
open Komorebi.StrongArtin.RepresentationTangentCocycles
open Komorebi.StrongArtin.FirstOrderRepresentationLifts
open Komorebi.StrongArtin.FirstOrderLiftGaugeClassification
open Komorebi.StrongArtin.PresentedRepresentationTangentH1
open Komorebi.StrongArtin.PresentedFixedRestrictionH1

noncomputable section

universe u

variable {k G V ι κ : Type u} [CommRing k] [Group G]
  [AddCommGroup V] [Module k V]

/-- Actual first-order representation lifts are exactly adjoint cocycles. -/
def firstOrderLiftEquivCocycles (rho : Representation k G V) :
    FirstOrderLift rho ≃ cocycles₁ (AdRep rho) :=
  (tangentEquivFirstOrderLift rho).symm.trans
    (tangentEquivCocycles rho).toEquiv

/-- Under a correct first-jet presentation, dual-number algebra points are
actual square-zero representation lifts. -/
def PresentedDatum.dualPointEquivFirstOrderLift
    {system : System ι κ k} {x : ι → k}
    {rho : Representation k G V}
    (D : PresentedRepresentationTangentH1.Datum system x rho)
    (hx : evalSystem system x = 0) :
    DualPointOver system x ≃ FirstOrderLift rho :=
  (D.representationTangentEquivDualPoint hx).symm.trans
    (tangentEquivFirstOrderLift rho)

/-- The complete first-order classification statement for actual square-zero
lifts: every adjoint `H¹` class is represented and equality of classes is
exactly gauge equivalence. -/
theorem actual_firstOrder_lifts_classified_by_H1
    (rho : Representation k G V) :
    Function.Surjective (h1ClassOfLift rho) ∧
      ∀ L₁ L₂ : FirstOrderLift rho,
        h1ClassOfLift rho L₁ = h1ClassOfLift rho L₂ ↔
          GaugeEquivalent rho L₁ L₂ :=
  firstOrderLift_classification rho

/-- A correctly differentiated fixed-restriction presentation has an exact
sequence from pulled-back centralizer gauge directions to the presented tangent
and then onto the relative image in global adjoint `H¹`. -/
theorem presented_fixedRestriction_exact
    {system : System ι κ k} {x : ι → k}
    {rho : Representation k G V} {H : Subgroup G}
    (D : PresentedFixedRestrictionH1.Datum system x rho H) :
    Function.Exact
      (Submodule.subtype (D.presentedFixedGaugeDirections))
      D.presentedTangentToRelativeH1Image :=
  D.presentedFixedGauge_exact_relativeH1

end

end Komorebi.StrongArtin.RepresentationDeformationResolutionCapstone

#print axioms Komorebi.StrongArtin.RepresentationDeformationResolutionCapstone.actual_firstOrder_lifts_classified_by_H1
#print axioms Komorebi.StrongArtin.RepresentationDeformationResolutionCapstone.presented_fixedRestriction_exact
