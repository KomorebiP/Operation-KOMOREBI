/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.ReciprocalCore
import Mathlib.Data.Nat.Choose.Cast
import Mathlib.Algebra.Polynomial.Eval.Defs

/-!
# Reciprocal and tangent completion certificates

This file strengthens the branch-free algebraic coverage of Sections 7 and 8
of Paper IV.  All identities are formal-power-series identities.  In
particular, the higher Riccati theorem below uses a recursively defined
complete differential Bell polynomial and does not appeal to pointwise
division or to an analytic logarithm branch.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

section ParameterRecurrence

variable {R : Type*} [CommRing R] [Algebra ℚ R]

/-- The denominator times the derivative of its reciprocal parameter family
satisfies the exact logarithmic-differentiation equation. -/
theorem reducedDenominator_reciprocalSeries_differentialEquation
    (N : ℕ) (r : R) :
    reducedDenominator N * PowerSeries.derivative R (reciprocalSeries N r) +
        PowerSeries.C r *
          (PowerSeries.derivative R (reducedDenominator N) *
            reciprocalSeries N r) = 0 := by
  rw [derivative_reciprocalSeries]
  have hlog := reducedDenominator_mul_reducedTangentSeries (R := R) N
  rw [reducedTangentSeries] at hlog
  calc
    reducedDenominator N *
          (PowerSeries.C r * reciprocalSeries N r *
            PowerSeries.derivative R (negativeLogDenominator N)) +
        PowerSeries.C r *
          (PowerSeries.derivative R (reducedDenominator N) *
            reciprocalSeries N r) =
        PowerSeries.C r * reciprocalSeries N r *
          (reducedDenominator N *
            PowerSeries.derivative R (negativeLogDenominator N)) +
        PowerSeries.C r * reciprocalSeries N r *
          PowerSeries.derivative R (reducedDenominator N) := by ring
    _ = 0 := by rw [hlog]; ring

/-- Coefficient form of the parameter recurrence before factorial
rescaling.  Multiplying this identity by `N (N(n+1)-1)!` gives the two
binomial sums displayed in Theorem 7.3. -/
theorem reciprocalOrdCoeff_parameter_equation (N n : ℕ) (r : R) :
    (∑ p ∈ Finset.antidiagonal n,
        PowerSeries.coeff p.1 (reducedDenominator (R := R) N) *
          ((p.2 + 1 : R) * reciprocalOrdCoeff N (p.2 + 1) r)) +
      r * ∑ p ∈ Finset.antidiagonal n,
        ((p.1 + 1 : R) *
          PowerSeries.coeff (p.1 + 1) (reducedDenominator (R := R) N)) *
            reciprocalOrdCoeff N p.2 r = 0 := by
  have h := congrArg (PowerSeries.coeff (R := R) n)
    (reducedDenominator_reciprocalSeries_differentialEquation (R := R) N r)
  rw [map_add, PowerSeries.coeff_mul, PowerSeries.coeff_C_mul,
    PowerSeries.coeff_mul] at h
  simp only [map_zero] at h
  simp_rw [PowerSeries.coeff_derivative] at h
  simpa [reciprocalOrdCoeff, mul_assoc, mul_left_comm, mul_comm] using h

end ParameterRecurrence

section ExactParameterRecurrence

variable {K : Type*} [Field K] [CharZero K]

