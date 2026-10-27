import Mathlib.LinearAlgebra.Matrix.Trace
import Mathlib.Algebra.Algebra.Rat
import Mathlib.Tactic.Abel

set_option autoImplicit false
namespace Komorebi.GainSolver
open Matrix
variable {ι κ : Type*} [Fintype κ]

/-- Exact rational Richardson correction of a right matrix equation B S = A. -/
def gainStep (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (B : Matrix ι κ ℚ) : Matrix ι κ ℚ := B + τ • (A - B*S)

/-- The solver's executable exact-rational iteration. -/
def gainIter (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (B : Matrix ι κ ℚ) : ℕ → Matrix ι κ ℚ
  | 0 => B
  | n+1 => gainStep A S τ (gainIter A S τ B n)

@[simp] theorem gainIter_zero (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (B : Matrix ι κ ℚ) : gainIter A S τ B 0 = B := rfl

@[simp] theorem gainIter_succ (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    gainIter A S τ B (n+1) = gainStep A S τ (gainIter A S τ B n) := rfl

/-- Exact residual recurrence; no symmetry, positivity or convergence assumption. -/
theorem residual_gainStep [DecidableEq κ] (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (B : Matrix ι κ ℚ) :
    A - gainStep A S τ B * S = (A-B*S)*(1-τ • S) := by
  simp only [gainStep, Matrix.add_mul, Matrix.smul_mul, Matrix.mul_sub,
    Matrix.mul_one, Matrix.mul_smul]
  abel

/-- Closed-form residual after an arbitrary finite number of exact updates. -/
theorem residual_gainIter [DecidableEq κ] (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (B : Matrix ι κ ℚ) (n : ℕ) :
    A - gainIter A S τ B n * S = (A-B*S)*(1-τ • S)^n := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [gainIter_succ, residual_gainStep, ih, pow_succ, Matrix.mul_assoc]

/-- An exact zero residual is preserved by the actual iteration. -/
theorem gainIter_of_zero_residual (A : Matrix ι κ ℚ) (S : Matrix κ κ ℚ) (τ : ℚ)
    (B : Matrix ι κ ℚ) (h : A-B*S=0) (n : ℕ) : gainIter A S τ B n = B := by
  induction n with
  | zero => rfl
  | succ n ih => simp [gainIter_succ, ih, gainStep, h]
end Komorebi.GainSolver
