module
public import DyadicFourAllRows
public import StepAmplification
public import DyadicFourSharpening
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.DyadicFourFinalStrengthening
open Mahler DyadicFourCongruences

/-- Step-sensitive precision at every row, with no saturation cap. -/
theorem normalized_step_bound (j u k n : ℕ) (hj : j < 4) :
    (2 : ℤ_[2]) ^ (k * (padicValNat 2 u + 1)) ∣
      difference u k (normalizedLift j hj) n := by
  have H := StepAmplification.repeated_precision 2 (normalizedLift j hj) 1 n u
    (k * (padicValNat 2 u + 1)) (fun a =>
      dvd_trans (pow_dvd_pow _ (min_le_left _ _))
        (DyadicFourAllRows.base_step_bound j a n hj)) k
  simpa only [Nat.cast_ofNat, mul_one, min_self] using H

theorem normalized_step_precision (j u k n : ℕ) (hj : j < 4) :
    GlobalEulerBoundary.precision 2 ((k * (padicValNat 2 u + 1) : ℕ) : ℤ)
      (difference u k (Congruential.coeff 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (normalizedLift j hj) n) _ (normalized_difference_coe j u k n hj)
    _ (normalized_step_bound j u k n hj)

/-- The original coefficients gain their full address-factorial valuation at every row. -/
theorem unnormalized_step_bound (j u k n : ℕ) (hj : j < 4) :
    (2 : ℤ_[2]) ^ (k * (padicValNat 2 u + 1) + padicValNat 2 j.factorial) ∣
      difference u k (unnormalizedLift j hj) n := by
  have hf : (2 : ℤ_[2]) ^ (padicValNat 2 j.factorial) ∣ (j.factorial : ℤ_[2]) := by
    obtain ⟨c, hc⟩ := pow_padicValNat_dvd (p := 2) (n := j.factorial)
    refine ⟨(c : ℤ_[2]), ?_⟩
    simpa only [Nat.cast_mul, Nat.cast_pow, Nat.cast_ofNat] using
      congrArg (fun a : ℕ => (a : ℤ_[2])) hc
  rw [DyadicFourSharpening.unnormalized_difference_factorial, pow_add]
  simpa only [mul_comm] using mul_dvd_mul hf (normalized_step_bound j u k n hj)

theorem unnormalized_step_precision (j u k n : ℕ) (hj : j < 4) :
    GlobalEulerBoundary.precision 2
      ((k * (padicValNat 2 u + 1) + padicValNat 2 j.factorial : ℕ) : ℤ)
      (difference u k (Congruential.unnormalized 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (unnormalizedLift j hj) n) _ (unnormalized_difference_coe j u k n hj)
    _ (unnormalized_step_bound j u k n hj)

/-- The normalized dyadic period is valid starting at row zero. -/
theorem normalized_period (j r n : ℕ) (hj : j < 4) (hr : 0 < r) :
    (2 : ℤ_[2]) ^ r ∣ normalizedLift j hj (n + 2 ^ (r - 1)) - normalizedLift j hj n := by
  have H := PeriodFromDifferences.prime_power_period 2 (normalizedLift j hj) 1 n r hr
    (fun k => dvd_trans (pow_dvd_pow _ (min_le_left _ _))
      (DyadicFourAllRows.base_step_bound j k n hj))
  simpa only [Nat.cast_ofNat, mul_one] using H

/-- All four original packets have the conjectured period at every row. -/
theorem all_rows_period (j r n : ℕ) (hj : j < 4) (hr : 0 < r) :
    (2 : ℤ_[2]) ^ r ∣ unnormalizedLift j hj (n + 2 ^ (r - 1)) - unnormalizedLift j hj n := by
  simpa only [unnormalizedLift, mul_sub] using
    dvd_mul_of_dvd_right (normalized_period j r n hj hr) (j.factorial : ℤ_[2])

theorem all_rows_period_precision (j r n : ℕ) (hj : j < 4) (hr : 0 < r) :
    GlobalEulerBoundary.precision 2 (r : ℤ)
      (Congruential.unnormalized 4 j (n + 2 ^ (r - 1)) - Congruential.unnormalized 4 j n) := by
  apply StandardWindowPrecision.rational_precision_of_divisibility 2
    (unnormalizedLift j hj (n + 2 ^ (r - 1)) - unnormalizedLift j hj n)
  · simp only [PadicInt.coe_sub, unnormalizedLift_coe, Rat.cast_sub]
  · exact all_rows_period j r n hj hr

/-- Literal original degree statement, with no lower bound on the packet row. -/
theorem all_rows_period_degree (j r n : ℕ) (hj : j < 4) (hr : 0 < r) :
    GlobalEulerBoundary.precision 2 (r : ℤ)
      (NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n + 2 ^ (r + 1)) -
       NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n)) := by
  have he : 4 * (n + 2 ^ (r - 1)) = 4 * n + 2 ^ (r + 1) := by
    have hp : 2 ^ (r + 1) = 2 ^ (r - 1) * 2 ^ 2 := by
      rw [← pow_add]
      congr 1
      omega
    rw [hp]
    ring
  rw [← he, NishibuchiCompletion.generalizedEuler_at_packet,
    NishibuchiCompletion.generalizedEuler_at_packet]
  exact all_rows_period_precision j r n hj hr

