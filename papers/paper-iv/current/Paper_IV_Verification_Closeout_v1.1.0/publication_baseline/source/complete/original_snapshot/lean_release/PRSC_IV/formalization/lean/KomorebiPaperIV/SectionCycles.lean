/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import Mathlib.RingTheory.PowerSeries.Exp

/-!
# Formal transfer and signed exponential sections

This file isolates the exponential-generating coefficient sequences behind
Paper IV's transfer sections `E_{N,j}` and signed sections `D_{N,j}`.  The
derivative cycles are proved as identities of formal power series, including
the minus sign at the signed wraparound.  There are no convergence hypotheses.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

variable {R : Type*} [CommRing R] [Algebra ℚ R]

/-- Realize a coefficient sequence as its exponential generating series. -/
def exponentialGeneratingSeries (a : ℕ → R) : R⟦X⟧ :=
  PowerSeries.mk fun n =>
    a n * algebraMap ℚ R (1 / (n.factorial : ℚ))

@[simp]
theorem coeff_exponentialGeneratingSeries (a : ℕ → R) (n : ℕ) :
    PowerSeries.coeff n (exponentialGeneratingSeries a) =
      a n * algebraMap ℚ R (1 / (n.factorial : ℚ)) := by
  simp [exponentialGeneratingSeries]

/-- Formal differentiation shifts exponential-generating coefficients. -/
theorem derivative_exponentialGeneratingSeries (a : ℕ → R) :
    PowerSeries.derivative R (exponentialGeneratingSeries a) =
      exponentialGeneratingSeries (fun n => a (n + 1)) := by
  ext n
  rw [PowerSeries.coeff_derivative]
  simp only [coeff_exponentialGeneratingSeries]
  have hfac :
      algebraMap ℚ R (1 / ((n + 1).factorial : ℚ)) * (n + 1 : R) =
        algebraMap ℚ R (1 / (n.factorial : ℚ)) := by
    have hn : (n + 1 : R) = algebraMap ℚ R (n + 1) := by
      rw [map_add, map_natCast, map_one]
    rw [hn, ← map_mul]
    congr 1
    rw [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add_one]
    field_simp
  rw [mul_assoc, hfac]

