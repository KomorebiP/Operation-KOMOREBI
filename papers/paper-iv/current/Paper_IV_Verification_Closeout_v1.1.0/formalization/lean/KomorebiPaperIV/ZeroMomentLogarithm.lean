/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.ZeroMomentCoefficients

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric FormalMultilinearSeries
open scoped Topology NNReal

/-- Taylor convergence throughout an open complex disk, with the radius
proved by Cauchy's formula on each smaller closed disk. -/
theorem differentiableOn_ball_taylor_hasSum {f : ℂ → ℂ} {R : ℝ}
    (hf : DifferentiableOn ℂ f (ball 0 R)) {w : ℂ} (hw : w ∈ ball 0 R) :
    HasSum (fun n => iteratedDeriv n f 0 / (n.factorial : ℂ) * w ^ n) (f w) := by
  have hwR : ‖w‖ < R := mem_ball_zero_iff.mp hw
  obtain ⟨S, hwS, hSR⟩ := exists_between hwR
  have hS : 0 < S := lt_of_le_of_lt (norm_nonneg w) hwS
  let s : ℝ≥0 := ⟨S, hS.le⟩
  have hd : DifferentiableOn ℂ f (closedBall 0 (s : ℝ)) :=
    hf.mono (fun z hz => mem_ball_zero_iff.mpr ((mem_closedBall_zero_iff.mp hz).trans_lt hSR))
  have hp := hd.hasFPowerSeriesOnBall (show 0 < s from hS)
  have he := hp.hasFPowerSeriesAt.eq_formalMultilinearSeries
    (hf.analyticAt (isOpen_ball.mem_nhds (mem_ball_self (hS.trans hSR)))).hasFPowerSeriesAt
  rw [he] at hp
  have h := hp.hasSum_sub (show w ∈ eball (0 : ℂ) (s : ENNReal) by
    rw [eball_coe]; exact mem_ball_zero_iff.mpr hwS)
  simpa only [sub_zero, ofScalars_apply_eq', smul_eq_mul, mul_comm] using h

/-- On every zero-free disk the normalized negative logarithm has exactly
the zero-moment Taylor series. The logarithm is the analytic branch with
value zero at the origin, rather than an unrestricted principal logarithm. -/
theorem reducedZeroPowerSum_logarithm {N : ℕ} (hN : 2 ≤ N) {R : ℝ} (hR : 0 < R)
    (hn : ∀ w ∈ ball (0 : ℂ) R, entireReducedDenominator N w ≠ 0) :
    ∃ L : ℂ → ℂ, DifferentiableOn ℂ L (ball 0 R) ∧ L 0 = 0 ∧
      (∀ w ∈ ball (0 : ℂ) R, Complex.exp (-L w) = entireReducedDenominator N w) ∧
      ∀ w ∈ ball (0 : ℂ) R,
        HasSum (fun m => zeroPowerSum (entireReducedDenominator N) m * w ^ m / (m : ℂ)) (L w) := by
  let f := entireReducedDenominator N
  let G : ℂ → ℂ := fun w => ∑' i, zeroPartialFraction f i w
  have hf : Differentiable ℂ f := fun z => (analyticAt_entireReducedDenominator (by omega) z).differentiableAt
  have hs := entireReducedDenominator_reciprocal_zeros_summable hN
  have h0 : f 0 ≠ 0 := by dsimp [f]; rw [entireReducedDenominator_zero]; exact one_ne_zero
  have hG : DifferentiableOn ℂ G (ball 0 R) := by
    have he : EqOn G (fun w => -logDeriv f w) (ball 0 R) :=
      fun w hw => (entireReducedDenominator_partialFractions hN (hn w hw)).symm
    apply DifferentiableOn.congr _ he
    intro w hw
    exact (((hf.analyticAt w).deriv.differentiableAt.div (hf w) (hn w hw)).neg).differentiableWithinAt
  obtain ⟨L, hL0, hL⟩ := hG.isExactOn_ball.with_val_at 0 0
  have hLd : DifferentiableOn ℂ L (ball 0 R) := fun w hw => (hL w hw).differentiableAt.differentiableWithinAt
  have hH : ∀ w ∈ ball (0 : ℂ) R, HasDerivAt (fun z => f z * Complex.exp (L z)) 0 w := by
    intro w hw
    have he : G w = -logDeriv f w := (entireReducedDenominator_partialFractions hN (hn w hw)).symm
    convert! (hf w).hasDerivAt.mul (hL w hw).cexp using 1
    rw [he, logDeriv_apply]
    field_simp [show f w ≠ 0 from hn w hw]
    ring
  have hExp : ∀ w ∈ ball (0 : ℂ) R, Complex.exp (-L w) = f w := by
    intro w hw
    have he := isOpen_ball.is_const_of_deriv_eq_zero (convex_ball (0 : ℂ) R).isPreconnected
      (fun z hz => (hH z hz).differentiableAt.differentiableWithinAt)
      (fun z hz => (hH z hz).deriv) hw (mem_ball_self hR)
    simp only [f, entireReducedDenominator_zero, hL0, Complex.exp_zero, one_mul] at he
    rw [Complex.exp_neg]
    exact (eq_inv_of_mul_eq_one_left he).symm
  have hcoeff (n : ℕ) : iteratedDeriv n L 0 / (n.factorial : ℂ) = zeroPowerSum f n / (n : ℂ) := by
    cases n with
    | zero => simp [hL0]
    | succ n =>
      have he : deriv L =ᶠ[𝓝 0] G := by
        filter_upwards [isOpen_ball.mem_nhds (mem_ball_self hR)] with w hw
        exact (hL w hw).deriv
      rw [iteratedDeriv_succ', he.iteratedDeriv_eq n,
        zeroPowerSum_resolvent_derivative hf hs h0 n]
      have hfac : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
      simp only [Nat.factorial_succ, Nat.cast_mul, Nat.cast_add, Nat.cast_one]
      field_simp
  refine ⟨L, hLd, hL0, hExp, fun w hw => ?_⟩
  have ht := differentiableOn_ball_taylor_hasSum hLd hw
  simp only [hcoeff] at ht
  simpa only [div_mul_eq_mul_div] using ht

/-- The analytic resolvent realizes the same coefficients as the formal
logarithmic derivative throughout any zero-free disk. -/
theorem reducedZeroPowerSum_resolvent_hasSum {N : ℕ} (hN : 2 ≤ N) {R : ℝ}
    (hn : ∀ w ∈ ball (0 : ℂ) R, entireReducedDenominator N w ≠ 0)
    {w : ℂ} (hw : w ∈ ball (0 : ℂ) R) :
    HasSum (fun n => zeroPowerSum (entireReducedDenominator N) (n + 1) * w ^ n)
      (-logDeriv (entireReducedDenominator N) w) := by
  let f := entireReducedDenominator N
  let G : ℂ → ℂ := fun w => ∑' i, zeroPartialFraction f i w
  have hf : Differentiable ℂ f := fun z => (analyticAt_entireReducedDenominator (by omega) z).differentiableAt
  have hs := entireReducedDenominator_reciprocal_zeros_summable hN
  have h0 : f 0 ≠ 0 := by dsimp [f]; rw [entireReducedDenominator_zero]; exact one_ne_zero
  have hG : DifferentiableOn ℂ G (ball 0 R) := by
    apply DifferentiableOn.congr _ (fun z hz => (entireReducedDenominator_partialFractions hN (hn z hz)).symm)
    intro z hz
    exact (((hf.analyticAt z).deriv.differentiableAt.div (hf z) (hn z hz)).neg).differentiableWithinAt
  have ht := differentiableOn_ball_taylor_hasSum hG hw
  have hc (n : ℕ) : iteratedDeriv n G 0 / (n.factorial : ℂ) = zeroPowerSum f (n + 1) := by
    rw [zeroPowerSum_resolvent_derivative hf hs h0 n]
    exact mul_div_cancel_left₀ _ (by exact_mod_cast n.factorial_ne_zero)
  simp only [hc] at ht
  rwa [entireReducedDenominator_partialFractions hN (hn w hw)]

/-- The factorial-normalized tangent coefficients are coefficients of the
actual analytic tangent, not merely of an unrelated formal series. -/
theorem analyticTransferTangent_coefficient_hasSum {N : ℕ} (hN : 2 ≤ N) {R : ℝ}
    (hn : ∀ w ∈ ball (0 : ℂ) R, entireReducedDenominator N w ≠ 0)
    {z : ℂ} (hz : z ^ N ∈ ball (0 : ℂ) R) :
    HasSum (fun n => transferTangentCoeff (R := ℂ) N n /
      ((N * n + N - 1).factorial : ℂ) * z ^ (N * n + N - 1))
      (analyticTransferTangent N z) := by
  have ht := (reducedZeroPowerSum_resolvent_hasSum hN hn hz).mul_left ((N : ℂ) * z ^ (N - 1))
  rw [← analyticTransferTangent_eq_reduced_logDeriv (show 0 < N by omega)] at ht
  convert! ht using 1
  funext n
  rw [transferTangentCoeff_zero_sum hN]
  have hfac : ((N * n + N - 1).factorial : ℂ) ≠ 0 := by exact_mod_cast (N * n + N - 1).factorial_ne_zero
  field_simp
  rw [show N * n + N - 1 = N * n + (N - 1) by omega, pow_add, pow_mul]
  ring

end
end Komorebi.PaperIV
