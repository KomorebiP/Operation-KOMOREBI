import ResidualLayer
import PolynomialSystemTaylor

/-! Polynomial evaluation, derivatives and moving relation matrices commute with
residue maps. This discharges the reduction comparisons in the graded theorem. -/
namespace Komorebi.StrongArtin.PolynomialResidueModel
open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.ResidualLayer
open Komorebi.StrongArtin.VariableJacobianHensel
open scoped BigOperators

variable {R k ι κ η : Type*} [CommRing R] [CommRing k]

/-- Reduce coefficients while preserving polynomial syntax. -/
def reduceExpr (q : R →+* k) : Expr ι R → Expr ι k
  | .const a => .const (q a)
  | .var i => .var i
  | .add e f => .add (reduceExpr q e) (reduceExpr q f)
  | .neg e => .neg (reduceExpr q e)
  | .mul e f => .mul (reduceExpr q e) (reduceExpr q f)

@[simp] theorem eval_reduceExpr (q : R →+* k) (e : Expr ι R) (x : ι → R) :
    Expr.eval (reduceExpr q e) (fun i => q (x i)) = q (Expr.eval e x) := by
  induction e with
  | const a => rfl
  | var i => rfl
  | add e f he hf => simp [reduceExpr, he, hf]
  | neg e he => simp [reduceExpr, he]
  | mul e f he hf => simp [reduceExpr, he, hf]

@[simp] theorem deriv_reduceExpr (q : R →+* k) (e : Expr ι R) (x u : ι → R) :
    Expr.deriv (reduceExpr q e) (fun i => q (x i)) (fun i => q (u i)) =
      q (Expr.deriv e x u) := by
  induction e with
  | const a => simp [reduceExpr]
  | var i => rfl
  | add e f he hf => simp [reduceExpr, he, hf]
  | neg e he => simp [reduceExpr, he]
  | mul e f he hf => simp [reduceExpr, he, hf]

/-- Reduce each equation. -/
def reduceSystem (q : R →+* k) (F : System ι κ R) : System ι κ k :=
  fun j => reduceExpr q (F j)

theorem derivative_residue_comparison
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi}) (F : System ι κ R)
    (base x : ι → R) (hx : SameResidual pi base x) (u : ι → R) :
    (coordinateReduction pi q hq hker).map (systemDerivative F x u) =
      systemDerivative (reduceSystem q F) (fun i => q (base i))
        ((coordinateReduction pi q hq hker).map u) := by
  have hred := (coordinateReduction (ι := ι) pi q hq hker).map_eq_of_difference_divisible hx
  have hr : (fun i => q (x i)) = (fun i => q (base i)) := hred
  rw [← hr]
  funext j
  exact (deriv_reduceExpr q (F j) x u).symm

section Relations
variable [Fintype κ]

/-- A matrix of polynomial coefficients gives a state-dependent relation map. -/
def relationMap (B : η → κ → Expr ι R) (x : ι → R) :
    (κ → R) →ₗ[R] (η → R) where
  toFun := fun w l => ∑ j, Expr.eval (B l j) x * w j
  map_add' := by
    intro w z
    funext l
    simp [mul_add, Finset.sum_add_distrib]
  map_smul' := by
    intro a w
    funext l
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j _
    ring

/-- Reduce each coefficient of the relation matrix. -/
def reduceRelations (q : R →+* k) (B : η → κ → Expr ι R) : η → κ → Expr ι k :=
  fun l j => reduceExpr q (B l j)

theorem relation_residue_comparison
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span {pi}) (B : η → κ → Expr ι R)
    (base x : ι → R) (hx : SameResidual pi base x) (w : κ → R) :
    (coordinateReduction pi q hq hker).map (relationMap B x w) =
      relationMap (reduceRelations q B) (fun i => q (base i))
        ((coordinateReduction pi q hq hker).map w) := by
  have hr : (fun i => q (x i)) = (fun i => q (base i)) :=
    (coordinateReduction (ι := ι) pi q hq hker).map_eq_of_difference_divisible hx
  rw [← hr]
  funext l
  change q (∑ j, Expr.eval (B l j) x * w j) =
    ∑ j, Expr.eval (reduceExpr q (B l j)) (fun i => q (x i)) * q (w j)
  simp only [map_sum, map_mul, eval_reduceExpr]

end Relations
end Komorebi.StrongArtin.PolynomialResidueModel
