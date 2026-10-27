/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroMomentDerivatives
import KomorebiPaperIV.BellCompletion
import KomorebiPaperIV.ReciprocalCompletion

namespace Komorebi.PaperIV
noncomputable section
open Set Filter FormalMultilinearSeries
open scoped Topology

theorem entireReducedDenominator_iteratedDeriv_zero {N : ℕ} (hN : 0 < N) (n : ℕ) :
    iteratedDeriv n (entireReducedDenominator N) 0 =
      (n.factorial : ℂ) * PowerSeries.coeff n (reducedDenominator (R := ℂ) N) := by
  let p := ofScalars ℂ (fun n => PowerSeries.coeff n (reducedDenominator (R := ℂ) N))
  have hp : HasFPowerSeriesAt (entireReducedDenominator N) p 0 :=
    (p.hasFPowerSeriesOnBall (by dsimp [p]; rw [reducedDenominator_entire_radius hN]; simp)).hasFPowerSeriesAt
  have he := hp.eq_formalMultilinearSeries (analyticAt_entireReducedDenominator hN 0).hasFPowerSeriesAt
  have hc := congrArg (fun q : FormalMultilinearSeries ℂ ℂ ℂ => q.coeff n) he
  simp only [p, coeff_ofScalars] at hc
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  exact ((div_eq_iff hn).mp hc.symm).trans (mul_comm _ _)

