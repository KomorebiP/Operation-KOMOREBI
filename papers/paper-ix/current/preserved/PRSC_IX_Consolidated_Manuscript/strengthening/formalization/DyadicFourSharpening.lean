module
public import NishibuchiCompletion
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.DyadicFourSharpening
open Mahler DyadicFourCongruences

/-- Addresses two and three have exactly one elementary factorial factor of two. -/
theorem factorial_even (j : ℕ) (hj : j < 4) (hj2 : 2 ≤ j) :
    (2 : ℤ_[2]) ∣ (j.factorial : ℤ_[2]) := by
  interval_cases j
  · norm_num
  · refine ⟨3, ?_⟩
    norm_num

theorem unnormalized_difference_factorial (j u k n : ℕ) (hj : j < 4) :
    difference u k (unnormalizedLift j hj) n =
      (j.factorial : ℤ_[2]) * difference u k (normalizedLift j hj) n := by
  induction k generalizing n with
  | zero => rfl
  | succ k ih => rw [difference_succ, ih, ih, difference_succ, mul_sub]

/-- The original coefficients at addresses two and three gain one dyadic digit. -/
theorem factorial_difference_bound (j u k n : ℕ) (hj : j < 4) (hj2 : 2 ≤ j) :
    (2 : ℤ_[2]) ^ (1 + min k n) ∣ difference u k (unnormalizedLift j hj) n := by
  rw [unnormalized_difference_factorial, pow_add, pow_one]
  exact mul_dvd_mul (factorial_even j hj hj2) (normalized_bound j u k n hj)

theorem factorial_difference_precision (j u k n : ℕ) (hj : j < 4) (hj2 : 2 ≤ j) :
    GlobalEulerBoundary.precision 2 ((1 + min k n : ℕ) : ℤ)
      (difference u k (Congruential.unnormalized 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (unnormalizedLift j hj) n) _ (unnormalized_difference_coe j u k n hj)
    _ (factorial_difference_bound j u k n hj hj2)

/-- The period mechanism applies before multiplication by the address factorial. -/
theorem normalized_period (j r n : ℕ) (hj : j < 4) (hr : 0 < r) (hn : r ≤ n) :
    (2 : ℤ_[2]) ^ r ∣ normalizedLift j hj (n + 2 ^ (r - 1)) - normalizedLift j hj n := by
  have H := PeriodFromDifferences.prime_power_period 2 (normalizedLift j hj) 1 n r hr ?_
  · simpa only [Nat.cast_ofNat, mul_one] using H
  · intro k
    exact dvd_trans (pow_dvd_pow _ (min_le_min_left k hn)) (normalized_bound j 1 k n hj)

/-- Half the old packet displacement suffices for addresses two and three.
The sufficient starting row improves from r to r-1; no least-period claim. -/
theorem half_period (j r n : ℕ) (hj : j < 4) (hj2 : 2 ≤ j)
    (hr : 2 ≤ r) (hn : r - 1 ≤ n) :
    (2 : ℤ_[2]) ^ r ∣ unnormalizedLift j hj (n + 2 ^ (r - 2)) - unnormalizedLift j hj n := by
  have h := mul_dvd_mul (factorial_even j hj hj2)
    (normalized_period j (r - 1) n hj (by omega) hn)
  have he : (2 : ℤ_[2]) * 2 ^ (r - 1) = 2 ^ r := by
    rw [← pow_succ']
    congr 1
    omega
  have he' : r - 1 - 1 = r - 2 := by omega
  rw [he, he'] at h
  simpa only [unnormalizedLift, mul_sub] using h

theorem half_period_precision (j r n : ℕ) (hj : j < 4) (hj2 : 2 ≤ j)
    (hr : 2 ≤ r) (hn : r - 1 ≤ n) :
    GlobalEulerBoundary.precision 2 (r : ℤ)
      (Congruential.unnormalized 4 j (n + 2 ^ (r - 2)) - Congruential.unnormalized 4 j n) := by
  apply StandardWindowPrecision.rational_precision_of_divisibility 2
    (unnormalizedLift j hj (n + 2 ^ (r - 2)) - unnormalizedLift j hj n)
  · simp only [PadicInt.coe_sub, unnormalizedLift_coe, Rat.cast_sub]
  · exact half_period j r n hj hj2 hr hn

/-- Literal degree displacement 2^r, in place of the original 2^(r+1). -/
theorem half_period_degree (j r n : ℕ) (hj : j < 4) (hj2 : 2 ≤ j)
    (hr : 2 ≤ r) (hn : r - 1 ≤ n) :
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
  exact half_period_precision j r n hj hj2 hr hn

/-- At precision one these addresses vanish modulo two at every row. -/
theorem all_rows_even (j n : ℕ) (hj : j < 4) (hj2 : 2 ≤ j) :
    (2 : ℤ_[2]) ∣ unnormalizedLift j hj n :=
  dvd_mul_of_dvd_left (factorial_even j hj hj2) _

end KomorebiPaperIX.DyadicFourSharpening
