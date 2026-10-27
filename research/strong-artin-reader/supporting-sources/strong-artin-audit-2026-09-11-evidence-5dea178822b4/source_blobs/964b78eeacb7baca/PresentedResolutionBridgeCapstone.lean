import AugmentationQuotientEquiv
import AugmentedPresentedPointCapstone
import PresentedAlgebraTangentEquiv

/-!
# Presented-resolution bridge capstones

This module records the three exact algebraic interfaces established in this
checkpoint: augmentation by genuine auxiliary variables, promotion of a
nonlinear coordinate solution to an algebra point, and identification of the
presentation tangent fibre with the coordinate Jacobian kernel.
-/

namespace Komorebi.StrongArtin.PresentedResolutionBridgeCapstone

open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PresentedAlgebraPoint
open Komorebi.StrongArtin.AugmentedRelationAlgebra
open Komorebi.StrongArtin.AuxiliaryIdealBasic
open Komorebi.StrongArtin.AugmentationQuotientEquiv
open Komorebi.StrongArtin.PresentedAlgebraTangentEquiv

noncomputable section

set_option linter.unusedSectionVars false

variable {R k ι κ Aux : Type*} [CommRing R] [CommRing k]
  [DecidableEq Aux]

/-- The auxiliary-variable specialization is a quotient map with exactly the
expected augmentation ideal as kernel. -/
theorem augmentation_exact
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux) :
    Function.Surjective (baseSpecialization system column Q) ∧
      RingHom.ker (baseSpecialization system column Q).toRingHom =
        auxiliaryIdeal system column Q := by
  exact ⟨baseSpecialization_surjective system column Q,
    ker_baseSpecialization_eq_auxiliaryIdeal system column Q⟩

/-- The exact quotient equivalence produced by killing the auxiliary
coordinates. -/
def augmentationQuotientEquiv
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux) :
    AuxiliaryKilledAlgebra system column Q ≃ₐ[R] PresentedAlgebra system :=
  auxiliaryQuotientEquivBase system column Q

/-- The tangent fibre of a finite presented algebra at a solution is exactly
the kernel of its coordinate Jacobian. -/
def tangentFiberEquivJacobianKernel
    (system : System ι κ k) (x : ι → k)
    (hx : evalSystem system x = 0) :
    DualPointOver system x ≃ TangentSpace system x :=
  (tangentEquivDualPoint system x hx).symm

end

end Komorebi.StrongArtin.PresentedResolutionBridgeCapstone

#print axioms Komorebi.StrongArtin.PresentedResolutionBridgeCapstone.augmentation_exact
#print axioms Komorebi.StrongArtin.PresentedResolutionBridgeCapstone.tangentFiberEquivJacobianKernel
