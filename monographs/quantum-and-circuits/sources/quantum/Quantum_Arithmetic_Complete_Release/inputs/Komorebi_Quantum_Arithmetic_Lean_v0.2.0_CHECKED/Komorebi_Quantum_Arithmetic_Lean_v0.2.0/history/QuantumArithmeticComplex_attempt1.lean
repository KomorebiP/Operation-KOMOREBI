module
public import QuantumArithmeticBridge
public import Mathlib.Analysis.Real.Sqrt
public import Mathlib.Basic.Complex.Basic
public import Mathlib.Tactic.Ring

@[expose] public section

set_option autoImplicit false

namespace Komorebi.QuantumArithmetic

/-- Interpret the exact four rational coordinates in the complex numbers. -/
noncomputable def toComplex (x : Cyclo12) : ℂ :=
  ⟨(x.a : ℝ) + (x.b : ℝ) * Real.sqrt 3,
   (x.c : ℝ) + (x.d : ℝ) * Real.sqrt 3⟩

@[simp] theorem toComplex_zero : toComplex cZero = 0 := by
  apply Complex.ext <;> norm_num [toComplex, cZero]

@[simp] theorem toComplex_one : toComplex cOne = 1 := by
  apply Complex.ext <;> norm_num [toComplex, cOne]

@[simp] theorem toComplex_rat (r : ℚ) : toComplex (cRat r) = (r : ℂ) := by
  apply Complex.ext <;> simp [toComplex, cRat]

@[simp] theorem toComplex_add (x y : Cyclo12) :
    toComplex (cAdd x y) = toComplex x + toComplex y := by
  apply Complex.ext <;> simp [toComplex, cAdd] <;> ring

@[simp] theorem toComplex_mul (x y : Cyclo12) :
    toComplex (cMul x y) = toComplex x * toComplex y := by
  apply Complex.ext <;>
    simp only [toComplex, cMul, Complex.mul_re, Complex.mul_im] <;>
    push_cast <;> ring_nf <;> norm_num [Real.sq_sqrt]

@[simp] theorem toComplex_conj (x : Cyclo12) :
    toComplex (cConj x) = star (toComplex x) := by
  apply Complex.ext <;> simp [toComplex, cConj] <;> ring

@[simp] theorem toComplex_pow (x : Cyclo12) (n : Nat) :
    toComplex (cPow x n) = (toComplex x) ^ n := by
  induction n with
  | zero => simp [cPow]
  | succ n ih => simp [cPow, pow_succ, ih]

@[simp] theorem toComplex_sum (xs : List Cyclo12) :
    toComplex (cSum xs) = (xs.map toComplex).sum := by
  induction xs with
  | nil => simp [cSum]
  | cons x xs ih => simp [cSum, ih]

/-- The arithmetic coordinate root has the intended complex phase. -/
theorem toComplex_zeta12 : toComplex zeta12 =
    ⟨Real.sqrt 3 / 2, 1 / 2⟩ := by
  apply Complex.ext <;> norm_num [toComplex, zeta12] <;> ring

/-- The exact root certificate transfers to actual complex exponentiation. -/
theorem complex_zeta12_power_twelve : (toComplex zeta12) ^ 12 = 1 := by
  have h := congrArg toComplex zeta12_order_certificate
  simpa using h

/-- The inverse certificate also transfers to complex multiplication. -/
theorem complex_zeta12_inverse : toComplex zeta12 * star (toComplex zeta12) = 1 := by
  have h := congrArg toComplex zeta12_inverse_certificate
  simpa [zeta12Inv] using h

end Komorebi.QuantumArithmetic
