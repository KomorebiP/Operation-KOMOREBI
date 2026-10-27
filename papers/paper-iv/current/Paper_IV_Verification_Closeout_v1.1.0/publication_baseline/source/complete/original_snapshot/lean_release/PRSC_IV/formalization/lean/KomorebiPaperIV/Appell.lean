/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/

import KomorebiPaperIV.FormalExponential
import Mathlib.Algebra.Polynomial.Derivative

/-!
# Formal Appell systems

This file packages the product `exp (rL) exp (xX)` and proves the exact
one- and two-parameter coefficient convolution laws.  These are the
formal generating-series statements behind Paper IV's block Appell family.
-/

namespace Komorebi.PaperIV

open scoped PowerSeries

noncomputable section

variable {R : Type*} [CommRing R] [Algebra ℚ R]

/-- The Appell generating series `exp (rL) exp (xX)`. -/
def appellSeries (L : R⟦X⟧) (r x : R) : R⟦X⟧ :=
  formalExpFamily L r * PowerSeries.rescale x (PowerSeries.exp R)

/-- The Appell polynomial value encoded by the exponential generating series. -/
def appellCoeff (L : R⟦X⟧) (r x : R) (m : ℕ) : R :=
  egfCoeff m (appellSeries L r x)

/-- Product law in both the order parameter and the space variable. -/
theorem appellSeries_two_parameter {L : R⟦X⟧} (hL : L.constantCoeff = 0)
    (r s x y : R) :
    appellSeries L r x * appellSeries L s y = appellSeries L (r + s) (x + y) := by
  rw [appellSeries, appellSeries, appellSeries]
  calc
    (formalExpFamily L r * PowerSeries.rescale x (PowerSeries.exp R)) *
        (formalExpFamily L s * PowerSeries.rescale y (PowerSeries.exp R)) =
      (formalExpFamily L r * formalExpFamily L s) *
        (PowerSeries.rescale x (PowerSeries.exp R) *
          PowerSeries.rescale y (PowerSeries.exp R)) := by ring
    _ = formalExpFamily L (r + s) * PowerSeries.rescale (x + y) (PowerSeries.exp R) := by
      rw [formalExpFamily_semigroup hL, PowerSeries.exp_mul_exp_eq_exp_add]

/-- Paper IV's exact two-parameter Appell convolution. -/
theorem appell_two_parameter_convolution {L : R⟦X⟧} (hL : L.constantCoeff = 0)
    (r s x y : R) (m : ℕ) :
    appellCoeff L (r + s) (x + y) m =
      ∑ p ∈ Finset.antidiagonal m,
        (m.choose p.1 : R) * appellCoeff L r x p.1 * appellCoeff L s y p.2 := by
  unfold appellCoeff
  rw [← appellSeries_two_parameter hL]
  exact egfCoeff_mul m _ _

/-- The EGF coefficient of `exp (xX)` is `x^m`. -/
theorem egfCoeff_rescale_exp (x : R) (m : ℕ) :
    egfCoeff m (PowerSeries.rescale x (PowerSeries.exp R)) = x ^ m := by
  rw [egfCoeff, PowerSeries.coeff_rescale, PowerSeries.coeff_exp]
  have hfac :
      (m.factorial : R) * algebraMap ℚ R (1 / (m.factorial : ℚ)) = 1 := by
    have key : (m.factorial : R) = algebraMap ℚ R (m.factorial : ℚ) := by
      rw [map_natCast]
    rw [key, ← map_mul]
    field_simp
    simp
  calc
    (m.factorial : R) * (x ^ m * algebraMap ℚ R (1 / (m.factorial : ℚ))) =
        x ^ m * ((m.factorial : R) * algebraMap ℚ R (1 / (m.factorial : ℚ))) := by ring
    _ = x ^ m := by rw [hfac, mul_one]

theorem appellCoeff_zero_parameter {L : R⟦X⟧} (hL : L.constantCoeff = 0)
    (y : R) (m : ℕ) :
    appellCoeff L 0 y m = y ^ m := by
  rw [appellCoeff, appellSeries, formalExpFamily_zero hL, one_mul,
    egfCoeff_rescale_exp]

