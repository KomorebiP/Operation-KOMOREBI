/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.CompleteHomogeneous

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology Classical
set_option maxHeartbeats 800000

theorem summable_norm_positive_powers {ι : Type*} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) {m : ℕ} (hm : 0 < m) :
    Summable (fun i => ‖a i ^ m‖) := by
  apply ha.of_norm_bounded_eventually
  filter_upwards [ha.tendsto_cofinite_zero.eventually (gt_mem_nhds (by norm_num : (0 : ℝ) < 1))] with i hi
  simp only [norm_norm, norm_pow]
  simpa using pow_le_pow_of_le_one (norm_nonneg (a i)) hi.le hm

@[simp] theorem homogeneousCoeff_zero (q : ℕ → ℂ) : homogeneousCoeff q 0 = 1 := by
  simp [homogeneousCoeff, PowerSeries.coeff_zero_eq_constantCoeff]

theorem homogeneousCoeff_succ (q : ℕ → ℂ) (n : ℕ) :
    homogeneousCoeff q (n + 1) =
      (∑ k ∈ Finset.range (n + 1), homogeneousCoeff q k * q (n - k + 1)) / (n + 1 : ℂ) := by
  apply (eq_div_iff (by exact_mod_cast Nat.succ_ne_zero n : (n + 1 : ℂ) ≠ 0)).mpr
  simpa only [mul_comm] using homogeneousCoeff_recurrence q n

theorem homogeneousCoeff_continuous (n : ℕ) : Continuous (fun q : ℕ → ℂ => homogeneousCoeff q n) := by
  induction n using Nat.strong_induction_on with
  | h n ih =>
      cases n with
      | zero => simpa using (continuous_const : Continuous (fun _ : ℕ → ℂ => (1 : ℂ)))
      | succ n =>
          simp_rw [homogeneousCoeff_succ]
          apply Continuous.div_const
          apply continuous_finsetSum
          intro k hk
          exact (ih k (Finset.mem_range.mp hk)).mul (continuous_apply _)

theorem homogeneousSeries_congr_positive {q Q : ℕ → ℂ} (h : ∀ m, 0 < m → q m = Q m) :
    homogeneousSeries q = homogeneousSeries Q := by
  have he : powerSumLog q = powerSumLog Q := by
    ext n
    simp only [powerSumLog, PowerSeries.coeff_mk]
    by_cases hn : n = 0
    · simp [hn]
    · rw [h n (Nat.pos_of_ne_zero hn)]
  rw [homogeneousSeries, homogeneousSeries, he]

