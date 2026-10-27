import MvPolynomialExprCompiler
import Mathlib.Algebra.MvPolynomial.PDeriv

/-!
# Polynomial semantics and derivatives of the expression compiler
-/

namespace Komorebi.StrongArtin.MvPolynomialExprDerivative

open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.MvPolynomialExprCompiler

noncomputable section

variable {R ι : Type*} [CommRing R]

namespace Expr

/-- Polynomial denotation of the intrinsic finite expression syntax. -/
def toPolynomial : Expr ι R → MvPolynomial ι R
  | .const c => MvPolynomial.C c
  | .var i => MvPolynomial.X i
  | .add f g => toPolynomial f + toPolynomial g
  | .neg f => -toPolynomial f
  | .mul f g => toPolynomial f * toPolynomial g

@[simp] theorem eval_toPolynomial (e : Expr ι R) (x : ι → R) :
    MvPolynomial.eval x (toPolynomial e) = Expr.eval e x := by
  induction e with
  | const c => simp [toPolynomial]
  | var i => simp [toPolynomial]
  | add f g hf hg => simp [toPolynomial, hf, hg]
  | neg f hf => simp [toPolynomial, hf]
  | mul f g hf hg => simp [toPolynomial, hf, hg]

@[simp] theorem toPolynomial_powExpr (e : Expr ι R) (n : ℕ) :
    toPolynomial (MvPolynomialExprCompiler.Expr.powExpr e n) =
      (toPolynomial e) ^ n := by
  induction n with
  | zero => simp [MvPolynomialExprCompiler.Expr.powExpr, toPolynomial]
  | succ n ih => simp [MvPolynomialExprCompiler.Expr.powExpr, toPolynomial, ih, pow_succ]

@[simp] theorem toPolynomial_mulList (es : List (Expr ι R)) :
    toPolynomial (MvPolynomialExprCompiler.Expr.mulList es) =
      (es.map toPolynomial).prod := by
  induction es with
  | nil => simp [MvPolynomialExprCompiler.Expr.mulList, toPolynomial]
  | cons e es ih => simp [MvPolynomialExprCompiler.Expr.mulList, toPolynomial, ih]

@[simp] theorem toPolynomial_varsMonomial (d : ι →₀ ℕ) :
    toPolynomial (MvPolynomialExprCompiler.Expr.varsMonomial d : Expr ι R) =
      MvPolynomial.monomial d 1 := by
  classical
  rw [MvPolynomialExprCompiler.Expr.varsMonomial, toPolynomial_mulList]
  rw [List.map_map]
  have hfun :
      (toPolynomial ∘ fun i => MvPolynomialExprCompiler.Expr.powExpr (.var i) (d i)) =
        (fun i => (MvPolynomial.X i : MvPolynomial ι R) ^ d i) := by
    funext i
    simp [toPolynomial]
  rw [hfun, Finset.prod_map_toList]
  exact (MvPolynomial.prod_X_pow_eq_monomial (R := R) (s := d))

@[simp] theorem toPolynomial_monomialExpr (d : ι →₀ ℕ) (c : R) :
    toPolynomial (MvPolynomialExprCompiler.Expr.monomialExpr d c : Expr ι R) =
      MvPolynomial.monomial d c := by
  rw [MvPolynomialExprCompiler.Expr.monomialExpr]
  simp [toPolynomial, MvPolynomial.monomial_eq]

@[simp] theorem toPolynomial_addList (es : List (Expr ι R)) :
    toPolynomial (MvPolynomialExprCompiler.Expr.addList es) =
      (es.map toPolynomial).sum := by
  induction es with
  | nil => simp [MvPolynomialExprCompiler.Expr.addList, toPolynomial]
  | cons e es ih => simp [MvPolynomialExprCompiler.Expr.addList, toPolynomial, ih]

/-- Directional derivative of an expression along a coordinate basis vector is
formal partial differentiation of its polynomial denotation. -/
theorem deriv_single_eq_eval_pderiv [DecidableEq ι]
    (e : Expr ι R) (x : ι → R) (i : ι) :
    Expr.deriv e x (Pi.single i 1) =
      MvPolynomial.eval x (MvPolynomial.pderiv i (toPolynomial e)) := by
  induction e with
  | const c => simp [toPolynomial]
  | var j => simp [toPolynomial, Pi.single_apply]
  | add f g hf hg => simp [toPolynomial, hf, hg]
  | neg f hf => simp [toPolynomial, hf]
  | mul f g hf hg =>
      simp only [Expr.deriv_mul, toPolynomial, MvPolynomial.pderiv_mul,
        map_add, map_mul, hf, hg, Expr.eval_toPolynomial]

end Expr

/-- The compiler is polynomial-semantics preserving, not only evaluation
preserving. -/
theorem toPolynomial_compile (p : MvPolynomial ι R) :
    Expr.toPolynomial (MvPolynomialExprCompiler.compile p) = p := by
  classical
  rw [MvPolynomialExprCompiler.compile, Expr.toPolynomial_addList]
  rw [List.map_map]
  have hfun :
      (Expr.toPolynomial ∘ fun d =>
        MvPolynomialExprCompiler.Expr.monomialExpr d (p.coeff d)) =
        (fun d => MvPolynomial.monomial d (p.coeff d)) := by
    funext d
    exact Expr.toPolynomial_monomialExpr d (p.coeff d)
  rw [hfun, Finset.sum_map_toList]
  exact p.as_sum.symm

/-- The compiled expression has exactly the formal partial derivatives of the
source polynomial. -/
theorem deriv_compile_single [DecidableEq ι]
    (p : MvPolynomial ι R) (x : ι → R) (i : ι) :
    Expr.deriv (MvPolynomialExprCompiler.compile p) x (Pi.single i 1) =
      MvPolynomial.eval x (MvPolynomial.pderiv i p) := by
  rw [Expr.deriv_single_eq_eval_pderiv, toPolynomial_compile]

end

end Komorebi.StrongArtin.MvPolynomialExprDerivative

#print axioms Komorebi.StrongArtin.MvPolynomialExprDerivative.toPolynomial_compile
#print axioms Komorebi.StrongArtin.MvPolynomialExprDerivative.deriv_compile_single
