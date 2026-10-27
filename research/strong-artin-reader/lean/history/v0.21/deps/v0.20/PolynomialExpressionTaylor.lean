import ScalarPowerDivisibility
import Mathlib.Tactic.Ring

/-!
# Taylor gain for scalar polynomial expressions

A small intrinsic syntax for polynomial expressions is enough to cover finite
coordinate presentations.  The directional derivative is defined by the usual
sum and product rules.  Every positive-depth correction has a first-order
remainder one filtration level deeper.
-/

namespace Komorebi.StrongArtin.PolynomialExpressionTaylor

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.ScalarPowerDivisibility

variable {ι R : Type*} [CommRing R]

/-- Polynomial expressions in coordinates indexed by `ι`. -/
inductive Expr (ι : Type*) (R : Type*) where
  | const : R → Expr ι R
  | var : ι → Expr ι R
  | add : Expr ι R → Expr ι R → Expr ι R
  | neg : Expr ι R → Expr ι R
  | mul : Expr ι R → Expr ι R → Expr ι R

deriving Repr

namespace Expr

/-- Evaluate a polynomial expression. -/
def eval : Expr ι R → (ι → R) → R
  | const c, _ => c
  | var i, x => x i
  | add f g, x => eval f x + eval g x
  | neg f, x => -eval f x
  | mul f g, x => eval f x * eval g x

/-- Directional derivative at `x` in direction `delta`. -/
def deriv : Expr ι R → (ι → R) → (ι → R) → R
  | const _, _, _ => 0
  | var i, _, delta => delta i
  | add f g, x, delta => deriv f x delta + deriv g x delta
  | neg f, x, delta => -deriv f x delta
  | mul f g, x, delta =>
      deriv f x delta * eval g x + eval f x * deriv g x delta

@[simp] theorem eval_const (c : R) (x : ι → R) :
    eval (.const c) x = c := rfl

@[simp] theorem eval_var (i : ι) (x : ι → R) :
    eval (.var i) x = x i := rfl

@[simp] theorem eval_add (f g : Expr ι R) (x : ι → R) :
    eval (.add f g) x = eval f x + eval g x := rfl

@[simp] theorem eval_neg (f : Expr ι R) (x : ι → R) :
    eval (.neg f) x = -eval f x := rfl

@[simp] theorem eval_mul (f g : Expr ι R) (x : ι → R) :
    eval (.mul f g) x = eval f x * eval g x := rfl

@[simp] theorem deriv_const (c : R) (x delta : ι → R) :
    deriv (.const c) x delta = 0 := rfl

@[simp] theorem deriv_var (i : ι) (x delta : ι → R) :
    deriv (.var i) x delta = delta i := rfl

@[simp] theorem deriv_add (f g : Expr ι R) (x delta : ι → R) :
    deriv (.add f g) x delta = deriv f x delta + deriv g x delta := rfl

@[simp] theorem deriv_neg (f : Expr ι R) (x delta : ι → R) :
    deriv (.neg f) x delta = -deriv f x delta := rfl

@[simp] theorem deriv_mul (f g : Expr ι R) (x delta : ι → R) :
    deriv (.mul f g) x delta =
      deriv f x delta * eval g x + eval f x * deriv g x delta := rfl

/-- The directional derivative is additive in its direction. -/
theorem deriv_add_direction (e : Expr ι R) (x delta eta : ι → R) :
    deriv e x (delta + eta) = deriv e x delta + deriv e x eta := by
  induction e with
  | const c => simp
  | var i => simp
  | add f g hf hg => simp [hf, hg]; ring
  | neg f hf => simp [hf]; ring
  | mul f g hf hg => simp [hf, hg]; ring

/-- The directional derivative is homogeneous in its direction. -/
theorem deriv_smul_direction (e : Expr ι R) (x delta : ι → R) (a : R) :
    deriv e x (a • delta) = a * deriv e x delta := by
  induction e with
  | const c => simp
  | var i => simp
  | add f g hf hg => simp [hf, hg]; ring
  | neg f hf => simp [hf]
  | mul f g hf hg => simp [hf, hg]; ring

