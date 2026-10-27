/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ParameterThetaCompletion

/-!
# Complete exponential Bell coefficients

The Bell coefficients are defined by their standard generating function,
independently of the reciprocal family. The specialization below proves the
exact normalization in Theorem 7.2, including the parameter degree.
-/

namespace Komorebi.PaperIV
open scoped PowerSeries
noncomputable section
variable {K : Type*} [Field K] [CharZero K]

/-- The zero-constant EGF input used to define the complete Bell polynomials. -/
def bellInput (x : ℕ → K) : K⟦X⟧ :=
  PowerSeries.mk fun m => if m = 0 then 0 else x m / (m.factorial : K)

/-- The standard complete exponential Bell coefficient, normalized by `n!`. -/
def completeExponentialBell (n : ℕ) (x : ℕ → K) : K :=
  (n.factorial : K) *
    PowerSeries.coeff n ((PowerSeries.exp K).subst (bellInput x))

omit [CharZero K] in
@[simp] theorem constantCoeff_bellInput (x : ℕ → K) :
    (bellInput x).constantCoeff = 0 := by
  simp [bellInput]

/-- Generating-function normalization, including the zeroth coefficient. -/
theorem completeExponentialBell_generating_coefficient (n : ℕ) (x : ℕ → K) :
    PowerSeries.coeff n ((PowerSeries.exp K).subst (bellInput x)) =
      completeExponentialBell n x / (n.factorial : K) := by
  have hn : (n.factorial : K) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  simp [completeExponentialBell, hn]

@[simp] theorem completeExponentialBell_zero (x : ℕ → K) :
    completeExponentialBell 0 x = 1 := by
  simp only [completeExponentialBell, Nat.factorial_zero, Nat.cast_one, one_mul,
    PowerSeries.coeff_zero_eq_constantCoeff]
  change MvPowerSeries.constantCoeff ((PowerSeries.exp K).subst (bellInput x)) = 1
  rw [PowerSeries.constantCoeff_subst_of_constantCoeff_zero (constantCoeff_bellInput x)]
  simp

/-- The logarithmic normalization gives exactly the Bell input in Paper IV. -/
theorem bellInput_reciprocal (N : ℕ) (r : K) :
    bellInput (fun m => r * ((m - 1).factorial : K) * kappaCoeff N m) =
      PowerSeries.C r * negativeLogDenominator N := by
  ext m
  cases m with
  | zero => simp [bellInput, constantCoeff_negativeLogDenominator,
      PowerSeries.coeff_zero_eq_constantCoeff]
  | succ m =>
    simp only [bellInput, PowerSeries.coeff_mk, Nat.succ_ne_zero, ↓reduceIte,
      Nat.succ_sub_one, kappaCoeff, PowerSeries.coeff_C_mul]
    rw [Nat.factorial_succ, Nat.cast_mul]
    have hm : (m.factorial : K) ≠ 0 := by exact_mod_cast m.factorial_ne_zero
    have hs : (m.succ : K) ≠ 0 := by exact_mod_cast Nat.succ_ne_zero m
    field_simp

/-- Theorem 7.2: the exact Bell formula, for every coefficient and parameter. -/
theorem reciprocalCoeff_bell_formula (N n : ℕ) (r : K) :
    reciprocalCoeff N n r =
      ((N * n).factorial : K) / (n.factorial : K) *
        completeExponentialBell n
          (fun m => r * ((m - 1).factorial : K) * kappaCoeff N m) := by
  rw [completeExponentialBell, bellInput_reciprocal, reciprocalCoeff, blockCoeff,
    reciprocalSeries, formalExpFamily_eq_exp_subst (constantCoeff_negativeLogDenominator N)]
  have hn : (n.factorial : K) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  field_simp

theorem coeff_one_negativeLogDenominator (N : ℕ) :
    PowerSeries.coeff 1 (negativeLogDenominator (R := K) N) =
      (N.factorial : K)⁻¹ := by
  rw [negativeLogDenominator, map_neg,
    coeff_one_logOf_of_constantCoeff_one (constantCoeff_reducedDenominator N),
    coeff_reducedDenominator]
  simp only [Nat.mul_one, pow_one, map_div₀, map_neg, map_one, map_natCast]
  ring

/-- Exact leading parameter coefficient of the reciprocal polynomial. -/
theorem coeff_reciprocalCoeffPolynomialOver_parameterDegree (N n : ℕ) :
    (reciprocalCoeffPolynomialOver (K := K) N n).coeff n =
      ((N * n).factorial : K) /
        ((n.factorial : K) * (N.factorial : K) ^ n) := by
  let L : K⟦X⟧ := negativeLogDenominator (R := K) N
  let Cφ : K →ₐ[ℚ] Polynomial K :=
    (Polynomial.CAlgHom : K →ₐ[K] Polynomial K).restrictScalars ℚ
  have hmapL : PowerSeries.map Polynomial.C L =
      negativeLogDenominator (R := Polynomial K) N := by
    have h := map_negativeLogDenominator Cφ N
    have hc : (Cφ : K →+* Polynomial K) = Polynomial.C := by
      ext x
      simp [Cφ]
    simpa only [hc] using h
  rw [reciprocalCoeffPolynomialOver, reciprocalCoeff, blockCoeff,
    reciprocalSeries, ← hmapL]
  rw [show ((N * n).factorial : Polynomial K) =
      Polynomial.C ((N * n).factorial : K) by simp]
  rw [Polynomial.coeff_C_mul,
    coeff_parameterDegree_formalExpFamily_map_C L
      (constantCoeff_negativeLogDenominator N)]
  simp only [L, coeff_one_negativeLogDenominator, inv_pow]
  ring

/-- The degree is exact, not merely bounded above. -/
theorem natDegree_reciprocalCoeffPolynomialOver (N n : ℕ) :
    (reciprocalCoeffPolynomialOver (K := K) N n).natDegree = n := by
  apply Polynomial.natDegree_eq_of_le_of_coeff_ne_zero
    (natDegree_reciprocalCoeffPolynomialOver_le N n)
  rw [coeff_reciprocalCoeffPolynomialOver_parameterDegree]
  apply div_ne_zero
  · exact_mod_cast (N * n).factorial_ne_zero
  · apply mul_ne_zero
    · exact_mod_cast n.factorial_ne_zero
    · apply pow_ne_zero
      exact_mod_cast N.factorial_ne_zero

/-- The parameter factor holds over every characteristic-zero field. -/
theorem X_dvd_reciprocalCoeffPolynomialOver (N : ℕ) {n : ℕ} (hn : 0 < n) :
    Polynomial.X ∣ reciprocalCoeffPolynomialOver (K := K) N n := by
  rw [Polynomial.X_dvd_iff]
  have h := eval_reciprocalCoeffPolynomialOver (K := K) N n 0
  rw [reciprocalCoeff_zero_parameter_of_pos N hn] at h
  rw [Polynomial.coeff_zero_eq_eval_zero]
  exact h

end
end Komorebi.PaperIV
