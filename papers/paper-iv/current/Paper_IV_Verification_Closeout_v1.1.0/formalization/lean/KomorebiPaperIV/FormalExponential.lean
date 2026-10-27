/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.Data.Nat.Choose.Cast
import Mathlib.RingTheory.PowerSeries.Exp
import Mathlib.RingTheory.PowerSeries.Expand

/-!
# Formal exponential parameter families

For a zero-constant formal logarithm `L`, `formalExpFamily L r` is the
formal series `exp (r L)`.  This is the branch-free algebraic core of the
reciprocal families in Paper IV (where `L = -log Δ_N`).
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

variable {R : Type*} [CommRing R] [Algebra ℚ R]

/-- Formal `exp (r L)`, implemented by substituting `L` into `exp (rX)`. -/
def formalExpFamily (L : R⟦X⟧) (r : R) : R⟦X⟧ :=
  (PowerSeries.rescale r (PowerSeries.exp R)).subst L

theorem formalExpFamily_semigroup {L : R⟦X⟧} (hL : L.constantCoeff = 0) (r s : R) :
    formalExpFamily L r * formalExpFamily L s = formalExpFamily L (r + s) := by
  let hsub : PowerSeries.HasSubst L := PowerSeries.HasSubst.of_constantCoeff_zero' hL
  rw [formalExpFamily, formalExpFamily, formalExpFamily]
  rw [← PowerSeries.subst_mul hsub]
  rw [PowerSeries.exp_mul_exp_eq_exp_add]

theorem formalExpFamily_zero {L : R⟦X⟧} (hL : L.constantCoeff = 0) :
    formalExpFamily L 0 = 1 := by
  rw [formalExpFamily, PowerSeries.rescale_zero_apply]
  let hsub : PowerSeries.HasSubst L := PowerSeries.HasSubst.of_constantCoeff_zero' hL
  rw [PowerSeries.constantCoeff_exp]
  change PowerSeries.subst L (1 : R⟦X⟧) = 1
  rw [← PowerSeries.coe_substAlgHom hsub, map_one]

theorem formalExpFamily_one (L : R⟦X⟧) :
    formalExpFamily L 1 = (PowerSeries.exp R).subst L := by
  rw [formalExpFamily, show PowerSeries.rescale 1 (PowerSeries.exp R) = PowerSeries.exp R by simp]

/-- Formal derivative of `exp (rX)`. -/
theorem derivative_rescale_exp (r : R) :
    PowerSeries.derivative R (PowerSeries.rescale r (PowerSeries.exp R)) =
      PowerSeries.C r * PowerSeries.rescale r (PowerSeries.exp R) := by
  ext n
  rw [PowerSeries.coeff_derivative, PowerSeries.coeff_C_mul]
  simp only [PowerSeries.coeff_rescale, PowerSeries.coeff_exp]
  have hrat :
      algebraMap ℚ R (1 / ((n + 1).factorial : ℚ)) * (n + 1 : R) =
        algebraMap ℚ R (1 / (n.factorial : ℚ)) := by
    have key : (n + 1 : R) = algebraMap ℚ R (n + 1) := by
      rw [map_add, map_natCast, map_one]
    rw [key, ← map_mul]
    congr 1
    rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add_one]
    field_simp
  rw [pow_succ]
  calc
    r ^ n * r * algebraMap ℚ R (1 / ((n + 1).factorial : ℚ)) * (n + 1 : R) =
        r * r ^ n *
          (algebraMap ℚ R (1 / ((n + 1).factorial : ℚ)) * (n + 1 : R)) := by ring
    _ = r * (r ^ n * algebraMap ℚ R (1 / (n.factorial : ℚ))) := by
      rw [hrat]
      ring

/-- Chain rule for the formal reciprocal family. -/
theorem derivative_formalExpFamily {L : R⟦X⟧} (hL : L.constantCoeff = 0) (r : R) :
    PowerSeries.derivative R (formalExpFamily L r) =
      PowerSeries.C r * formalExpFamily L r * PowerSeries.derivative R L := by
  let hsub : PowerSeries.HasSubst L := PowerSeries.HasSubst.of_constantCoeff_zero' hL
  rw [formalExpFamily, PowerSeries.derivative_subst hsub, derivative_rescale_exp]
  rw [PowerSeries.subst_mul hsub, PowerSeries.subst_C]
  simp only [PowerSeries.C_apply]

/-- Newton-type finite coefficient recurrence for `exp (rL)`. -/
theorem formalExpFamily_coefficient_recurrence {L : R⟦X⟧}
    (hL : L.constantCoeff = 0) (r : R) (n : ℕ) :
    (n + 1 : R) * PowerSeries.coeff (n + 1) (formalExpFamily L r) =
      r * ∑ p ∈ Finset.antidiagonal n,
        PowerSeries.coeff p.1 (formalExpFamily L r) *
          ((p.2 + 1 : R) * PowerSeries.coeff (p.2 + 1) L) := by
  have hd : PowerSeries.derivative R (formalExpFamily L r) =
      PowerSeries.C r *
        (formalExpFamily L r * PowerSeries.derivative R L) := by
    simpa only [mul_assoc] using derivative_formalExpFamily hL r
  have h := congrArg (PowerSeries.coeff (R := R) n) hd
  rw [PowerSeries.coeff_derivative, PowerSeries.coeff_C_mul,
    PowerSeries.coeff_mul] at h
  simp_rw [PowerSeries.coeff_derivative] at h
  simpa [mul_assoc, mul_left_comm, mul_comm] using h