/-- The directional derivative packaged as a linear map. -/
def derivativeLinear (e : Expr ι R) (x : ι → R) : (ι → R) →ₗ[R] R where
  toFun := deriv e x
  map_add' := deriv_add_direction e x
  map_smul' := by
    intro a delta
    simpa [smul_eq_mul] using deriv_smul_direction e x delta a

/-- A polynomial increment preserves the filtration depth of its input change. -/
theorem eval_sub_powDivisible
    (e : Expr ι R) (pi : R) {n : ℕ} (x delta : ι → R)
    (hdelta : PowDivisible pi n delta) :
    PowDivisible pi n (eval e (x + delta) - eval e x) := by
  induction e with
  | const c => simp
  | var i =>
      simpa using powDivisible_apply hdelta i
  | add f g hf hg =>
      simpa [eval, sub_eq_add_neg, add_assoc, add_left_comm, add_comm] using
        (hf.add hg)
  | neg f hf =>
      change PowDivisible pi n (-eval f (x + delta) - -eval f x)
      have heq : -eval f (x + delta) - -eval f x =
          -(eval f (x + delta) - eval f x) := by ring
      rw [heq]
      exact hf.neg
  | mul f g hf hg =>
      have h₁ := powDivisible_mul_right hf (eval g (x + delta))
      have h₂ := powDivisible_mul_left (eval f x) hg
      have hsum := h₁.add h₂
      have hid :
          eval f (x + delta) * eval g (x + delta) - eval f x * eval g x =
            (eval f (x + delta) - eval f x) * eval g (x + delta) +
              eval f x * (eval g (x + delta) - eval g x) := by
        ring
      simpa [eval, hid] using hsum

/-- A directional derivative has the same filtration depth as its direction. -/
theorem deriv_powDivisible
    (e : Expr ι R) (pi : R) {n : ℕ} (x delta : ι → R)
    (hdelta : PowDivisible pi n delta) :
    PowDivisible pi n (deriv e x delta) := by
  induction e with
  | const c => simp
  | var i => simpa using powDivisible_apply hdelta i
  | add f g hf hg => simpa [deriv] using hf.add hg
  | neg f hf => simpa [deriv] using hf.neg
  | mul f g hf hg =>
      exact (powDivisible_mul_right hf (eval g x)).add (powDivisible_mul_left (eval f x) hg)


/-- Evaluation at two points differing by a depth-`n` vector differs at the
same depth. -/
theorem eval_sub_eval_powDivisible
    (e : Expr ι R) (pi : R) {n : ℕ} (x y : ι → R)
    (hxy : PowDivisible pi n (x - y)) :
    PowDivisible pi n (eval e x - eval e y) := by
  have h := eval_sub_powDivisible e pi y (x - y) hxy
  have hpoint : y + (x - y) = x := by
    funext i
    simp
  simpa [hpoint] using h

