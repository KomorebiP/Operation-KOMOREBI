import PresentedAlgebraPoint
import DualNumberSystemTangent

/-!
# Tangent vectors as dual-number points of the presented algebra

For a finite polynomial presentation and a base solution `x`, algebra points
in the dual numbers that reduce to `x` are exactly vectors in the kernel of the
coordinate Jacobian at `x`.
-/

namespace Komorebi.StrongArtin.PresentedAlgebraTangentEquiv

open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.PresentedAlgebraPoint
open Komorebi.StrongArtin.ExprMvPolynomial
open Komorebi.StrongArtin.DualNumberExprTangent
open Komorebi.StrongArtin.DualNumberSystemTangent
open TrivSqZeroExt

noncomputable section

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

variable {k ι κ : Type*} [CommRing k]

/-- The coordinate Jacobian tangent space at `x`. -/
abbrev TangentSpace (system : System ι κ k) (x : ι → k) :=
  LinearMap.ker (systemDerivative system x)

/-- Dual-number algebra points whose constant coordinates are the fixed base
point `x`. -/
def DualPointOver (system : System ι κ k) (x : ι → k) :=
  {φ : PresentedAlgebra system →ₐ[k] DualNumber k //
    ∀ i, TrivSqZeroExt.fst
      (φ (PresentedAlgebraPoint.generator system i)) = x i}

/-- A tangent vector gives a dual-number point over the base solution. -/
def dualPointOfTangent
    (system : System ι κ k) (x : ι → k)
    (hx : evalSystem system x = 0)
    (delta : TangentSpace system x) : DualPointOver system x := by
  let hrel : ∀ j, MvPolynomial.aeval (dualCoordinates x delta.1)
      (Expr.toMvPolynomial (system j)) = 0 :=
    (dualCoordinates_satisfy_iff_mem_ker system x delta.1 hx).2 delta.2
  refine ⟨PresentedAlgebraPoint.pointAlgHom system
      (dualCoordinates x delta.1) hrel, ?_⟩
  intro i
  rw [PresentedAlgebraPoint.pointAlgHom_generator]
  rfl

/-- The infinitesimal coordinate of a dual-number point. -/
def directionOfDualPoint
    (system : System ι κ k) (x : ι → k)
    (φ : DualPointOver system x) : ι → k :=
  fun i => TrivSqZeroExt.snd
    (φ.1 (PresentedAlgebraPoint.generator system i))

/-- The direction extracted from any dual-number point over a solution lies in
the coordinate Jacobian kernel. -/
theorem directionOfDualPoint_mem_ker
    (system : System ι κ k) (x : ι → k)
    (hx : evalSystem system x = 0)
    (φ : DualPointOver system x) :
    directionOfDualPoint system x φ ∈
      LinearMap.ker (systemDerivative system x) := by
  have hcoords :
      PresentedAlgebraPoint.coordinates system φ.1 =
        dualCoordinates x (directionOfDualPoint system x φ) := by
    funext i
    apply TrivSqZeroExt.ext
    · exact φ.2 i
    · rfl
  have hrel := PresentedAlgebraPoint.coordinates_satisfy system φ.1
  have hdual : ∀ j, MvPolynomial.aeval
      (dualCoordinates x (directionOfDualPoint system x φ))
      (Expr.toMvPolynomial (system j)) = 0 := by
    intro j
    rw [← hcoords]
    exact hrel j
  exact (dualCoordinates_satisfy_iff_mem_ker system x
    (directionOfDualPoint system x φ) hx).1 hdual

/-- Package the extracted infinitesimal coordinate as a tangent vector. -/
def tangentOfDualPoint
    (system : System ι κ k) (x : ι → k)
    (hx : evalSystem system x = 0)
    (φ : DualPointOver system x) : TangentSpace system x :=
  ⟨directionOfDualPoint system x φ,
    directionOfDualPoint_mem_ker system x hx φ⟩

/--
**Presented-algebra tangent equivalence.**
At a solution of the defining equations, dual-number algebra points over that
solution are exactly vectors in the kernel of the coordinate Jacobian.
-/
def tangentEquivDualPoint
    (system : System ι κ k) (x : ι → k)
    (hx : evalSystem system x = 0) :
    TangentSpace system x ≃ DualPointOver system x where
  toFun := dualPointOfTangent system x hx
  invFun := tangentOfDualPoint system x hx
  left_inv delta := by
    apply Subtype.ext
    funext i
    change TrivSqZeroExt.snd
        ((dualPointOfTangent system x hx delta).1
          (PresentedAlgebraPoint.generator system i)) = delta.1 i
    rw [show (dualPointOfTangent system x hx delta).1
        (PresentedAlgebraPoint.generator system i) =
          dualCoordinates x delta.1 i by
      exact PresentedAlgebraPoint.pointAlgHom_generator system
        (dualCoordinates x delta.1)
        ((dualCoordinates_satisfy_iff_mem_ker system x delta.1 hx).2 delta.2) i]
    rfl
  right_inv φ := by
    apply Subtype.ext
    apply Ideal.Quotient.algHom_ext k
    apply MvPolynomial.algHom_ext
    intro i
    change (dualPointOfTangent system x hx
        (tangentOfDualPoint system x hx φ)).1
          (PresentedAlgebraPoint.generator system i) =
      φ.1 (PresentedAlgebraPoint.generator system i)
    rw [show (dualPointOfTangent system x hx
        (tangentOfDualPoint system x hx φ)).1
          (PresentedAlgebraPoint.generator system i) =
        dualCoordinates x
          (directionOfDualPoint system x φ) i by
      exact PresentedAlgebraPoint.pointAlgHom_generator system
        (dualCoordinates x (directionOfDualPoint system x φ))
        ((dualCoordinates_satisfy_iff_mem_ker system x
          (directionOfDualPoint system x φ) hx).2
            (directionOfDualPoint_mem_ker system x hx φ)) i]
    apply TrivSqZeroExt.ext
    · simpa using (φ.2 i).symm
    · rfl

end

end Komorebi.StrongArtin.PresentedAlgebraTangentEquiv

#print axioms Komorebi.StrongArtin.PresentedAlgebraTangentEquiv.tangentEquivDualPoint