/-- Repeated formal differentiation shifts EGF coefficients by the same amount. -/
theorem iterate_derivative_exponentialGeneratingSeries (a : ℕ → R) (k : ℕ) :
    (PowerSeries.derivative R)^[k] (exponentialGeneratingSeries a) =
      exponentialGeneratingSeries (fun n => a (n + k)) := by
  induction k with
  | zero => simp
  | succ k ih =>
      rw [Function.iterate_succ_apply', ih, derivative_exponentialGeneratingSeries]
      apply congrArg exponentialGeneratingSeries
      funext n
      congr 1
      omega

/-- Exponential-generating coefficients of the transfer section `E_{N,j}(λz)`. -/
def transferSectionCoeff (N j : ℕ) (lambda : R) (n : ℕ) : R :=
  if n % N = j then lambda ^ n else 0

/-- Formal transfer section `E_{N,j}(λX)`. -/
def transferSection (N j : ℕ) (lambda : R) : R⟦X⟧ :=
  exponentialGeneratingSeries (transferSectionCoeff N j lambda)

@[simp]
theorem coeff_transferSection (N j n : ℕ) (lambda : R) :
    PowerSeries.coeff n (transferSection N j lambda) =
      transferSectionCoeff N j lambda n *
        algebraMap ℚ R (1 / (n.factorial : ℚ)) := by
  simp [transferSection]

omit [Algebra ℚ R] in
/-- Away from the wraparound, transfer coefficients shift by one and gain `λ`. -/
theorem transferSectionCoeff_succ_of_pos {N j : ℕ} (hN : 0 < N)
    (hj : 0 < j) (hjN : j < N) (lambda : R) (n : ℕ) :
    transferSectionCoeff N j lambda (n + 1) =
      lambda * transferSectionCoeff N (j - 1) lambda n := by
  unfold transferSectionCoeff
  have hnmod : n % N < N := Nat.mod_lt n hN
  have hstep : (n + 1) % N = (n % N + 1) % N :=
    (Nat.mod_add_mod n N 1).symm
  by_cases h : n % N = j - 1
  · have hlt : n % N + 1 < N := by omega
    have hs : (n + 1) % N = j := by
      rw [hstep, Nat.mod_eq_of_lt hlt]
      omega
    simp only [hs, h, ite_true]
    rw [pow_succ']
  · have hs : (n + 1) % N ≠ j := by
      intro hs
      apply h
      by_cases hlt : n % N + 1 < N
      · have heq : (n + 1) % N = n % N + 1 := by
          rw [hstep, Nat.mod_eq_of_lt hlt]
        omega
      · have heq : n % N + 1 = N := by omega
        have hzero : (n + 1) % N = 0 := by simp [hstep, heq]
        omega
    simp [h, hs]

omit [Algebra ℚ R] in
/-- At the wraparound, transfer coefficients shift by one and gain `λ`. -/
theorem transferSectionCoeff_succ_zero {N : ℕ} (hN : 0 < N)
    (lambda : R) (n : ℕ) :
    transferSectionCoeff N 0 lambda (n + 1) =
      lambda * transferSectionCoeff N (N - 1) lambda n := by
  unfold transferSectionCoeff
  have hnmod : n % N < N := Nat.mod_lt n hN
  have hstep : (n + 1) % N = (n % N + 1) % N :=
    (Nat.mod_add_mod n N 1).symm
  by_cases h : n % N = N - 1
  · have heq : n % N + 1 = N := by omega
    have hs : (n + 1) % N = 0 := by simp [hstep, heq]
    simp only [hs, h, ite_true]
    rw [pow_succ']
  · have hs : (n + 1) % N ≠ 0 := by
      intro hs
      apply h
      by_cases hlt : n % N + 1 < N
      · have heq : (n + 1) % N = n % N + 1 := by
          rw [hstep, Nat.mod_eq_of_lt hlt]
        omega
      · omega
    simp [h, hs]

/-- Exponential-generating coefficients of the signed section `D_{N,j}`. -/
def signedSectionCoeff (N j : ℕ) (n : ℕ) : R :=
  if n % N = j then (-1 : R) ^ (n / N) else 0

/-- Formal signed section `D_{N,j}`. -/
def signedSection (N j : ℕ) : R⟦X⟧ :=
  exponentialGeneratingSeries (signedSectionCoeff (R := R) N j)

@[simp]
theorem coeff_signedSection (N j n : ℕ) :
    PowerSeries.coeff n (signedSection (R := R) N j) =
      signedSectionCoeff (R := R) N j n *
        algebraMap ℚ R (1 / (n.factorial : ℚ)) := by
  simp [signedSection]

private theorem succ_div_eq_of_mod_succ_lt {N n : ℕ} (hN : 0 < N)
    (h : n % N + 1 < N) :
    (n + 1) / N = n / N := by
  have hOne : 1 < N := by omega
  rw [Nat.add_div hN, Nat.div_eq_of_lt hOne, Nat.mod_eq_of_lt hOne]
  simp [Nat.not_le.mpr h]

private theorem succ_div_eq_add_one_of_mod_eq_pred {N n : ℕ} (hN : 0 < N)
    (h : n % N = N - 1) :
    (n + 1) / N = n / N + 1 := by
  by_cases hOne : N = 1
  · subst N
    simp
  · have hOneN : 1 < N := by omega
    rw [Nat.add_div hN, Nat.div_eq_of_lt hOneN, Nat.mod_eq_of_lt hOneN]
    simp [show N ≤ n % N + 1 by omega]

omit [Algebra ℚ R] in
/-- Away from the wraparound, signed coefficients shift without changing sign. -/
theorem signedSectionCoeff_succ_of_pos {N j : ℕ} (hN : 0 < N)
    (hj : 0 < j) (hjN : j < N) (n : ℕ) :
    signedSectionCoeff (R := R) N j (n + 1) =
      signedSectionCoeff (R := R) N (j - 1) n := by
  unfold signedSectionCoeff
  have hnmod : n % N < N := Nat.mod_lt n hN
  have hstep : (n + 1) % N = (n % N + 1) % N :=
    (Nat.mod_add_mod n N 1).symm
  by_cases h : n % N = j - 1
  · have hlt : n % N + 1 < N := by omega
    have hs : (n + 1) % N = j := by
      rw [hstep, Nat.mod_eq_of_lt hlt]
      omega
    have hdiv : (n + 1) / N = n / N :=
      succ_div_eq_of_mod_succ_lt hN hlt
    simp [h, hs, hdiv]
  · have hs : (n + 1) % N ≠ j := by
      intro hs
      apply h
      by_cases hlt : n % N + 1 < N
      · have heq : (n + 1) % N = n % N + 1 := by
          rw [hstep, Nat.mod_eq_of_lt hlt]
        omega
      · have heq : n % N + 1 = N := by omega
        have hzero : (n + 1) % N = 0 := by simp [hstep, heq]
        omega
    simp [h, hs]

omit [Algebra ℚ R] in
/-- The signed coefficient wraparound contributes exactly one minus sign. -/
theorem signedSectionCoeff_succ_zero {N : ℕ} (hN : 0 < N) (n : ℕ) :
    signedSectionCoeff (R := R) N 0 (n + 1) =
      -signedSectionCoeff (R := R) N (N - 1) n := by
  unfold signedSectionCoeff
  have hnmod : n % N < N := Nat.mod_lt n hN
  have hstep : (n + 1) % N = (n % N + 1) % N :=
    (Nat.mod_add_mod n N 1).symm
  by_cases h : n % N = N - 1
  · have heq : n % N + 1 = N := by omega
    have hs : (n + 1) % N = 0 := by simp [hstep, heq]
    have hdiv : (n + 1) / N = n / N + 1 :=
      succ_div_eq_add_one_of_mod_eq_pred hN h
    simp only [hs, h, ite_true, hdiv, pow_succ]
    ring
  · have hs : (n + 1) % N ≠ 0 := by
      intro hs
      apply h
      by_cases hlt : n % N + 1 < N
      · have heq : (n + 1) % N = n % N + 1 := by
          rw [hstep, Nat.mod_eq_of_lt hlt]
        omega
      · omega
    simp [h, hs]

/-- Formal derivative cycle for the nonzero transfer-section labels. -/
theorem derivative_transferSection_of_pos {N j : ℕ} (hN : 0 < N)
    (hj : 0 < j) (hjN : j < N) (lambda : R) :
    PowerSeries.derivative R (transferSection N j lambda) =
      PowerSeries.C lambda * transferSection N (j - 1) lambda := by
  rw [transferSection, derivative_exponentialGeneratingSeries, transferSection]
  ext n
  rw [PowerSeries.coeff_C_mul]
  simp only [coeff_exponentialGeneratingSeries]
  rw [transferSectionCoeff_succ_of_pos hN hj hjN]
  ring

/-- Formal derivative cycle at the transfer-section wraparound. -/
theorem derivative_transferSection_zero {N : ℕ} (hN : 0 < N) (lambda : R) :
    PowerSeries.derivative R (transferSection N 0 lambda) =
      PowerSeries.C lambda * transferSection N (N - 1) lambda := by
  rw [transferSection, derivative_exponentialGeneratingSeries, transferSection]
  ext n
  rw [PowerSeries.coeff_C_mul]
  simp only [coeff_exponentialGeneratingSeries]
  rw [transferSectionCoeff_succ_zero hN]
  ring

/-- Formal derivative cycle for the nonzero signed-section labels. -/
theorem derivative_signedSection_of_pos {N j : ℕ} (hN : 0 < N)
    (hj : 0 < j) (hjN : j < N) :
    PowerSeries.derivative R (signedSection (R := R) N j) =
      signedSection (R := R) N (j - 1) := by
  rw [signedSection, derivative_exponentialGeneratingSeries, signedSection]
  ext n
  simp only [coeff_exponentialGeneratingSeries]
  rw [signedSectionCoeff_succ_of_pos hN hj hjN]

/-- Formal derivative cycle at the signed wraparound, with the required minus sign. -/
theorem derivative_signedSection_zero {N : ℕ} (hN : 0 < N) :
    PowerSeries.derivative R (signedSection (R := R) N 0) =
      -signedSection (R := R) N (N - 1) := by
  rw [signedSection, derivative_exponentialGeneratingSeries, signedSection]
  ext n
  simp only [coeff_exponentialGeneratingSeries, map_neg]
  rw [signedSectionCoeff_succ_zero hN]
  ring

omit [Algebra ℚ R] in
/-- Advancing by one full block multiplies transfer coefficients by `λ^N`. -/
theorem transferSectionCoeff_add_period {N j : ℕ} (_hN : 0 < N)
    (lambda : R) (n : ℕ) :
    transferSectionCoeff N j lambda (n + N) =
      lambda ^ N * transferSectionCoeff N j lambda n := by
  unfold transferSectionCoeff
  have hmod : (n + N) % N = n % N := Nat.add_mod_right n N
  rw [hmod]
  by_cases h : n % N = j
  · simp only [h, ite_true]
    rw [pow_add]
    ring
  · simp [h]

omit [Algebra ℚ R] in
/-- Advancing by one full block reverses the signed coefficient. -/
theorem signedSectionCoeff_add_period {N j : ℕ} (hN : 0 < N) (n : ℕ) :
    signedSectionCoeff (R := R) N j (n + N) =
      -signedSectionCoeff (R := R) N j n := by
  unfold signedSectionCoeff
  have hmod : (n + N) % N = n % N := Nat.add_mod_right n N
  have hdiv : (n + N) / N = n / N + 1 := by
    simpa using Nat.add_mul_div_left n 1 hN
  rw [hmod, hdiv]
  by_cases h : n % N = j
  · simp only [h, ite_true, pow_succ]
    ring
  · simp [h]

/-- Every formal transfer section satisfies the expected `N`th-order equation. -/
theorem iterate_derivative_transferSection {N j : ℕ} (hN : 0 < N)
    (lambda : R) :
    (PowerSeries.derivative R)^[N] (transferSection N j lambda) =
      PowerSeries.C (lambda ^ N) * transferSection N j lambda := by
  rw [transferSection, iterate_derivative_exponentialGeneratingSeries]
  ext n
  rw [PowerSeries.coeff_C_mul]
  simp only [coeff_exponentialGeneratingSeries]
  rw [transferSectionCoeff_add_period hN]
  ring

/-- Every formal signed section satisfies `D^(N) = -D`. -/
theorem iterate_derivative_signedSection {N j : ℕ} (hN : 0 < N) :
    (PowerSeries.derivative R)^[N] (signedSection (R := R) N j) =
      -signedSection (R := R) N j := by
  rw [signedSection, iterate_derivative_exponentialGeneratingSeries]
  ext n
  simp only [coeff_exponentialGeneratingSeries, map_neg]
  rw [signedSectionCoeff_add_period hN]
  ring

/-- Formal initial data for the transfer basis. -/
theorem constantCoeff_iterate_derivative_transferSection {N j k : ℕ}
    (hkN : k < N) (lambda : R) :
    PowerSeries.constantCoeff
        ((PowerSeries.derivative R)^[k] (transferSection N j lambda)) =
      if k = j then lambda ^ j else 0 := by
  rw [transferSection, iterate_derivative_exponentialGeneratingSeries]
  rw [← PowerSeries.coeff_zero_eq_constantCoeff]
  simp only [coeff_exponentialGeneratingSeries, zero_add, Nat.factorial_zero,
    Nat.cast_one, one_div]
  rw [transferSectionCoeff]
  rw [Nat.mod_eq_of_lt hkN]
  by_cases h : k = j
  · subst j
    simp
  · simp [h]

/-- Formal initial data for the signed basis: the derivative matrix is the identity. -/
theorem constantCoeff_iterate_derivative_signedSection {N j k : ℕ}
    (_hjN : j < N) (hkN : k < N) :
    PowerSeries.constantCoeff
        ((PowerSeries.derivative R)^[k] (signedSection (R := R) N j)) =
      if k = j then 1 else 0 := by
  rw [signedSection, iterate_derivative_exponentialGeneratingSeries]
  rw [← PowerSeries.coeff_zero_eq_constantCoeff]
  simp only [coeff_exponentialGeneratingSeries, zero_add, Nat.factorial_zero,
    Nat.cast_one, one_div]
  rw [signedSectionCoeff]
  rw [Nat.mod_eq_of_lt hkN]
  by_cases h : k = j
  · subst j
    simp [Nat.div_eq_of_lt hkN]
  · simp [h]

end

end Komorebi.PaperIV