/-- Exponential-generating coefficient: `n! [X^n] f`. -/
def egfCoeff (n : ℕ) (f : R⟦X⟧) : R :=
  (n.factorial : R) * PowerSeries.coeff n f

omit [Algebra ℚ R] in
/-- Coefficient multiplication in exponential-generating normalization. -/
theorem egfCoeff_mul (n : ℕ) (f g : R⟦X⟧) :
    egfCoeff n (f * g) =
      ∑ p ∈ Finset.antidiagonal n,
        (n.choose p.1 : R) * egfCoeff p.1 f * egfCoeff p.2 g := by
  rw [egfCoeff, PowerSeries.coeff_mul, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro p hp
  have hpadd : p.1 + p.2 = n := Finset.mem_antidiagonal.mp hp
  have hnat :
      (p.1 + p.2).choose p.1 * p.1.factorial * p.2.factorial =
        (p.1 + p.2).factorial := by
    simpa [Nat.add_comm, Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc] using
      Nat.add_choose_mul_factorial_mul_factorial p.2 p.1
  have hcast :
      (((p.1 + p.2).choose p.1 : ℕ) : R) * (p.1.factorial : R) * (p.2.factorial : R) =
        ((p.1 + p.2).factorial : R) := by
    simpa only [Nat.cast_mul] using congrArg (fun z : ℕ => (z : R)) hnat
  rw [← hpadd]
  rw [egfCoeff, egfCoeff]
  rw [← hcast]
  ring

/-- Paper IV's block normalization `(N n)! [w^n] f`. -/
def blockCoeff (N n : ℕ) (f : R⟦X⟧) : R :=
  ((N * n).factorial : R) * PowerSeries.coeff n f

omit [Algebra ℚ R] in
/-- Cauchy multiplication in the block normalization used by `P_{N,n}`. -/
theorem blockCoeff_mul (N n : ℕ) (f g : R⟦X⟧) :
    blockCoeff N n (f * g) =
      ∑ q ∈ Finset.range (n + 1),
        ((N * n).choose (N * q) : R) * blockCoeff N q f * blockCoeff N (n - q) g := by
  rw [blockCoeff, PowerSeries.coeff_mul]
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro q hq
  have hqn : q ≤ n := Nat.le_of_lt_succ (Finset.mem_range.mp hq)
  have hsum : N * q + N * (n - q) = N * n := by
    rw [← Nat.mul_add, Nat.add_sub_of_le hqn]
  have hnat :
      (N * q + N * (n - q)).choose (N * q) * (N * q).factorial *
          (N * (n - q)).factorial =
        (N * q + N * (n - q)).factorial := by
    simpa [Nat.add_comm, Nat.mul_comm, Nat.mul_left_comm, Nat.mul_assoc] using
      Nat.add_choose_mul_factorial_mul_factorial (N * (n - q)) (N * q)
  have hcast :
      (((N * q + N * (n - q)).choose (N * q) : ℕ) : R) *
          ((N * q).factorial : R) * ((N * (n - q)).factorial : R) =
        ((N * q + N * (n - q)).factorial : R) := by
    simpa only [Nat.cast_mul] using congrArg (fun z : ℕ => (z : R)) hnat
  rw [← hsum]
  rw [blockCoeff, blockCoeff]
  rw [← hcast]
  ring

/-- Exact block coefficient convolution for the reciprocal parameter semigroup. -/
theorem reciprocal_block_convolution {L : R⟦X⟧} (hL : L.constantCoeff = 0)
    (N n : ℕ) (r s : R) :
    blockCoeff N n (formalExpFamily L (r + s)) =
      ∑ q ∈ Finset.range (n + 1),
        ((N * n).choose (N * q) : R) *
          blockCoeff N q (formalExpFamily L r) *
          blockCoeff N (n - q) (formalExpFamily L s) := by
  rw [← formalExpFamily_semigroup hL]
  exact blockCoeff_mul N n _ _

/-- Binomial-type normalization of the same parameter semigroup. -/
theorem reciprocal_binomial_type {L : R⟦X⟧} (hL : L.constantCoeff = 0)
    (n : ℕ) (r s : R) :
    egfCoeff n (formalExpFamily L (r + s)) =
      ∑ p ∈ Finset.antidiagonal n,
        (n.choose p.1 : R) * egfCoeff p.1 (formalExpFamily L r) *
          egfCoeff p.2 (formalExpFamily L s) := by
  rw [← formalExpFamily_semigroup hL]
  exact egfCoeff_mul n _ _

section Field

variable {K : Type*} [Field K]

/-- Triangular inverse identity for any unit-constant formal series. -/
theorem inverse_coefficient_convolution {D : K⟦X⟧} (hD : D.constantCoeff = 1) (n : ℕ) :
    (∑ p ∈ Finset.antidiagonal n,
        PowerSeries.coeff p.1 D * PowerSeries.coeff p.2 D⁻¹) =
      if n = 0 then 1 else 0 := by
  have hunit : D.constantCoeff ≠ 0 := by simp [hD]
  have h := congrArg (PowerSeries.coeff (R := K) n) (PowerSeries.mul_inv_cancel D hunit)
  rw [PowerSeries.coeff_mul] at h
  simpa [PowerSeries.coeff_one] using h

/-- The inverse's constant coefficient remains one. -/
theorem constantCoeff_inverse_of_one {D : K⟦X⟧} (hD : D.constantCoeff = 1) :
    D⁻¹.constantCoeff = 1 := by
  rw [PowerSeries.constantCoeff_inv, hD, inv_one]

end Field

end

end Komorebi.PaperIV
