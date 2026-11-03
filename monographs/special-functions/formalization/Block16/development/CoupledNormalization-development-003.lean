import CoupledEvaluation
import Mathlib.Data.Nat.Choose.Basic

/-!
# Factorial normalization of the coupled derivative recurrence

The mathematical recurrence underlying `coupled_odd_derivatives` is defined
over exact rationals. Its order-(2n+1) arrays, divided by (2n+1)!, equal the
ordinary Taylor recurrence at every index, for arbitrary rational scales.
Finite inclusive prefixes therefore yield the certified polynomials.

This is a mathematical recurrence and finite-array specification. It does
not certify a Python interpreter, Fraction, mutation, guards or exceptions.
-/

set_option autoImplicit false
set_option maxHeartbeats 2500000

noncomputable section

namespace Komorebi.SpecialFunctions.Coupled.Scales

def oddFactorial (n : ℕ) : ℚ := ((2*n+1).factorial : ℚ)

theorem oddFactorial_ne_zero (n : ℕ) : oddFactorial n ≠ 0 := by
  unfold oddFactorial
  exact_mod_cast Nat.factorial_ne_zero (2*n+1)

theorem oddFactorial_zero : oddFactorial 0 = 1 := by
  norm_num [oddFactorial]

theorem oddFactorial_succ (n : ℕ) :
    oddFactorial (n+1) = (2*(n : ℚ)+3) * ((2*n+2).factorial : ℚ) := by
  have he : 2*(n+1)+1 = (2*n+2)+1 := by omega
  rw [oddFactorial, he, Nat.factorial_succ]
  push_cast
  ring

theorem binomial_factorial_product (n i : ℕ) (hi : i ≤ n) :
    ((2*n+2).choose (2*i+1) : ℚ) * oddFactorial i * oddFactorial (n-i) =
      ((2*n+2).factorial : ℚ) := by
  have h := Nat.choose_mul_factorial_mul_factorial (show 2*i+1 ≤ 2*n+2 by omega)
  have he : 2*n+2-(2*i+1) = 2*(n-i)+1 := by omega
  rw [he] at h
  unfold oddFactorial
  exact_mod_cast h

theorem binomial_factorial_quotient (n i : ℕ) (hi : i ≤ n) :
    ((2*n+2).choose (2*i+1) : ℚ) / oddFactorial (n+1) =
      1 / ((2*(n : ℚ)+3) * oddFactorial i * oddFactorial (n-i)) := by
  have h := binomial_factorial_product n i hi
  have hf := oddFactorial_succ n
  have hn : (2*(n : ℚ)+3) ≠ 0 := by positivity
  apply (div_eq_div_iff (oddFactorial_ne_zero (n+1))
    (mul_ne_zero (mul_ne_zero hn (oddFactorial_ne_zero i)) (oddFactorial_ne_zero (n-i)))).mpr
  calc
    _ = (2*(n : ℚ)+3) *
        (((2*n+2).choose (2*i+1) : ℚ) * oddFactorial i * oddFactorial (n-i)) := by ring
    _ = _ := by rw [h, hf]; ring

def derivativeRow (q r : ℚ) (c : ℕ → ℚ × ℚ) (n : ℕ) : ℚ :=
  ∑ i : Fin (n+1), ((2*n+2).choose (2*i.val+1) : ℚ) *
    (c i.val).1 * (c (n-i.val)).2 * q^(2*i.val+1) * r^(2*(n-i.val)+1)

def RationalScales.derivativeNext (p : RationalScales) (c : ℕ → ℚ × ℚ) (n : ℕ) : ℚ × ℚ :=
  (derivativeRow p.q p.r c n, derivativeRow p.a p.b c n)

def RationalScales.derivatives (p : RationalScales) : ℕ → ℚ × ℚ
  | 0 => (1, 1)
  | n+1 =>
    ((∑ i : Fin (n+1), ((2*n+2).choose (2*i.val+1) : ℚ) *
      (p.derivatives i.val).1 * (p.derivatives (n-i.val)).2 *
      p.q^(2*i.val+1) * p.r^(2*(n-i.val)+1)),
     (∑ i : Fin (n+1), ((2*n+2).choose (2*i.val+1) : ℚ) *
      (p.derivatives i.val).1 * (p.derivatives (n-i.val)).2 *
      p.a^(2*i.val+1) * p.b^(2*(n-i.val)+1)))