/-- The higher-address half period also starts at row zero. -/
theorem all_rows_half_period (j r n : ℕ) (hj : j < 4) (hj2 : 2 ≤ j) (hr : 2 ≤ r) :
    (2 : ℤ_[2]) ^ r ∣ unnormalizedLift j hj (n + 2 ^ (r - 2)) - unnormalizedLift j hj n := by
  have h := mul_dvd_mul (DyadicFourSharpening.factorial_even j hj hj2)
    (normalized_period j (r - 1) n hj (by omega))
  have he : (2 : ℤ_[2]) * 2 ^ (r - 1) = 2 ^ r := by
    rw [← pow_succ']
    congr 1
    omega
  have he' : r - 1 - 1 = r - 2 := by omega
  rw [he, he'] at h
  simpa only [unnormalizedLift, mul_sub] using h

theorem all_rows_half_period_precision (j r n : ℕ) (hj : j < 4)
    (hj2 : 2 ≤ j) (hr : 2 ≤ r) :
    GlobalEulerBoundary.precision 2 (r : ℤ)
      (Congruential.unnormalized 4 j (n + 2 ^ (r - 2)) - Congruential.unnormalized 4 j n) := by
  apply StandardWindowPrecision.rational_precision_of_divisibility 2
    (unnormalizedLift j hj (n + 2 ^ (r - 2)) - unnormalizedLift j hj n)
  · simp only [PadicInt.coe_sub, unnormalizedLift_coe, Rat.cast_sub]
  · exact all_rows_half_period j r n hj hj2 hr

theorem all_rows_half_period_degree (j r n : ℕ) (hj : j < 4)
    (hj2 : 2 ≤ j) (hr : 2 ≤ r) :
    GlobalEulerBoundary.precision 2 (r : ℤ)
      (NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n + 2 ^ r) -
       NishibuchiCompletion.generalizedEuler 4 (by decide) j (4 * n)) := by
  have he : 4 * (n + 2 ^ (r - 2)) = 4 * n + 2 ^ r := by
    have hp : 2 ^ r = 2 ^ (r - 2) * 2 ^ 2 := by
      rw [← pow_add, Nat.sub_add_cancel hr]
    rw [hp]
    ring
  rw [← he, NishibuchiCompletion.generalizedEuler_at_packet,
    NishibuchiCompletion.generalizedEuler_at_packet]
  exact all_rows_half_period_precision j r n hj hj2 hr

end KomorebiPaperIX.DyadicFourFinalStrengthening