/-- Appell translation/addition law. -/
theorem appell_addition {L : R⟦X⟧} (hL : L.constantCoeff = 0)
    (r x y : R) (m : ℕ) :
    appellCoeff L r (x + y) m =
      ∑ p ∈ Finset.antidiagonal m,
        (m.choose p.1 : R) * appellCoeff L r x p.1 * y ^ p.2 := by
  have h := appell_two_parameter_convolution hL r 0 x y m
  simpa [appellCoeff_zero_parameter hL] using h

/-- The reciprocal-family coefficients are the Appell values at `x = 0`. -/
theorem appellCoeff_at_zero (L : R⟦X⟧) (r : R) (m : ℕ) :
    appellCoeff L r 0 m = egfCoeff m (formalExpFamily L r) := by
  rw [appellCoeff, appellSeries]
  have hexp : PowerSeries.rescale 0 (PowerSeries.exp R) = 1 := by
    rw [PowerSeries.rescale_zero_apply, PowerSeries.constantCoeff_exp, map_one]
  rw [hexp, mul_one]

/-- Polynomial reconstructed from its Appell base coefficients. -/
def appellPolynomial (a : ℕ → R) (m : ℕ) : Polynomial R :=
  ∑ q ∈ Finset.range (m + 1),
    Polynomial.C ((m.choose q : R) * a q) * Polynomial.X ^ (m - q)

omit [Algebra ℚ R] in
/-- The exact Appell lowering law, proved for arbitrary base coefficients. -/
theorem derivative_appellPolynomial (a : ℕ → R) (m : ℕ) :
    Polynomial.derivative (appellPolynomial a (m + 1)) =
      Polynomial.C (m + 1 : R) * appellPolynomial a m := by
  rw [appellPolynomial, appellPolynomial]
  rw [map_sum]
  rw [Finset.sum_range_succ]
  simp only [Polynomial.derivative_mul, Polynomial.derivative_C, zero_mul, zero_add,
    Polynomial.derivative_X_pow]
  simp only [Nat.sub_self, Nat.cast_zero, map_zero, zero_mul, mul_zero, add_zero]
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro q hq
  have hqm : q ≤ m := Nat.le_of_lt_succ (Finset.mem_range.mp hq)
  have hsub : m + 1 - q - 1 = m - q := by omega
  have hnat := Nat.choose_mul_succ_eq m q
  have hcast :
      (m.choose q : R) * (m + 1 : R) =
        ((m + 1).choose q : R) * ((m + 1 - q : ℕ) : R) := by
    simpa only [Nat.cast_mul, Nat.cast_add, Nat.cast_one, Nat.cast_sub hqm] using
      congrArg (fun z : ℕ => (z : R)) hnat
  rw [hsub]
  simp only [← mul_assoc, ← map_mul]
  apply congrArg (fun c : R => Polynomial.C c * Polynomial.X ^ (m - q))
  calc
    ((m + 1).choose q : R) * a q * ((m + 1 - q : ℕ) : R) =
        (((m + 1).choose q : R) * ((m + 1 - q : ℕ) : R)) * a q := by ring
    _ = ((m.choose q : R) * (m + 1 : R)) * a q := by rw [← hcast]
    _ = (m + 1 : R) * (m.choose q : R) * a q := by ring

/-- Paper IV's Appell polynomial attached to `exp (rL)`. -/
def formalAppellPolynomial (L : R⟦X⟧) (r : R) (m : ℕ) : Polynomial R :=
  appellPolynomial (fun q => egfCoeff q (formalExpFamily L r)) m

/-- Paper IV's Appell derivative law. -/
theorem derivative_formalAppellPolynomial (L : R⟦X⟧) (r : R) (m : ℕ) :
    Polynomial.derivative (formalAppellPolynomial L r (m + 1)) =
      Polynomial.C (m + 1 : R) * formalAppellPolynomial L r m := by
  exact derivative_appellPolynomial _ m

theorem eval_formalAppellPolynomial (L : R⟦X⟧) (r x : R) (m : ℕ) :
    (formalAppellPolynomial L r m).eval x = appellCoeff L r x m := by
  rw [formalAppellPolynomial, appellPolynomial, Polynomial.eval_finsetSum]
  unfold appellCoeff appellSeries
  rw [egfCoeff_mul]
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk]
  apply Finset.sum_congr rfl
  intro q hq
  simp only [Polynomial.eval_mul, Polynomial.eval_C, Polynomial.eval_pow, Polynomial.eval_X]
  rw [egfCoeff_rescale_exp]

end

end Komorebi.PaperIV