private theorem scaled_reducedDenominator_term
    {N n k : ℕ} (hN : 0 < N) (hk : k < n) :
    (((N * n - 1).factorial : K) * (N : K)) *
        (PowerSeries.coeff k (reducedDenominator (R := K) N) *
          (n - k : K)) =
      (-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
        ((N * (n - k)).factorial : K) := by
  have hkn : k ≤ n := Nat.le_of_lt hk
  have hNkn : 0 < N * (n - k) := Nat.mul_pos hN (Nat.sub_pos_of_lt hk)
  have hmul_lt : N * k < N * n := (Nat.mul_lt_mul_left hN).2 hk
  have hmul_le : N * k ≤ N * n := Nat.le_of_lt hmul_lt
  have hchoose : N * k ≤ N * n - 1 := by omega
  have hsub : N * n - 1 - N * k = N * (n - k) - 1 := by
    rw [Nat.mul_sub_left_distrib]
    omega
  have hfac :
      ((N * (n - k)).factorial : K) =
        (N * (n - k) : K) * ((N * (n - k) - 1).factorial : K) := by
    exact_mod_cast (Nat.mul_factorial_pred hNkn.ne').symm
  have hfacNk : ((N * k).factorial : K) ≠ 0 := by
    exact_mod_cast (N * k).factorial_pos.ne'
  have hfacRest : ((N * (n - k) - 1).factorial : K) ≠ 0 := by
    exact_mod_cast (N * (n - k) - 1).factorial_pos.ne'
  rw [coeff_reducedDenominator]
  rw [eq_ratCast]
  push_cast
  have hsign : ((↑((-1 : ℚ) ^ k) : K)) = (-1 : K) ^ k := by norm_cast
  rw [hsign]
  rw [Nat.cast_choose K hchoose, hsub, hfac]
  field_simp [hfacNk, hfacRest]

private theorem scaled_derivative_reducedDenominator_term
    {N n k : ℕ} (hN : 0 < N) (hk : 0 < k) (hkn : k ≤ n) :
    (((N * n - 1).factorial : K) * (N : K)) *
        ((k : K) *
          PowerSeries.coeff k (reducedDenominator (R := K) N)) =
      (-1 : K) ^ k * ((N * n - 1).choose (N * k - 1) : K) *
        ((N * (n - k)).factorial : K) := by
  have hNk : 0 < N * k := Nat.mul_pos hN hk
  have hmul_le : N * k ≤ N * n := Nat.mul_le_mul_left N hkn
  have hchoose : N * k - 1 ≤ N * n - 1 := by omega
  have hsub : N * n - 1 - (N * k - 1) = N * (n - k) := by
    rw [Nat.mul_sub_left_distrib]
    omega
  have hfac :
      ((N * k).factorial : K) =
        (N * k : K) * ((N * k - 1).factorial : K) := by
    exact_mod_cast (Nat.mul_factorial_pred hNk.ne').symm
  have hfacNk : ((N * k).factorial : K) ≠ 0 := by
    exact_mod_cast (N * k).factorial_pos.ne'
  have hfacPred : ((N * k - 1).factorial : K) ≠ 0 := by
    exact_mod_cast (N * k - 1).factorial_pos.ne'
  have hfacRest : ((N * (n - k)).factorial : K) ≠ 0 := by
    exact_mod_cast (N * (n - k)).factorial_pos.ne'
  have hN0 : (N : K) ≠ 0 := by exact_mod_cast hN.ne'
  have hk0 : (k : K) ≠ 0 := by exact_mod_cast hk.ne'
  rw [coeff_reducedDenominator]
  rw [eq_ratCast]
  push_cast
  have hsign : ((↑((-1 : ℚ) ^ k) : K)) = (-1 : K) ^ k := by norm_cast
  rw [hsign]
  rw [Nat.cast_choose K hchoose, hsub, hfac]
  field_simp [hfacNk, hfacPred, hfacRest, hN0, hk0]

private theorem scaled_reciprocalOrdCoeff_term
    {N n k : ℕ} (hN : 0 < N) (hk : k < n) (r : K) :
    (((N * n - 1).factorial : K) * (N : K)) *
        (PowerSeries.coeff k (reducedDenominator (R := K) N) *
          ((n - k : K) * reciprocalOrdCoeff N (n - k) r)) =
      (-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
        reciprocalCoeff N (n - k) r := by
  rw [reciprocalCoeff, blockCoeff, reciprocalOrdCoeff]
  have hs := scaled_reducedDenominator_term (K := K) hN hk
  calc
    (((N * n - 1).factorial : K) * (N : K)) *
        (PowerSeries.coeff k (reducedDenominator (R := K) N) *
          ((n - k : K) *
            PowerSeries.coeff (n - k) (reciprocalSeries N r))) =
      ((((N * n - 1).factorial : K) * (N : K)) *
        (PowerSeries.coeff k (reducedDenominator (R := K) N) *
          (n - k : K))) *
            PowerSeries.coeff (n - k) (reciprocalSeries N r) := by ring
    _ = ((-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
        ((N * (n - k)).factorial : K)) *
          PowerSeries.coeff (n - k) (reciprocalSeries N r) := by rw [hs]
    _ = (-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
        (((N * (n - k)).factorial : K) *
          PowerSeries.coeff (n - k) (reciprocalSeries N r)) := by ring

private theorem scaled_derivative_reciprocalOrdCoeff_term
    {N n k : ℕ} (hN : 0 < N) (hk : 0 < k) (hkn : k ≤ n) (r : K) :
    (((N * n - 1).factorial : K) * (N : K)) *
        (((k : K) *
          PowerSeries.coeff k (reducedDenominator (R := K) N)) *
            reciprocalOrdCoeff N (n - k) r) =
      (-1 : K) ^ k * ((N * n - 1).choose (N * k - 1) : K) *
        reciprocalCoeff N (n - k) r := by
  rw [reciprocalCoeff, blockCoeff, reciprocalOrdCoeff]
  have hs := scaled_derivative_reducedDenominator_term (K := K) hN hk hkn
  calc
    (((N * n - 1).factorial : K) * (N : K)) *
        (((k : K) *
          PowerSeries.coeff k (reducedDenominator (R := K) N)) *
            PowerSeries.coeff (n - k) (reciprocalSeries N r)) =
      ((((N * n - 1).factorial : K) * (N : K)) *
        ((k : K) *
          PowerSeries.coeff k (reducedDenominator (R := K) N))) *
            PowerSeries.coeff (n - k) (reciprocalSeries N r) := by ring
    _ = ((-1 : K) ^ k * ((N * n - 1).choose (N * k - 1) : K) *
        ((N * (n - k)).factorial : K)) *
          PowerSeries.coeff (n - k) (reciprocalSeries N r) := by rw [hs]
    _ = (-1 : K) ^ k * ((N * n - 1).choose (N * k - 1) : K) *
        (((N * (n - k)).factorial : K) *
          PowerSeries.coeff (n - k) (reciprocalSeries N r)) := by ring

/-- Exact factorially normalized coefficient equation behind Theorem 7.3.
The second sum uses the reindexing `k = q + 1`, so all displayed indices are
total natural-number expressions. -/
theorem reciprocalCoeff_parameter_equation
    {N n : ℕ} (hN : 0 < N) (hn : 0 < n) (r : K) :
    (∑ k ∈ Finset.range n,
        (-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
          reciprocalCoeff N (n - k) r) +
      r * ∑ q ∈ Finset.range n,
        (-1 : K) ^ (q + 1) *
          ((N * n - 1).choose (N * (q + 1) - 1) : K) *
            reciprocalCoeff N (n - (q + 1)) r = 0 := by
  have hraw := reciprocalOrdCoeff_parameter_equation (R := K) N (n - 1) r
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk,
    Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at hraw
  simp only [Nat.succ_eq_add_one] at hraw
  have hpred : n - 1 + 1 = n := Nat.sub_add_cancel (Nat.one_le_iff_ne_zero.mpr hn.ne')
  have hfirst :
      (∑ k ∈ Finset.range n,
          PowerSeries.coeff k (reducedDenominator (R := K) N) *
            ((n - k : K) * reciprocalOrdCoeff N (n - k) r)) =
        ∑ k ∈ Finset.range (n - 1 + 1),
          PowerSeries.coeff k (reducedDenominator (R := K) N) *
            ((((n - 1 - k : ℕ) : K) + 1) *
              reciprocalOrdCoeff N (n - 1 - k + 1) r) := by
    rw [hpred]
    apply Finset.sum_congr rfl
    intro k hk
    have hklt : k < n := Finset.mem_range.mp hk
    have hidx : n - 1 - k + 1 = n - k := by omega
    have hcast : (((n - 1 - k : ℕ) : K) + 1) = (n - k : K) := by
      have hc := congrArg (fun m : ℕ => (m : K)) hidx
      simpa only [Nat.cast_add, Nat.cast_one,
        Nat.cast_sub (Nat.le_of_lt hklt)] using hc
    rw [hcast, hidx]
  have hsecond :
      (∑ q ∈ Finset.range n,
          ((q + 1 : K) *
            PowerSeries.coeff (q + 1) (reducedDenominator (R := K) N)) *
              reciprocalOrdCoeff N (n - (q + 1)) r) =
        ∑ q ∈ Finset.range (n - 1 + 1),
          ((q + 1 : K) *
            PowerSeries.coeff (q + 1) (reducedDenominator (R := K) N)) *
              reciprocalOrdCoeff N (n - 1 - q) r := by
    rw [hpred]
    apply Finset.sum_congr rfl
    intro q hq
    have hqlt : q < n := Finset.mem_range.mp hq
    have hidx : n - 1 - q = n - (q + 1) := by omega
    rw [hidx]
  rw [← hfirst, ← hsecond] at hraw
  let scale : K := ((N * n - 1).factorial : K) * (N : K)
  have hscaled :
      scale *
        ((∑ k ∈ Finset.range n,
            PowerSeries.coeff k (reducedDenominator (R := K) N) *
              ((n - k : K) * reciprocalOrdCoeff N (n - k) r)) +
          r * ∑ q ∈ Finset.range n,
            ((q + 1 : K) *
              PowerSeries.coeff (q + 1) (reducedDenominator (R := K) N)) *
                reciprocalOrdCoeff N (n - (q + 1)) r) = 0 := by
    rw [hraw, mul_zero]
  have hfirstScaled :
      scale *
          (∑ k ∈ Finset.range n,
            PowerSeries.coeff k (reducedDenominator (R := K) N) *
              ((n - k : K) * reciprocalOrdCoeff N (n - k) r)) =
        ∑ k ∈ Finset.range n,
          (-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
            reciprocalCoeff N (n - k) r := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k hk
    exact scaled_reciprocalOrdCoeff_term (K := K) hN (Finset.mem_range.mp hk) r
  have hsecondScaled :
      scale *
          (∑ q ∈ Finset.range n,
            ((q + 1 : K) *
              PowerSeries.coeff (q + 1) (reducedDenominator (R := K) N)) *
                reciprocalOrdCoeff N (n - (q + 1)) r) =
        ∑ q ∈ Finset.range n,
          (-1 : K) ^ (q + 1) *
            ((N * n - 1).choose (N * (q + 1) - 1) : K) *
              reciprocalCoeff N (n - (q + 1)) r := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro q hq
    have hqlt : q < n := Finset.mem_range.mp hq
    simpa [scale, Nat.succ_eq_add_one] using
      (scaled_derivative_reciprocalOrdCoeff_term
        (K := K) hN (Nat.zero_lt_succ q) (Nat.succ_le_iff.mpr hqlt) r)
  calc
    (∑ k ∈ Finset.range n,
        (-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
          reciprocalCoeff N (n - k) r) +
      r * ∑ q ∈ Finset.range n,
        (-1 : K) ^ (q + 1) *
          ((N * n - 1).choose (N * (q + 1) - 1) : K) *
            reciprocalCoeff N (n - (q + 1)) r =
      scale *
        ((∑ k ∈ Finset.range n,
            PowerSeries.coeff k (reducedDenominator (R := K) N) *
              ((n - k : K) * reciprocalOrdCoeff N (n - k) r)) +
          r * ∑ q ∈ Finset.range n,
            ((q + 1 : K) *
              PowerSeries.coeff (q + 1) (reducedDenominator (R := K) N)) *
                reciprocalOrdCoeff N (n - (q + 1)) r) := by
        rw [mul_add, hfirstScaled]
        rw [show scale *
            (r * ∑ q ∈ Finset.range n,
              ((q + 1 : K) *
                PowerSeries.coeff (q + 1) (reducedDenominator (R := K) N)) *
                  reciprocalOrdCoeff N (n - (q + 1)) r) =
            r * (scale * ∑ q ∈ Finset.range n,
              ((q + 1 : K) *
                PowerSeries.coeff (q + 1) (reducedDenominator (R := K) N)) *
                  reciprocalOrdCoeff N (n - (q + 1)) r) by ring,
          hsecondScaled]
    _ = 0 := hscaled

/-- The solved parameter recurrence, exactly matching Theorem 7.3 after the
harmless reindexing `k = q + 1` in the second finite sum. -/
theorem reciprocalCoeff_parameter_recurrence
    {N n : ℕ} (hN : 0 < N) (hn : 0 < n) (r : K) :
    reciprocalCoeff N n r =
      -(∑ k ∈ Finset.Ico 1 n,
          (-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
            reciprocalCoeff N (n - k) r) -
      r * ∑ q ∈ Finset.range n,
        (-1 : K) ^ (q + 1) *
          ((N * n - 1).choose (N * (q + 1) - 1) : K) *
            reciprocalCoeff N (n - (q + 1)) r := by
  let f : ℕ → K := fun k =>
    (-1 : K) ^ k * ((N * n - 1).choose (N * k) : K) *
      reciprocalCoeff N (n - k) r
  have hsplit :
      (∑ k ∈ Finset.range n, f k) =
        reciprocalCoeff N n r + ∑ k ∈ Finset.Ico 1 n, f k := by
    have hi := Finset.sum_Ico_eq_sub f (show 1 ≤ n by omega)
    simp only [Finset.sum_range_one] at hi
    have hf0 : f 0 = reciprocalCoeff N n r := by simp [f]
    rw [hi, hf0]
    ring
  have h := reciprocalCoeff_parameter_equation (K := K) hN hn r
  change (∑ k ∈ Finset.range n, f k) + _ = 0 at h
  rw [hsplit] at h
  change reciprocalCoeff N n r =
      -(∑ k ∈ Finset.Ico 1 n, f k) - _
  linear_combination h

@[simp]
theorem reciprocalCoeff_block_zero (N : ℕ) (r : K) :
    reciprocalCoeff N 0 r = 1 := by
  simp [reciprocalCoeff, blockCoeff]

/-- The first reciprocal polynomial: `P_(N,1)(r) = r`. -/
theorem reciprocalCoeff_one {N : ℕ} (hN : 0 < N) (r : K) :
    reciprocalCoeff N 1 r = r := by
  have h := reciprocalCoeff_parameter_recurrence
    (K := K) hN (n := 1) (by omega) r
  simpa using h

/-- A recurrence-normal-form certificate for the second reciprocal
polynomial.  The two adjacent binomial coefficients combine to the compact
formula printed in Corollary 7.7. -/
theorem reciprocalCoeff_two_recurrence_form
    {N : ℕ} (hN : 0 < N) (r : K) :
    reciprocalCoeff N 2 r =
      ((2 * N - 1).choose N : K) * r +
        r * (((2 * N - 1).choose (N - 1) : K) * r - 1) := by
  have h := reciprocalCoeff_parameter_recurrence
    (K := K) hN (n := 2) (by omega) r
  norm_num [Finset.sum_range_succ, Finset.sum_Ico_eq_sub,
    reciprocalCoeff_one hN] at h
  rw [Nat.mul_comm N 2] at h
  linear_combination h

/-- A recurrence-normal-form certificate for the third reciprocal
polynomial.  Substitution of the preceding second-degree formula and the
standard adjacent-binomial identities yields the compact form in
Corollary 7.7. -/
theorem reciprocalCoeff_three_recurrence_form
    {N : ℕ} (hN : 0 < N) (r : K) :
    reciprocalCoeff N 3 r =
      ((3 * N - 1).choose N : K) * reciprocalCoeff N 2 r -
        ((3 * N - 1).choose (2 * N) : K) * r +
      r * (((3 * N - 1).choose (N - 1) : K) * reciprocalCoeff N 2 r -
        ((3 * N - 1).choose (2 * N - 1) : K) * r + 1) := by
  have h := reciprocalCoeff_parameter_recurrence
    (K := K) hN (n := 3) (by omega) r
  norm_num [Finset.sum_range_succ, Finset.sum_Ico_eq_sub,
    reciprocalCoeff_one hN] at h
  rw [Nat.mul_comm N 3, Nat.mul_comm N 2] at h
  linear_combination h

end ExactParameterRecurrence

section PolynomialFactor

/-- The universal reciprocal coefficient obtained by taking the parameter to
be the indeterminate `X` over `ℚ`.  This is a literal polynomial lift of
`P_(N,n)(r)`, not merely a function-valued surrogate. -/
def reciprocalCoeffPolynomial (N n : ℕ) : Polynomial ℚ :=
  reciprocalCoeff (R := Polynomial ℚ) N n Polynomial.X

/-- Corollary 7.8 in the universal polynomial ring: every positive-index
reciprocal coefficient has the factor `X`. -/
theorem X_dvd_reciprocalCoeffPolynomial
    (N : ℕ) {n : ℕ} (hn : 0 < n) :
    Polynomial.X ∣ reciprocalCoeffPolynomial N n := by
  have hpred : n - 1 + 1 = n := Nat.sub_add_cancel (Nat.one_le_iff_ne_zero.mpr hn.ne')
  have hnewton := reciprocalOrdCoeff_newton
    (R := Polynomial ℚ) N Polynomial.X (n - 1)
  have hcast : (((n - 1 : ℕ) : Polynomial ℚ) + 1) =
      (n : Polynomial ℚ) := by
    have hc := congrArg (fun m : ℕ => (m : Polynomial ℚ)) hpred
    simpa only [Nat.cast_add, Nat.cast_one] using hc
  rw [hpred, hcast] at hnewton
  have hdivScaled :
      Polynomial.X ∣ (n : Polynomial ℚ) *
        reciprocalOrdCoeff N n Polynomial.X := by
    rw [hnewton]
    exact dvd_mul_right Polynomial.X _
  have hnq : (n : ℚ) ≠ 0 := by exact_mod_cast hn.ne'
  have huq : IsUnit (n : ℚ) := isUnit_iff_ne_zero.mpr hnq
  have hu : IsUnit (n : Polynomial ℚ) := by
    change IsUnit (Polynomial.C (n : ℚ))
    exact huq.map Polynomial.C
  have hcoeff :
      Polynomial.X ∣ reciprocalOrdCoeff N n Polynomial.X :=
    hu.dvd_mul_left.mp hdivScaled
  rw [reciprocalCoeffPolynomial, reciprocalCoeff, blockCoeff]
  exact dvd_mul_of_dvd_right hcoeff _

/-- Equivalent root-at-zero certificate for the universal polynomial. -/
theorem coeff_zero_reciprocalCoeffPolynomial
    (N : ℕ) {n : ℕ} (hn : 0 < n) :
    (reciprocalCoeffPolynomial N n).coeff 0 = 0 := by
  exact Polynomial.X_dvd_iff.mp
    (X_dvd_reciprocalCoeffPolynomial N hn)

end PolynomialFactor

section TransferTangent

variable {R : Type*} [CommRing R] [Algebra ℚ R]

/-- The manuscript's factorially normalized `z`-variable tangent
coefficient `T_N(n)`. -/
def transferTangentCoeff (N n : ℕ) : R :=
  (N : R) * ((N * n + N - 1).factorial : R) * kappaCoeff N (n + 1)

/-- Exact named form of Proposition 8.2. -/
theorem transferTangentCoeff_eq_kappa (N n : ℕ) :
    transferTangentCoeff (R := R) N n =
      (N : R) * ((N * n + N - 1).factorial : R) * kappaCoeff N (n + 1) := by
  rfl

section Field

variable {K : Type*} [Field K] [CharZero K]

private theorem scaled_tangent_convolution_term
    {N n k : ℕ} (hN : 0 < N) (hk : k ≤ n) :
    ((N : K) * ((N * n + N - 1).factorial : K)) *
        (PowerSeries.coeff k (reducedDenominator (R := K) N) *
          kappaCoeff N (n - k + 1)) =
      (-1 : K) ^ k *
        ((N * n + N - 1).choose (N * k) : K) *
          transferTangentCoeff N (n - k) := by
  have hmul : N * k ≤ N * n := Nat.mul_le_mul_left N hk
  have hchoose : N * k ≤ N * n + N - 1 := by omega
  have hsub :
      N * n + N - 1 - N * k = N * (n - k) + N - 1 := by
    rw [Nat.mul_sub_left_distrib]
    omega
  have hfacK : ((N * k).factorial : K) ≠ 0 := by
    exact_mod_cast (N * k).factorial_pos.ne'
  have hfacRest : ((N * (n - k) + N - 1).factorial : K) ≠ 0 := by
    exact_mod_cast (N * (n - k) + N - 1).factorial_pos.ne'
  rw [coeff_reducedDenominator, eq_ratCast]
  push_cast
  have hsign : ((↑((-1 : ℚ) ^ k) : K)) = (-1 : K) ^ k := by norm_cast
  rw [hsign, Nat.cast_choose K hchoose, hsub]
  rw [transferTangentCoeff]
  field_simp [hfacK, hfacRest]

private theorem scaled_tangent_convolution_rhs
    (N n : ℕ) (hN : 0 < N) :
    ((N : K) * ((N * n + N - 1).factorial : K)) *
        (-(PowerSeries.coeff (n + 1) (reducedDenominator (R := K) N) *
          (n + 1 : K))) = (-1 : K) ^ n := by
  have hpos : 0 < N * (n + 1) := Nat.mul_pos hN (Nat.succ_pos n)
  have htop : N * n + N - 1 = N * (n + 1) - 1 := by
    rw [Nat.mul_add, Nat.mul_one]
  have hfac :
      ((N * (n + 1)).factorial : K) =
        (N * (n + 1) : K) * ((N * (n + 1) - 1).factorial : K) := by
    exact_mod_cast (Nat.mul_factorial_pred hpos.ne').symm
  have hfacTop : ((N * (n + 1) - 1).factorial : K) ≠ 0 := by
    exact_mod_cast (N * (n + 1) - 1).factorial_pos.ne'
  have hN0 : (N : K) ≠ 0 := by exact_mod_cast hN.ne'
  have hn0 : (n + 1 : K) ≠ 0 := by
    exact_mod_cast (Nat.succ_ne_zero n)
  rw [coeff_reducedDenominator, eq_ratCast]
  push_cast
  have hsign : ((↑((-1 : ℚ) ^ (n + 1)) : K)) =
      (-1 : K) ^ (n + 1) := by norm_cast
  rw [hsign, htop, hfac]
  field_simp [hfacTop, hN0, hn0]
  rw [pow_succ]
  ring

/-- Fully normalized convolution equation for the named `z`-variable tangent
coefficients. -/
theorem transferTangentCoeff_convolution
    (N n : ℕ) (hN : 0 < N) :
    (∑ k ∈ Finset.range (n + 1),
        (-1 : K) ^ k *
          ((N * n + N - 1).choose (N * k) : K) *
            transferTangentCoeff N (n - k)) = (-1 : K) ^ n := by
  have hraw := reducedTangent_coefficient_convolution (R := K) N n
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk] at hraw
  let scale : K := (N : K) * ((N * n + N - 1).factorial : K)
  have hscaled := congrArg (fun x : K => scale * x) hraw
  have hleft :
      scale *
          (∑ k ∈ Finset.range (n + 1),
            PowerSeries.coeff k (reducedDenominator (R := K) N) *
              kappaCoeff N (n - k + 1)) =
        ∑ k ∈ Finset.range (n + 1),
          (-1 : K) ^ k *
            ((N * n + N - 1).choose (N * k) : K) *
              transferTangentCoeff N (n - k) := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k hk
    exact scaled_tangent_convolution_term
      (K := K) hN (Nat.le_of_lt_succ (Finset.mem_range.mp hk))
  rw [hleft, scaled_tangent_convolution_rhs (K := K) N n hN] at hscaled
  exact hscaled

/-- The exact tangent recurrence of Theorem 8.3. -/
theorem transferTangentCoeff_recurrence
    (N n : ℕ) (hN : 0 < N) :
    transferTangentCoeff (R := K) N n =
      (-1 : K) ^ n -
        ∑ k ∈ Finset.Ico 1 (n + 1),
          (-1 : K) ^ k *
            ((N * n + N - 1).choose (N * k) : K) *
              transferTangentCoeff N (n - k) := by
  let f : ℕ → K := fun k =>
    (-1 : K) ^ k *
      ((N * n + N - 1).choose (N * k) : K) *
        transferTangentCoeff N (n - k)
  have hsplit :
      (∑ k ∈ Finset.range (n + 1), f k) =
        transferTangentCoeff N n + ∑ k ∈ Finset.Ico 1 (n + 1), f k := by
    have hi := Finset.sum_Ico_eq_sub f (show 1 ≤ n + 1 by omega)
    simp only [Finset.sum_range_one] at hi
    have hf0 : f 0 = transferTangentCoeff N n := by simp [f]
    rw [hi, hf0]
    ring
  have h := transferTangentCoeff_convolution (K := K) N n hN
  change (∑ k ∈ Finset.range (n + 1), f k) = (-1 : K) ^ n at h
  rw [hsplit] at h
  change transferTangentCoeff N n =
      (-1 : K) ^ n - ∑ k ∈ Finset.Ico 1 (n + 1), f k
  linear_combination h

@[simp]
theorem transferTangentCoeff_zero (N : ℕ) (hN : 0 < N) :
    transferTangentCoeff (R := K) N 0 = 1 := by
  simpa using transferTangentCoeff_recurrence (K := K) N 0 hN

end Field

end TransferTangent

section FormalRiccati

variable {K : Type*} [Field K] [CharZero K]

/-- Formal transfer tangent `-D_N'/D_N` in the full `z` variable. -/
def formalTransferTangent (N : ℕ) : K⟦X⟧ :=
  -PowerSeries.derivative K (signedSection (R := K) N 0) *
    (signedSection (R := K) N 0)⁻¹

/-- The complete differential Bell polynomial evaluated at the successive
derivatives of a single logarithmic derivative.  Recursively,
`Y_0 = 1` and `Y_(n+1) = Y_n' + g Y_n`. -/
def differentialBellSeries (g : K⟦X⟧) : ℕ → K⟦X⟧
  | 0 => 1
  | n + 1 =>
      PowerSeries.derivative K (differentialBellSeries g n) +
        g * differentialBellSeries g n

omit [CharZero K] in
@[simp]
theorem differentialBellSeries_zero (g : K⟦X⟧) :
    differentialBellSeries g 0 = 1 := rfl

omit [CharZero K] in
@[simp]
theorem differentialBellSeries_succ (g : K⟦X⟧) (n : ℕ) :
    differentialBellSeries g (n + 1) =
      PowerSeries.derivative K (differentialBellSeries g n) +
        g * differentialBellSeries g n := rfl

omit [CharZero K] in
/-- Recursive differential Bell polynomials encode every iterated derivative
of a formal series satisfying `f' = g f`. -/
theorem iterate_derivative_eq_differentialBellSeries_mul
    (f g : K⟦X⟧)
    (hfg : PowerSeries.derivative K f = g * f) (n : ℕ) :
    (PowerSeries.derivative K)^[n] f = differentialBellSeries g n * f := by
  induction n with
  | zero => simp
  | succ n ih =>
      rw [Function.iterate_succ_apply', ih, Derivation.leibniz, hfg]
      simp only [smul_eq_mul]
      rw [differentialBellSeries_succ]
      ring

/-- The formal tangent is exactly the negative logarithmic derivative: this
version avoids any analytic choice of logarithm. -/
theorem derivative_signedSection_zero_eq_neg_formalTransferTangent_mul
    {N : ℕ} (hN : 0 < N) :
    PowerSeries.derivative K (signedSection (R := K) N 0) =
      -formalTransferTangent N * signedSection (R := K) N 0 := by
  have hconst :
      PowerSeries.constantCoeff (signedSection (R := K) N 0) = 1 := by
    simpa using
      (constantCoeff_iterate_derivative_signedSection
        (R := K) (j := 0) (k := 0) hN hN)
  have hunit :
      PowerSeries.constantCoeff (signedSection (R := K) N 0) ≠ 0 := by
    simp [hconst]
  rw [formalTransferTangent]
  simp only [neg_mul, neg_neg]
  rw [mul_assoc, PowerSeries.inv_mul_cancel _ hunit, mul_one]

/-- Formal scalar higher Riccati identity (Theorem 8.5).  It is the exact
power-series analogue of
`Y_N(-T,-T',..., -T^(N-1)) = -1`. -/
theorem differentialBellSeries_neg_formalTransferTangent_eq_neg_one
    {N : ℕ} (hN : 0 < N) :
    differentialBellSeries (-formalTransferTangent (K := K) N) N = -1 := by
  let D : K⟦X⟧ := signedSection (R := K) N 0
  have hconst : D.constantCoeff = 1 := by
    simpa [D] using
      (constantCoeff_iterate_derivative_signedSection
        (R := K) (j := 0) (k := 0) hN hN)
  have hD : D ≠ 0 := by
    intro hzero
    rw [hzero, map_zero] at hconst
    exact zero_ne_one hconst
  have hbell := iterate_derivative_eq_differentialBellSeries_mul
    D (-formalTransferTangent (K := K) N)
      (by
        simpa [D] using
          (derivative_signedSection_zero_eq_neg_formalTransferTangent_mul
            (K := K) hN)) N
  have hcycle := iterate_derivative_signedSection (R := K) (j := 0) hN
  rw [show D = signedSection (R := K) N 0 by rfl, hcycle] at hbell
  apply mul_right_cancel₀ hD
  simpa [D, mul_assoc] using hbell.symm

end FormalRiccati

end

end Komorebi.PaperIV
