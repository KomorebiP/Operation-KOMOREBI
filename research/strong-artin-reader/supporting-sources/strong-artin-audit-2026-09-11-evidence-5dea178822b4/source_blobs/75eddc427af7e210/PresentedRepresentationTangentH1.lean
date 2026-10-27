import PresentedAlgebraTangentEquiv
import RepresentationGaugeH1

/-!
# Presented deformation tangents and adjoint H¹

An explicit first-jet comparison between a finite polynomial presentation and
the multiplication equations of a representation transports the presented
algebra's dual-number tangent fibre to adjoint cocycles.  Quotienting by the
pulled-back infinitesimal conjugation directions gives adjoint `H¹`.
-/

namespace Komorebi.StrongArtin.PresentedRepresentationTangentH1

open groupCohomology
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PresentedAlgebraTangentEquiv
open Komorebi.StrongArtin.RepresentationTangentCocycles
open Komorebi.StrongArtin.RepresentationGaugeH1

noncomputable section

universe u

variable {k G V ι κ : Type u} [CommRing k] [Group G]
  [AddCommGroup V] [Module k V]

/-- The exact first-jet datum required to recognize a finite presentation as a
presentation of the framed representation deformation problem at `rho`. -/
structure Datum
    (system : System ι κ k) (x : ι → k)
    (rho : Representation k G V) where
  /-- The coordinate Jacobian kernel is the derivative of the representation
  multiplication equations. -/
  tangentEquiv : TangentSpace system x ≃ₗ[k] representationTangents rho

namespace Datum

variable {system : System ι κ k} {x : ι → k}
  {rho : Representation k G V} (D : Datum system x rho)

/-- The presented framed tangent is adjoint `Z¹`. -/
def presentedTangentEquivCocycles :
    TangentSpace system x ≃ₗ[k] cocycles₁ (AdRep rho) :=
  D.tangentEquiv.trans (tangentEquivCocycles rho)

/-- The canonical map from the presented tangent to adjoint `H¹`. -/
def presentedTangentToH1 :
    TangentSpace system x →ₗ[k] H1 (AdRep rho) :=
  (tangentToH1 rho).comp D.tangentEquiv.toLinearMap

/-- Infinitesimal conjugation directions pulled back into presentation coordinates. -/
def presentedGaugeDirections : Submodule k (TangentSpace system x) :=
  (gaugeRange rho).comap D.tangentEquiv.toLinearMap

/-- The presented tangent-to-`H¹` map is surjective. -/
theorem presentedTangentToH1_surjective :
    Function.Surjective (presentedTangentToH1 D) := by
  intro h
  rcases tangentToH1_surjective rho h with ⟨delta, rfl⟩
  exact ⟨D.tangentEquiv.symm delta, by
    simp [presentedTangentToH1]⟩

/-- Its kernel is exactly the pulled-back infinitesimal conjugation space. -/
theorem ker_presentedTangentToH1 :
    LinearMap.ker (presentedTangentToH1 D) = presentedGaugeDirections D := by
  rw [presentedTangentToH1, LinearMap.ker_comp]
  rw [ker_tangentToH1 rho]
  rfl

/-- The unframed tangent of the presented problem. -/
abbrev PresentedUnframedTangent :=
  TangentSpace system x ⧸ presentedGaugeDirections D

/-- A correctly differentiated finite presentation has unframed tangent equal
to adjoint first cohomology. -/
def presentedUnframedTangentEquivH1 :
    PresentedUnframedTangent D ≃ₗ[k] H1 (AdRep rho) := by
  let e := (presentedTangentToH1 D).quotKerEquivOfSurjective
    (presentedTangentToH1_surjective D)
  rw [ker_presentedTangentToH1 D] at e
  exact e

/-- At a genuine base solution, dual-number points of the presented algebra are
exactly framed representation tangents. -/
def representationTangentEquivDualPoint
    (hx : evalSystem system x = 0) :
    representationTangents rho ≃ DualPointOver system x :=
  D.tangentEquiv.symm.toEquiv.trans
    (tangentEquivDualPoint system x hx)

/-- Equivalently, dual-number points above the base representation are exactly
adjoint one-cocycles. -/
def cocyclesEquivDualPoint
    (hx : evalSystem system x = 0) :
    cocycles₁ (AdRep rho) ≃ DualPointOver system x :=
  (tangentEquivCocycles rho).symm.toEquiv.trans
    (representationTangentEquivDualPoint D hx)

end Datum

end

end Komorebi.StrongArtin.PresentedRepresentationTangentH1

#print axioms Komorebi.StrongArtin.PresentedRepresentationTangentH1.Datum.presentedUnframedTangentEquivH1
#print axioms Komorebi.StrongArtin.PresentedRepresentationTangentH1.Datum.cocyclesEquivDualPoint
