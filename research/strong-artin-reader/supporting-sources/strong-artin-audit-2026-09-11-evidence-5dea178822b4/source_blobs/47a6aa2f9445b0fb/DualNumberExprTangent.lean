import ExprMvPolynomial
import Mathlib.Algebra.DualNumber

/-!
# First-order evaluation in dual numbers

Evaluation of a coordinate polynomial at `x + ε·delta` has constant term the
ordinary value and infinitesimal term the directional derivative.  This is the
bridge from the coordinate presentation to its Jacobian tangent space.
-/

namespace Komorebi.StrongArtin.DualNumberExprTangent

open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.ExprMvPolynomial
open TrivSqZeroExt

noncomputable section

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

variable {k ι : Type*} [CommRing k]

/-- Coordinates of the first-order deformation `x + ε delta`. -/
def dualCoordinates (x delta : ι → k) : ι → DualNumber k :=
  fun i => (x i, delta i)

@[simp] theorem fst_dualCoordinates (x delta : ι → k) (i : ι) :
    TrivSqZeroExt.fst (dualCoordinates x delta i) = x i := rfl

@[simp] theorem snd_dualCoordinates (x delta : ι → k) (i : ι) :
    TrivSqZeroExt.snd (dualCoordinates x delta i) = delta i := rfl

/-- Exact first-order Taylor formula in the dual-number algebra. -/
theorem aeval_toMvPolynomial_dualCoordinates
    (e : Expr ι k) (x delta : ι → k) :
    MvPolynomial.aeval (dualCoordinates x delta) (Expr.toMvPolynomial e) =
      (Expr.eval e x, Expr.deriv e x delta) := by
  induction e with
  | const c =>
      simp only [Expr.toMvPolynomial_const, MvPolynomial.aeval_C,
        Expr.eval_const, Expr.deriv_const]
      rw [TrivSqZeroExt.algebraMap_eq_inl]
      rfl
  | var i =>
      simp only [Expr.toMvPolynomial_var, MvPolynomial.aeval_X,
        Expr.eval_var, Expr.deriv_var]
      rfl
  | add f g hf hg =>
      simp only [Expr.toMvPolynomial_add, map_add, Expr.eval_add,
        Expr.deriv_add, hf, hg]
      rfl
  | neg f hf =>
      simp only [Expr.toMvPolynomial_neg, map_neg, Expr.eval_neg,
        Expr.deriv_neg, hf]
      rfl
  | mul f g hf hg =>
      simp only [Expr.toMvPolynomial_mul, map_mul, Expr.eval_mul,
        Expr.deriv_mul, hf, hg]
      apply TrivSqZeroExt.ext
      · rfl
      · change f.eval x * g.deriv x delta + f.deriv x delta * g.eval x =
          f.deriv x delta * g.eval x + f.eval x * g.deriv x delta
        exact add_comm _ _

/-- The constant coordinate of dual-number evaluation is ordinary evaluation. -/
theorem fst_aeval_toMvPolynomial_dualCoordinates
    (e : Expr ι k) (x delta : ι → k) :
    TrivSqZeroExt.fst
      (MvPolynomial.aeval (dualCoordinates x delta) (Expr.toMvPolynomial e)) =
        Expr.eval e x := by
  rw [aeval_toMvPolynomial_dualCoordinates]
  rfl

/-- The infinitesimal coordinate of dual-number evaluation is the directional derivative. -/
theorem snd_aeval_toMvPolynomial_dualCoordinates
    (e : Expr ι k) (x delta : ι → k) :
    TrivSqZeroExt.snd
      (MvPolynomial.aeval (dualCoordinates x delta) (Expr.toMvPolynomial e)) =
        Expr.deriv e x delta := by
  rw [aeval_toMvPolynomial_dualCoordinates]
  rfl

end

end Komorebi.StrongArtin.DualNumberExprTangent

#print axioms Komorebi.StrongArtin.DualNumberExprTangent.aeval_toMvPolynomial_dualCoordinates
