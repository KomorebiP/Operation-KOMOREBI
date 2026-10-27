import Komorebi.RationalMatrixCertificates
import Mathlib.Algebra.Order.BigOperators.Ring.Finset
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Positivity

set_option autoImplicit false
namespace Komorebi.RoundoffSolver
open Matrix Komorebi.ExactPosterior
variable {ι κ ν : Type*}

@[simp] theorem energy_zero [Fintype ι] [Fintype κ] :
    rationalEnergy (0 : Matrix ι κ ℚ) = 0 := by simp [rationalEnergy]

@[simp] theorem energy_neg [Fintype ι] [Fintype κ] (A : Matrix ι κ ℚ) :
    rationalEnergy (-A) = rationalEnergy A := by simp [rationalEnergy]

/-- Young's inequality without square roots, summed in the declared Frobenius convention. -/
theorem energy_young [Fintype ι] [Fintype κ] (A B : Matrix ι κ ℚ) (t : ℚ) :
    t*rationalEnergy (A+B) ≤ (t+1)*rationalEnergy A + t*(t+1)*rationalEnergy B := by
  have h := Finset.sum_le_sum fun i (_ : i ∈ Finset.univ) =>
    Finset.sum_le_sum fun j (_ : j ∈ Finset.univ) =>
      (show t*(A i j+B i j)^2 ≤ (t+1)*(A i j)^2+t*(t+1)*(B i j)^2 by
        nlinarith only [sq_nonneg (A i j-t*B i j)])
  simpa only [rationalEnergy, Matrix.add_apply, Finset.sum_add_distrib,
    Finset.mul_sum] using h

theorem energy_add_le [Fintype ι] [Fintype κ] (A B : Matrix ι κ ℚ) :
    rationalEnergy (A+B) ≤ 2*rationalEnergy A+2*rationalEnergy B := by
  simpa only [one_mul, show (1 : ℚ)+1=2 by norm_num] using energy_young A B 1

/-- Finite Cauchy-Schwarz, valid for rectangular matrices and empty coordinate types. -/
theorem energy_mul_le [Fintype ι] [Fintype κ] [Fintype ν]
    (A : Matrix ι κ ℚ) (B : Matrix κ ν ℚ) :
    rationalEnergy (A*B) ≤ rationalEnergy A*rationalEnergy B := by
  calc
    rationalEnergy (A*B) ≤ ∑ i, ∑ k, (∑ j, (A i j)^2)*(∑ j, (B j k)^2) := by
      exact Finset.sum_le_sum fun i _ => Finset.sum_le_sum fun k _ =>
        Finset.sum_mul_sq_le_sq_mul_sq Finset.univ (A i) (fun j => B j k)
    _ = ∑ i, (∑ j, (A i j)^2)*rationalEnergy B := by
      apply Finset.sum_congr rfl
      intro i _
      rw [← Finset.mul_sum, Finset.sum_comm]
      rfl
    _ = rationalEnergy A*rationalEnergy B := by rw [← Finset.sum_mul]; rfl

/-- A robust energy step: exact contraction plus bounded additive update error. -/
theorem energy_add_contract [Fintype ι] [Fintype κ]
    (A E : Matrix ι κ ℚ) (q d e : ℚ)
    (hq : 0 ≤ q) (h1 : q < 1) (hd : 0 ≤ d) (he : 0 ≤ e)
    (hA : rationalEnergy A ≤ q*d) (hE : rationalEnergy E ≤ e) :
    rationalEnergy (A+E) ≤ ((1+q)/2)*d + (3/(1-q))*e := by
  let s : ℚ := (1-q)/2
  have hs : 0 < s := by dsimp [s]; positivity
  have hden : 1-q ≠ 0 := ne_of_gt (sub_pos.mpr h1)
  have hy := energy_young E A s
  rw [add_comm E A] at hy
  have hx := mul_le_mul_of_nonneg_left hA (show 0 ≤ s*(s+1) by positivity)
  have hz := mul_le_mul_of_nonneg_left hE (show 0 ≤ s+1 by positivity)
  have hc : s*(s+1)*q ≤ s*((1+q)/2) := by
    dsimp [s]
    nlinarith only [mul_nonneg (sub_pos.mpr h1).le (sq_nonneg (1-q))]
  have hcd := mul_le_mul_of_nonneg_right hc hd
  have hec : s+1 ≤ s*(3/(1-q)) := by
    have hid : s*(3/(1-q)) = 3/2 := by dsimp [s]; field_simp
    rw [hid]
    dsimp [s]
    linarith
  have hece := mul_le_mul_of_nonneg_right hec he
  apply le_of_mul_le_mul_left (a := s) _ hs
  nlinarith only [hy,hx,hz,hcd,hece]

/-- The invariant tube for squared errors; the denominator exposes the roundoff floor. -/
theorem invariant_energy_floor (q e : ℚ) (h1 : q < 1) :
    ((1+q)/2)*(6*e/(1-q)^2) + (3/(1-q))*e = 6*e/(1-q)^2 := by
  have h : 1-q ≠ 0 := ne_of_gt (sub_pos.mpr h1)
  field_simp
  ring

end Komorebi.RoundoffSolver
