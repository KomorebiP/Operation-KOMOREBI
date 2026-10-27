import PolynomialExpressionTaylor
import Mathlib.Algebra.MvPolynomial.Eval

/-!
# Compile multivariate polynomials into the finite expression syntax
-/

namespace Komorebi.StrongArtin.MvPolynomialExprCompiler

open Komorebi.StrongArtin.PolynomialExpressionTaylor

noncomputable section

variable {ι R : Type*} [CommRing R]

namespace Expr

/-- Syntactic natural power. -/
def powExpr (e : Expr ι R) : ℕ → Expr ι R
  | 0 => .const 1
  | n + 1 => .mul (powExpr e n) e

@[simp] theorem eval_powExpr (e : Expr ι R) (n : ℕ) (x : ι → R) :
    Expr.eval (powExpr e n) x = (Expr.eval e x) ^ n := by
  induction n with
  | zero => simp [powExpr]
  | succ n ih => simp [powExpr, ih, pow_succ]

/-- Right-associated syntactic product. -/
def mulList : List (Expr ι R) → Expr ι R
  | [] => .const 1
  | e :: es => .mul e (mulList es)

@[simp] theorem eval_mulList (es : List (Expr ι R)) (x : ι → R) :
    Expr.eval (mulList es) x = (es.map fun e => Expr.eval e x).prod := by
  induction es with
  | nil => simp [mulList]
  | cons e es ih => simp [mulList, ih]

/-- Syntactic product of variables with exponents from one monomial. -/
def varsMonomial (d : ι →₀ ℕ) : Expr ι R :=
  mulList <| d.support.toList.map fun i => powExpr (.var i) (d i)

@[simp] theorem eval_varsMonomial (d : ι →₀ ℕ) (x : ι → R) :
    Expr.eval (varsMonomial d : Expr ι R) x = d.prod fun i n => x i ^ n := by
  classical
  rw [varsMonomial, eval_mulList, List.map_map, Finset.prod_map_toList]
  apply Finset.prod_congr rfl
  intro i hi
  simp

/-- Compile one coefficient-monomial pair. -/
def monomialExpr (d : ι →₀ ℕ) (c : R) : Expr ι R :=
  .mul (.const c) (varsMonomial d)

@[simp] theorem eval_monomialExpr (d : ι →₀ ℕ) (c : R) (x : ι → R) :
    Expr.eval (monomialExpr d c) x = c * d.prod fun i n => x i ^ n := by
  simp [monomialExpr]

/-- Right-associated syntactic sum. -/
def addList : List (Expr ι R) → Expr ι R
  | [] => .const 0
  | e :: es => .add e (addList es)

@[simp] theorem eval_addList (es : List (Expr ι R)) (x : ι → R) :
    Expr.eval (addList es) x = (es.map fun e => Expr.eval e x).sum := by
  induction es with
  | nil => simp [addList]
  | cons e es ih => simp [addList, ih]

end Expr

/-- Compile a multivariate polynomial into the intrinsic expression syntax. -/
def compile (p : MvPolynomial ι R) : Expr ι R :=
  Expr.addList <|
    p.support.toList.map fun d => Expr.monomialExpr d (p.coeff d)

@[simp] theorem eval_compile (p : MvPolynomial ι R) (x : ι → R) :
    Expr.eval (compile p) x = MvPolynomial.eval x p := by
  classical
  simp [compile, MvPolynomial.eval_eq, Finsupp.prod]

end

end Komorebi.StrongArtin.MvPolynomialExprCompiler

#print axioms Komorebi.StrongArtin.MvPolynomialExprCompiler.eval_compile
