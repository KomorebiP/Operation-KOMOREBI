import PolynomialSystemTaylor
import Mathlib.Algebra.MvPolynomial.Eval

/-!
# Conversion from the internal finite polynomial syntax to `MvPolynomial`

The nonlinear Hensel calculus uses a small intrinsic expression syntax.  This
module embeds it in the universal multivariable polynomial algebra and proves
that the two evaluations agree exactly.
-/

namespace Komorebi.StrongArtin.ExprMvPolynomial

open Komorebi.StrongArtin.PolynomialExpressionTaylor

variable {ι R : Type*} [CommRing R]

noncomputable section

namespace Expr

/-- Interpret an internal polynomial expression as a multivariable polynomial. -/
def toMvPolynomial : Expr ι R → MvPolynomial ι R
  | .const c => MvPolynomial.C c
  | .var i => MvPolynomial.X i
  | .add f g => toMvPolynomial f + toMvPolynomial g
  | .neg f => -toMvPolynomial f
  | .mul f g => toMvPolynomial f * toMvPolynomial g

@[simp] theorem toMvPolynomial_const (c : R) :
    toMvPolynomial (.const c : Expr ι R) = MvPolynomial.C c := rfl

@[simp] theorem toMvPolynomial_var (i : ι) :
    toMvPolynomial (.var i : Expr ι R) = MvPolynomial.X i := rfl

@[simp] theorem toMvPolynomial_add (f g : Expr ι R) :
    toMvPolynomial (.add f g) = toMvPolynomial f + toMvPolynomial g := rfl

@[simp] theorem toMvPolynomial_neg (f : Expr ι R) :
    toMvPolynomial (.neg f) = -toMvPolynomial f := rfl

@[simp] theorem toMvPolynomial_mul (f g : Expr ι R) :
    toMvPolynomial (.mul f g) = toMvPolynomial f * toMvPolynomial g := rfl

/-- Evaluation of the universal polynomial agrees with the internal evaluator. -/
@[simp] theorem aeval_toMvPolynomial (e : Expr ι R) (x : ι → R) :
    MvPolynomial.aeval x (toMvPolynomial e) =
      Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.eval e x := by
  induction e with
  | const c =>
      simp only [toMvPolynomial, MvPolynomial.aeval_C,
        Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.eval_const]
      simp
  | var i => simp only [toMvPolynomial, MvPolynomial.aeval_X,
      Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.eval_var]
  | add f g hf hg =>
      simp only [toMvPolynomial, map_add,
        Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.eval_add]
      exact congrArg₂ (· + ·) hf hg
  | neg f hf =>
      simp only [toMvPolynomial, map_neg,
        Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.eval_neg]
      exact congrArg Neg.neg hf
  | mul f g hf hg =>
      simp only [toMvPolynomial, map_mul,
        Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.eval_mul]
      exact congrArg₂ (· * ·) hf hg

end Expr

end

end Komorebi.StrongArtin.ExprMvPolynomial

#print axioms Komorebi.StrongArtin.ExprMvPolynomial.Expr.aeval_toMvPolynomial