theorem zeroResolvent_analyticAt_zero {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (h0 : f 0 ≠ 0) :
    AnalyticAt ℂ (fun w => ∑' i, zeroPartialFraction f i w) 0 := by
  have hU : IsOpen {w : ℂ | f w ≠ 0} := isOpen_ne_fun hf.continuous continuous_const
  have h := (zeroPartialFraction_locally_uniform hs h0).mono (subset_univ {w : ℂ | f w ≠ 0})
  apply (h.differentiableOn ?_ hU).analyticAt (hU.mem_nhds h0)
  apply Eventually.of_forall
  intro S
  apply DifferentiableOn.fun_sum
  intro i _ w hw
  have hn : w ≠ indexedZero i := by intro he; apply hw; rw [he]; exact i.1.property
  exact ((hasDerivAt_const w (1 : ℂ)).div
    ((hasDerivAt_const w (indexedZero i)).sub (hasDerivAt_id w))
    (sub_ne_zero.mpr hn.symm)).differentiableAt.differentiableWithinAt

/-- Newton's convolution for the actual complex zero power sums, obtained by
differentiating the proved analytic partial-fraction identity at zero. -/
theorem reducedZeroPowerSum_convolution {N : ℕ} (hN : 2 ≤ N) (n : ℕ) :
    (∑ k ∈ Finset.range (n + 1),
      PowerSeries.coeff k (reducedDenominator (R := ℂ) N) *
        zeroPowerSum (entireReducedDenominator N) (n - k + 1)) =
      -(PowerSeries.coeff (n + 1) (reducedDenominator (R := ℂ) N) * (n + 1 : ℂ)) := by
  let f := entireReducedDenominator N
  let G : ℂ → ℂ := fun w => ∑' i, zeroPartialFraction f i w
  have hf : Differentiable ℂ f := fun z => (analyticAt_entireReducedDenominator (by omega) z).differentiableAt
  have hs := entireReducedDenominator_reciprocal_zeros_summable hN
  have h0 : f 0 ≠ 0 := by dsimp [f]; rw [entireReducedDenominator_zero]; exact one_ne_zero
  have hG : AnalyticAt ℂ G 0 := zeroResolvent_analyticAt_zero hf hs h0
  have hnear : f * G =ᶠ[𝓝 0] -deriv f := by
    filter_upwards [hf.continuous.continuousAt.eventually_ne h0] with w hw
    have h := entireReducedDenominator_partialFractions hN hw
    change -logDeriv f w = G w at h
    change f w * G w = -deriv f w
    rw [← h, logDeriv_apply]
    field_simp
  have he := hnear.iteratedDeriv_eq n
  rw [iteratedDeriv_mul (hf.analyticAt 0).contDiffAt hG.contDiffAt,
    iteratedDeriv_neg, ← iteratedDeriv_succ'] at he
  simp only [f, entireReducedDenominator_iteratedDeriv_zero (show 0 < N by omega)] at he
  have hGD (k : ℕ) : iteratedDeriv k G 0 =
      (k.factorial : ℂ) * zeroPowerSum f (k + 1) := zeroPowerSum_resolvent_derivative hf hs h0 k
  simp only [hGD] at he
  have hsimp : (∑ k ∈ Finset.range (n + 1),
      (n.choose k : ℂ) * ((k.factorial : ℂ) * PowerSeries.coeff k (reducedDenominator (R := ℂ) N)) *
        ((n - k).factorial : ℂ) * zeroPowerSum f (n - k + 1)) =
      (n.factorial : ℂ) * ∑ k ∈ Finset.range (n + 1),
        PowerSeries.coeff k (reducedDenominator (R := ℂ) N) * zeroPowerSum f (n - k + 1) := by
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k hk
    have hk' : k ≤ n := by simpa only [Finset.mem_range, Nat.lt_succ_iff] using hk
    have hfac : (n.choose k : ℂ) * (k.factorial : ℂ) * ((n - k).factorial : ℂ) = (n.factorial : ℂ) := by
      exact_mod_cast Nat.choose_mul_factorial_mul_factorial hk'
    linear_combination (PowerSeries.coeff k (reducedDenominator (R := ℂ) N) * zeroPowerSum f (n - k + 1)) * hfac
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  apply mul_left_cancel₀ hn
  dsimp [f] at hsimp
  rw [← hsimp]
  have hfac : ((n + 1).factorial : ℂ) = (n + 1 : ℂ) * (n.factorial : ℂ) := by
    simp only [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
  rw [hfac] at he
  dsimp [f] at he
  simpa only [mul_assoc, mul_comm, mul_left_comm, mul_neg] using he

def zeroMomentSeries (f : ℂ → ℂ) : PowerSeries ℂ :=
  PowerSeries.mk (fun n => zeroPowerSum f (n + 1))

theorem reducedDenominator_mul_zeroMomentSeries {N : ℕ} (hN : 2 ≤ N) :
    reducedDenominator (R := ℂ) N * zeroMomentSeries (entireReducedDenominator N) =
      -PowerSeries.derivative ℂ (reducedDenominator N) := by
  ext n
  rw [PowerSeries.coeff_mul, map_neg, PowerSeries.coeff_derivative]
  simp only [zeroMomentSeries, PowerSeries.coeff_mk]
  rw [Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk]
  exact reducedZeroPowerSum_convolution hN n

/-- Every formal logarithmic coefficient equals the actual zero power sum. -/
theorem kappaCoeff_eq_zeroPowerSum {N m : ℕ} (hN : 2 ≤ N) (hm : 0 < m) :
    kappaCoeff (R := ℂ) N m = zeroPowerSum (entireReducedDenominator N) m := by
  have hu : IsUnit (reducedDenominator (R := ℂ) N) :=
    PowerSeries.isUnit_iff_constantCoeff.mpr (by rw [constantCoeff_reducedDenominator]; exact isUnit_one)
  have he : zeroMomentSeries (entireReducedDenominator N) = reducedTangentSeries (R := ℂ) N :=
    hu.mul_left_cancel ((reducedDenominator_mul_zeroMomentSeries hN).trans
      (reducedDenominator_mul_reducedTangentSeries (R := ℂ) N).symm)
  obtain ⟨n, rfl⟩ := Nat.exists_eq_succ_of_ne_zero hm.ne'
  have hc := congrArg (PowerSeries.coeff n) he
  simpa only [zeroMomentSeries, PowerSeries.coeff_mk, coeff_reducedTangentSeries] using hc.symm

theorem reducedZeroPowerSum_newton {N : ℕ} (hN : 2 ≤ N) (n : ℕ) :
    zeroPowerSum (entireReducedDenominator N) (n + 1) =
      -((n + 1 : ℂ) * PowerSeries.coeff (n + 1) (reducedDenominator (R := ℂ) N)) -
      ∑ k ∈ Finset.range n, PowerSeries.coeff (k + 1) (reducedDenominator (R := ℂ) N) *
        zeroPowerSum (entireReducedDenominator N) (n - k) := by
  have h := reducedZeroPowerSum_convolution hN n
  rw [Finset.sum_range_succ'] at h
  simp only [Nat.sub_zero, PowerSeries.coeff_zero_eq_constantCoeff, constantCoeff_reducedDenominator, one_mul] at h
  have he : (∑ k ∈ Finset.range n,
      PowerSeries.coeff (k + 1) (reducedDenominator (R := ℂ) N) *
        zeroPowerSum (entireReducedDenominator N) (n - (k + 1) + 1)) =
      ∑ k ∈ Finset.range n,
      PowerSeries.coeff (k + 1) (reducedDenominator (R := ℂ) N) *
        zeroPowerSum (entireReducedDenominator N) (n - k) := by
    apply Finset.sum_congr rfl
    intro k hk
    rw [show n - (k + 1) + 1 = n - k by have := Finset.mem_range.mp hk; omega]
  rw [he] at h
  linear_combination h

/-- Corollary 12.9 in exactly the manuscript's factorial normalization. -/
theorem transferTangentCoeff_zero_sum {N : ℕ} (hN : 2 ≤ N) (n : ℕ) :
    transferTangentCoeff (R := ℂ) N n =
      (N : ℂ) * ((N * n + N - 1).factorial : ℂ) * zeroPowerSum (entireReducedDenominator N) (n + 1) := by
  rw [transferTangentCoeff_eq_kappa, kappaCoeff_eq_zeroPowerSum hN (by omega)]

theorem bellInput_zero_sums {N : ℕ} (hN : 2 ≤ N) (r : ℂ) :
    bellInput (fun m => r * ((m - 1).factorial : ℂ) * kappaCoeff N m) =
      bellInput (fun m => r * ((m - 1).factorial : ℂ) * zeroPowerSum (entireReducedDenominator N) m) := by
  ext m
  simp only [bellInput, PowerSeries.coeff_mk]
  split_ifs with hm
  · rfl
  · rw [kappaCoeff_eq_zeroPowerSum hN (Nat.pos_of_ne_zero hm)]

/-- Corollary 12.10: reciprocal coefficients from the genuine zero multiset. -/
theorem reciprocalCoeff_zero_sum_bell {N : ℕ} (hN : 2 ≤ N) (n : ℕ) (r : ℂ) :
    reciprocalCoeff N n r =
      ((N * n).factorial : ℂ) / (n.factorial : ℂ) * completeExponentialBell n
        (fun m => r * ((m - 1).factorial : ℂ) * zeroPowerSum (entireReducedDenominator N) m) := by
  rw [reciprocalCoeff_bell_formula, completeExponentialBell, bellInput_zero_sums hN]
  rfl

end
end Komorebi.PaperIV