termination_by n => n
decreasing_by all_goals omega

theorem rational_derivatives_zero (p : RationalScales) : p.derivatives 0 = (1,1) := by
  rw [RationalScales.derivatives.eq_def]

theorem rational_derivatives_succ (p : RationalScales) (n : ℕ) :
    p.derivatives (n+1) = p.derivativeNext p.derivatives n := by
  rw [RationalScales.derivatives.eq_def]
  rfl

def RationalScales.IsDerivativeSolution (p : RationalScales) (c : ℕ → ℚ × ℚ) : Prop :=
  c 0 = (1,1) ∧ ∀ n, c (n+1) = p.derivativeNext c n

theorem rational_derivatives_solution (p : RationalScales) :
    p.IsDerivativeSolution p.derivatives :=
  ⟨rational_derivatives_zero p, rational_derivatives_succ p⟩

theorem derivative_solution_unique (p : RationalScales) {c d : ℕ → ℚ × ℚ}
    (hc : p.IsDerivativeSolution c) (hd : p.IsDerivativeSolution d) : c = d := by
  funext n
  induction n using Nat.strong_induction_on with
  | h n ih =>
    cases n with
    | zero => exact hc.1.trans hd.1.symm
    | succ n =>
      rw [hc.2 n, hd.2 n]
      apply Prod.ext
      all_goals
        simp only [RationalScales.derivativeNext, derivativeRow, Prod.fst, Prod.snd]
        apply Finset.sum_congr rfl
        intro i _
        have hi : i.val < n+1 := i.isLt
        have hj : n-i.val < n+1 := by omega
        simp only [ih i.val hi, ih (n-i.val) hj]

theorem derivativeRow_factorialScale (q r : ℚ) (c : ℕ → ℚ × ℚ) (n : ℕ) :
    derivativeRow q r (fun k => (oddFactorial k * (c k).1, oddFactorial k * (c k).2)) n =
      ((2*n+2).factorial : ℚ) *
        ∑ i : Fin (n+1), q^(2*i.val+1) * r^(2*(n-i.val)+1) * (c i.val).1 * (c (n-i.val)).2 := by
  rw [derivativeRow, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  have hi : i.val ≤ n := by omega
  have h := binomial_factorial_product n i.val hi
  dsimp only
  calc
    _ = (((2*n+2).choose (2*i.val+1) : ℚ) * oddFactorial i.val * oddFactorial (n-i.val)) *
        (q^(2*i.val+1) * r^(2*(n-i.val)+1) * (c i.val).1 * (c (n-i.val)).2) := by ring
    _ = _ := by rw [h]

theorem factorial_scaled_coefficients_solution (p : RationalScales) :
    p.IsDerivativeSolution
      (fun n => (oddFactorial n * (p.coefficients n).1, oddFactorial n * (p.coefficients n).2)) := by
  constructor
  · dsimp only
    have hz : p.coefficients 0 = (1,1) := by rw [RationalScales.coefficients.eq_def]
    rw [hz, oddFactorial_zero]
    norm_num
  · intro n
    dsimp only
    have hn : (2*(n : ℚ)+3) ≠ 0 := by positivity
    have hc := RationalScales.coefficients.eq_def p (n+1)
    rw [hc]
    apply Prod.ext
    all_goals
      simp only [RationalScales.derivativeNext, derivativeRow_factorialScale,
        oddFactorial_succ, Prod.fst, Prod.snd]
      field_simp [hn]

theorem rational_derivatives_factorial (p : RationalScales) (n : ℕ) :
    p.derivatives n =
      (oddFactorial n * (p.coefficients n).1, oddFactorial n * (p.coefficients n).2) :=
  congrFun (derivative_solution_unique p (rational_derivatives_solution p)
    (factorial_scaled_coefficients_solution p)) n

end Komorebi.SpecialFunctions.Coupled.Scales
