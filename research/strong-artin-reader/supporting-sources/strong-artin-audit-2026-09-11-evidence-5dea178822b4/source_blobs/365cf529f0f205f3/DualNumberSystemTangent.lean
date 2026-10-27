import DualNumberExprTangent
import PolynomialSystemTaylor

/-!
# Dual-number solutions and the coordinate Jacobian kernel

At a residual solution `x`, first-order solutions of a finite polynomial system
in the dual-number algebra are exactly the directions killed by the coordinate
Jacobian.
-/

namespace Komorebi.StrongArtin.DualNumberSystemTangent

open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.ExprMvPolynomial
open Komorebi.StrongArtin.DualNumberExprTangent
open TrivSqZeroExt

noncomputable section

set_option linter.unusedSectionVars false

variable {k ι κ : Type*} [CommRing k]

/-- Evaluation of every defining relation at `x + ε delta`. -/
theorem aeval_relation_dualCoordinates
    (system : System ι κ k) (x delta : ι → k) (j : κ) :
    MvPolynomial.aeval (dualCoordinates x delta)
        (Expr.toMvPolynomial (system j)) =
      (evalSystem system x j, systemDerivative system x delta j) := by
  exact aeval_toMvPolynomial_dualCoordinates (system j) x delta

/-- At an ordinary solution, a dual-number coordinate tuple is a solution
exactly when its infinitesimal direction lies in the Jacobian kernel. -/
theorem dualCoordinates_satisfy_iff_derivative_eq_zero
    (system : System ι κ k) (x delta : ι → k)
    (hx : evalSystem system x = 0) :
    (∀ j, MvPolynomial.aeval (dualCoordinates x delta)
        (Expr.toMvPolynomial (system j)) = 0) ↔
      systemDerivative system x delta = 0 := by
  constructor
  · intro h
    apply funext
    intro j
    have hj := congrArg TrivSqZeroExt.snd (h j)
    rw [aeval_relation_dualCoordinates] at hj
    simpa using hj
  · intro h j
    apply TrivSqZeroExt.ext
    · rw [aeval_relation_dualCoordinates]
      have hxj := congrFun hx j
      simpa using hxj
    · rw [aeval_relation_dualCoordinates]
      have hj := congrFun h j
      simpa using hj

/-- Jacobian-kernel membership is the dual-number relation-vanishing
condition. -/
theorem dualCoordinates_satisfy_iff_mem_ker
    (system : System ι κ k) (x delta : ι → k)
    (hx : evalSystem system x = 0) :
    (∀ j, MvPolynomial.aeval (dualCoordinates x delta)
        (Expr.toMvPolynomial (system j)) = 0) ↔
      delta ∈ LinearMap.ker (systemDerivative system x) := by
  rw [dualCoordinates_satisfy_iff_derivative_eq_zero system x delta hx]
  rfl

end

end Komorebi.StrongArtin.DualNumberSystemTangent

#print axioms Komorebi.StrongArtin.DualNumberSystemTangent.dualCoordinates_satisfy_iff_derivative_eq_zero