/-- The polynomial Jacobian is stable modulo the same power as a change of
base point. -/
theorem deriv_sub_deriv_powDivisible
    (e : Expr ι R) (pi : R) {n : ℕ} (x y delta : ι → R)
    (hxy : PowDivisible pi n (x - y)) :
    PowDivisible pi n (deriv e x delta - deriv e y delta) := by
  induction e with
  | const c => simp
  | var i => simp
  | add f g hf hg =>
      simpa [deriv, sub_eq_add_neg, add_assoc, add_left_comm, add_comm] using
        (hf.add hg)
  | neg f hf =>
      have heq : -deriv f x delta - -deriv f y delta =
          -(deriv f x delta - deriv f y delta) := by ring
      change PowDivisible pi n (-deriv f x delta - -deriv f y delta)
      rw [heq]
      exact hf.neg
  | mul f g hf hg =>
      let dFx := deriv f x delta
      let dFy := deriv f y delta
      let dGx := deriv g x delta
      let dGy := deriv g y delta
      let Fx := eval f x
      let Fy := eval f y
      let Gx := eval g x
      let Gy := eval g y
      have hG : PowDivisible pi n (Gx - Gy) := by
        simpa [Gx, Gy] using eval_sub_eval_powDivisible g pi x y hxy
      have hF : PowDivisible pi n (Fx - Fy) := by
        simpa [Fx, Fy] using eval_sub_eval_powDivisible f pi x y hxy
      have hsum :=
        (powDivisible_mul_right hf Gx).add
          ((powDivisible_mul_left dFy hG).add
            ((powDivisible_mul_right hF dGx).add
              (powDivisible_mul_left Fy hg)))
      have hid :
          (dFx * Gx + Fx * dGx) - (dFy * Gy + Fy * dGy) =
            (dFx - dFy) * Gx + dFy * (Gx - Gy) +
              (Fx - Fy) * dGx + Fy * (dGx - dGy) := by
        ring
      change PowDivisible pi n
        ((dFx * Gx + Fx * dGx) - (dFy * Gy + Fy * dGy))
      rw [hid]
      simpa [add_assoc] using hsum

/-- The scalar first-order Taylor remainder. -/
def remainder (e : Expr ι R) (x delta : ι → R) : R :=
  eval e (x + delta) - eval e x - deriv e x delta

/-- Every polynomial expression gains one filtration level after subtracting
its first-order directional derivative. -/
theorem remainder_powDivisible
    (e : Expr ι R) (pi : R) {n : ℕ} (hn : 1 ≤ n)
    (x delta : ι → R) (hdelta : PowDivisible pi n delta) :
    PowDivisible pi (n + 1) (remainder e x delta) := by
  induction e with
  | const c => simp [remainder]
  | var i => simp [remainder]
  | add f g hf hg =>
      simpa [remainder, eval, deriv, sub_eq_add_neg, add_assoc, add_left_comm,
        add_comm] using (hf.add hg)
  | neg f hf =>
      have heq : remainder (.neg f) x delta = -(remainder f x delta) := by
        simp [remainder]
        ring
      rw [heq]
      exact hf.neg
  | mul f g hf hg =>
      let F := eval f x
      let F' := eval f (x + delta)
      let G := eval g x
      let G' := eval g (x + delta)
      let dF := deriv f x delta
      let dG := deriv g x delta
      have hRf : PowDivisible pi (n + 1) (F' - F - dF) := by
        simpa [F, F', dF, remainder] using hf
      have hRg : PowDivisible pi (n + 1) (G' - G - dG) := by
        simpa [G, G', dG, remainder] using hg
      have hdF : PowDivisible pi n dF := by
        simpa [dF] using deriv_powDivisible f pi x delta hdelta
      have hDG : PowDivisible pi n (G' - G) := by
        simpa [G, G'] using eval_sub_powDivisible g pi x delta hdelta
      have hcross : PowDivisible pi (n + n) (dF * (G' - G)) := powDivisible_mul hdF hDG
      have hcross' : PowDivisible pi (n + 1) (dF * (G' - G)) :=
        hcross.mono (Nat.add_le_add_left hn n)
      have hsum := (powDivisible_mul_right hRf G').add ((powDivisible_mul_left F hRg).add hcross')
      have hid :
          F' * G' - F * G - (dF * G + F * dG) =
            (F' - F - dF) * G' + F * (G' - G - dG) + dF * (G' - G) := by
        ring
      change PowDivisible pi (n + 1) (F' * G' - F * G - (dF * G + F * dG))
      rw [hid]
      simpa [add_assoc] using hsum

end Expr

end Komorebi.StrongArtin.PolynomialExpressionTaylor

#print axioms Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.derivativeLinear
#print axioms Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.eval_sub_powDivisible
#print axioms Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.deriv_sub_deriv_powDivisible
#print axioms Komorebi.StrongArtin.PolynomialExpressionTaylor.Expr.remainder_powDivisible