def completeHomogeneous {ι : Type*} (a : ι → ℂ) (n : ℕ) : ℂ :=
  homogeneousCoeff (fun m => ∑' i, a i ^ m) n

theorem finiteHomogeneousSeries_coefficient_limit {ι : Type*} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (n : ℕ) :
    Tendsto (fun S : Finset ι => PowerSeries.coeff n (finiteHomogeneousSeries a S))
      atTop (𝓝 (completeHomogeneous a n)) := by
  let q : Finset ι → ℕ → ℂ := fun S m => if m = 0 then 0 else ∑ i ∈ S, a i ^ m
  let Q : ℕ → ℂ := fun m => if m = 0 then 0 else ∑' i, a i ^ m
  have ht : Tendsto q atTop (𝓝 Q) := by
    apply tendsto_pi_nhds.mpr
    intro m
    by_cases hm : m = 0
    · simp [q, Q, hm]
    · simpa only [q, Q, ite_eq_right hm] using! (summable_norm_positive_powers ha (Nat.pos_of_ne_zero hm)).of_norm.hasSum
  have h := (homogeneousCoeff_continuous n).tendsto Q |>.comp ht
  change Tendsto (fun S => homogeneousCoeff (q S) n) atTop (𝓝 (homogeneousCoeff Q n)) at h
  have he (S : Finset ι) : homogeneousSeries (q S) = homogeneousSeries (fun m => ∑ i ∈ S, a i ^ m) :=
    homogeneousSeries_congr_positive (fun m hm => by simp [q, hm.ne'])
  have hE : homogeneousSeries Q = homogeneousSeries (fun m => ∑' i, a i ^ m) :=
    homogeneousSeries_congr_positive (fun m hm => by simp [Q, hm.ne'])
  simpa only [Function.comp_def, homogeneousCoeff, he, hE, completeHomogeneous,
    finiteHomogeneousSeries_eq_homogeneous] using! h

/-- The infinite-variable meaning is the limit of the actual finite monomial sums. -/
theorem completeHomogeneous_monomial_limit {ι : Type*} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (n : ℕ) :
    Tendsto (fun S : Finset ι => ∑ l ∈ S.finsuppAntidiag n, ∏ i ∈ S, a i ^ (l i))
      atTop (𝓝 (completeHomogeneous a n)) := by
  simpa only [finiteHomogeneousSeries_monomials] using finiteHomogeneousSeries_coefficient_limit ha n

def repeatedEigenvalue {ι : Type*} (a : ι → ℂ) (r : ℕ) : ι × Fin r → ℂ := fun p => a p.1

theorem repeatedEigenvalue_norm_summable {ι : Type*} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (r : ℕ) : Summable (fun p => ‖repeatedEigenvalue a r p‖) := by
  apply (summable_prod_of_nonneg (fun p => norm_nonneg (repeatedEigenvalue a r p))).mpr
  refine ⟨fun i => (hasSum_fintype _).summable, ?_⟩
  simpa [repeatedEigenvalue, tsum_fintype, nsmul_eq_mul] using ha.mul_left (r : ℝ)

theorem repeatedEigenvalue_powerSum {ι : Type*} {a : ι → ℂ}
    (ha : Summable (fun i => ‖a i‖)) (r : ℕ) {m : ℕ} (hm : 0 < m) :
    (∑' p, repeatedEigenvalue a r p ^ m) = (r : ℂ) * ∑' i, a i ^ m := by
  have hs := (summable_norm_positive_powers (repeatedEigenvalue_norm_summable ha r) hm).of_norm
  rw [hs.tsum_prod]
  simp [repeatedEigenvalue, tsum_fintype, nsmul_eq_mul, tsum_mul_left]

theorem reciprocalSeries_eq_homogeneous_zero_sums {N : ℕ} (hN : 2 ≤ N) (r : ℂ) :
    reciprocalSeries N r = homogeneousSeries (fun m => r * zeroPowerSum (entireReducedDenominator N) m) := by
  have hd : PowerSeries.derivative ℂ (powerSumLog (fun m => r * zeroPowerSum (entireReducedDenominator N) m)) =
      PowerSeries.C r * PowerSeries.derivative ℂ (negativeLogDenominator N) := by
    ext n
    rw [powerSumLog_derivative_coeff, PowerSeries.coeff_C_mul, PowerSeries.coeff_derivative,
      ← kappaCoeff_eq_zeroPowerSum hN (Nat.succ_pos n)]
    simp [kappaCoeff, mul_comm]
  apply powerSeries_linear_ode_unique (H := PowerSeries.C r * PowerSeries.derivative ℂ (negativeLogDenominator N))
  · simp [constantCoeff_reciprocalSeries]
  · rw [derivative_reciprocalSeries]; ring
  · rw [homogeneousSeries_derivative, hd]

theorem reciprocalCoeff_completeHomogeneous {N : ℕ} (hN : 2 ≤ N) (n r : ℕ) :
    reciprocalCoeff N n (r : ℂ) / ((N * n).factorial : ℂ) =
      completeHomogeneous (repeatedEigenvalue
        (fun i : ZeroMultiplicityIndex (entireReducedDenominator N) => (indexedZero i)⁻¹) r) n := by
  have ha : Summable (fun i : ZeroMultiplicityIndex (entireReducedDenominator N) => ‖(indexedZero i)⁻¹‖) := by
    simpa [norm_inv, one_div] using zeroMultiplicity_reciprocal_summable
      (entireReducedDenominator_reciprocal_zeros_summable hN)
  have he : homogeneousSeries (fun m => ∑' p, repeatedEigenvalue
      (fun i : ZeroMultiplicityIndex (entireReducedDenominator N) => (indexedZero i)⁻¹) r p ^ m) =
      homogeneousSeries (fun m => (r : ℂ) * zeroPowerSum (entireReducedDenominator N) m) := by
    apply homogeneousSeries_congr_positive
    intro m hm
    simpa only [zeroPowerSum, one_div, inv_pow] using repeatedEigenvalue_powerSum ha r hm
  change ((N * n).factorial : ℂ) * PowerSeries.coeff n (reciprocalSeries N (r : ℂ)) /
      ((N * n).factorial : ℂ) = _
  rw [mul_div_cancel_left₀ _ (by exact_mod_cast (N * n).factorial_ne_zero),
    reciprocalSeries_eq_homogeneous_zero_sums hN]
  exact congrArg (PowerSeries.coeff n) he.symm

/-- Arbitrary complex r has the exact Bell-polynomial continuation of these power sums. -/
theorem reciprocalCoeff_symmetric_polynomial_continuation {N : ℕ} (hN : 2 ≤ N) (n : ℕ) (r : ℂ) :
    reciprocalCoeff N n r = ((N * n).factorial : ℂ) / (n.factorial : ℂ) *
      completeExponentialBell n (fun m => r * ((m - 1).factorial : ℂ) *
        zeroPowerSum (entireReducedDenominator N) m) := reciprocalCoeff_zero_sum_bell hN n r

end
end Komorebi.PaperIV
