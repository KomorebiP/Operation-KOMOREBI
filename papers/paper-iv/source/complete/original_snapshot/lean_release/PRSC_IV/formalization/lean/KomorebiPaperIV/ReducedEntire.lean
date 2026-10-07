/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.SignedFiniteExceptions
import KomorebiPaperIV.ReciprocalCore
import Mathlib.Analysis.Analytic.OfScalars

namespace Komorebi.PaperIV
noncomputable section
open FormalMultilinearSeries

/-- The manuscript's reduced denominator as an actual complex power series. -/
def entireReducedDenominator (N : ℕ) : ℂ → ℂ :=
  ofScalarsSum (fun n => PowerSeries.coeff n (reducedDenominator (R := ℂ) N))

theorem reducedDenominator_coeff_complex (N n : ℕ) :
    PowerSeries.coeff n (reducedDenominator (R := ℂ) N) =
      (-1 : ℂ) ^ n / ((N * n).factorial : ℂ) := by
  simp [coeff_reducedDenominator]

theorem reducedDenominator_coeff_norm (N n : ℕ) :
    ‖PowerSeries.coeff n (reducedDenominator (R := ℂ) N)‖ =
      1 / ((N * n).factorial : ℝ) := by
  rw [reducedDenominator_coeff_complex, norm_div, norm_pow]
  simp

theorem reducedDenominator_entire_radius {N : ℕ} (hN : 0 < N) :
    (ofScalars ℂ (fun n => PowerSeries.coeff n (reducedDenominator (R := ℂ) N))).radius = ⊤ := by
  apply radius_eq_top_of_summable_norm
  intro r
  apply Summable.of_nonneg_of_le (fun n => mul_nonneg (norm_nonneg _) (pow_nonneg r.2 _))
    (fun n => ?_) (Real.summable_pow_div_factorial (r : ℝ))
  rw [ofScalars_norm, reducedDenominator_coeff_norm, one_div_mul_eq_div]
  apply div_le_div_of_nonneg_left (pow_nonneg r.2 n) (by positivity)
  exact_mod_cast Nat.factorial_le (Nat.le_mul_of_pos_left n hN)

theorem analyticAt_entireReducedDenominator {N : ℕ} (hN : 0 < N) (w : ℂ) :
    AnalyticAt ℂ (entireReducedDenominator N) w := by
  apply (ofScalars ℂ (fun n => PowerSeries.coeff n (reducedDenominator (R := ℂ) N))).analyticOnNhd
  rw [reducedDenominator_entire_radius hN]; simp

theorem hasSum_entireReducedDenominator {N : ℕ} (hN : 0 < N) (w : ℂ) :
    HasSum (fun n => PowerSeries.coeff n (reducedDenominator (R := ℂ) N) * w ^ n)
      (entireReducedDenominator N w) := by
  have h := (ofScalars ℂ (fun n => PowerSeries.coeff n (reducedDenominator (R := ℂ) N))).hasSum
    (x := w) (by rw [reducedDenominator_entire_radius hN]; simp)
  simpa only [entireReducedDenominator, ofScalarsSum, ofScalars_apply_eq', smul_eq_mul] using h

@[simp] theorem entireReducedDenominator_zero (N : ℕ) : entireReducedDenominator N 0 = 1 := by
  simp [entireReducedDenominator]

/-- Exact analytic substitution, proved by reindexing the convergent Taylor series. -/
theorem canonicalSignedDenominator_eq_reduced_power {N : ℕ} (hN : 0 < N) (z : ℂ) :
    canonicalSignedDenominator N z = entireReducedDenominator N (z ^ N) := by
  have hd := hasSum_entireSigned hN hN (canonicalPrimitiveRoot_isPrimitive hN)
    (canonicalSignedRoot_pow hN) z
  have hi : Function.Injective (fun n : ℕ => N * n) := fun _ _ h => Nat.mul_left_cancel hN h
  have hz : ∀ n ∉ Set.range (fun m : ℕ => N * m),
      PowerSeries.coeff n (signedSection (R := ℂ) N 0) * z ^ n = 0 := by
    intro n hn
    have hnd : ¬ N ∣ n := by rintro ⟨m, rfl⟩; exact hn ⟨m, rfl⟩
    rw [signedSection_zero_eq_expand_reducedDenominator hN, PowerSeries.coeff_expand]
    simp [hnd]
  have hh := (hi.hasSum_iff hz).mpr hd
  apply hh.unique
  convert hasSum_entireReducedDenominator hN (z ^ N) using 1
  ext n
  dsimp only [Function.comp_def]
  rw [signedSection_zero_eq_expand_reducedDenominator hN, PowerSeries.coeff_expand_mul, pow_mul]

/-- Away from zero the power substitution preserves analytic multiplicity. -/
theorem canonicalSignedDenominator_order_eq_reduced {N : ℕ} (hN : 0 < N)
    {z : ℂ} (hz : z ≠ 0) :
    analyticOrderAt (canonicalSignedDenominator N) z =
      analyticOrderAt (entireReducedDenominator N) (z ^ N) := by
  have hd : deriv (fun w : ℂ => w ^ N) z = (N : ℂ) * z ^ (N - 1) := by
    exact (hasDerivAt_pow N z).deriv
  have hh := analyticOrderAt_comp_of_deriv_ne_zero (f := entireReducedDenominator N)
    (show AnalyticAt ℂ (fun w : ℂ => w ^ N) z by fun_prop)
    (by rw [hd]; exact mul_ne_zero (Nat.cast_ne_zero.mpr hN.ne') (pow_ne_zero _ hz))
  have he : entireReducedDenominator N ∘ (fun w : ℂ => w ^ N) = canonicalSignedDenominator N :=
    funext fun w => (canonicalSignedDenominator_eq_reduced_power hN w).symm
  rwa [he] at hh

end
end Komorebi.PaperIV
