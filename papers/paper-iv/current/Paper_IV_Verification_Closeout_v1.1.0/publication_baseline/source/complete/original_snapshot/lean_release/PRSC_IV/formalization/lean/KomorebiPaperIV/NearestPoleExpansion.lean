/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.PoleTaylor

namespace Komorebi.PaperIV
noncomputable section
open Set Filter Metric
open scoped Topology Classical

theorem removedPoleRemainder_taylor {f : ℂ → ℂ} (hf : Differentiable ℂ f) (hf0 : f 0 ≠ 0)
    {S : Finset ℂ} (hS : ∀ ρ ∈ S, ρ ≠ 0) (a : ℂ → ℕ → ℂ) (r m : ℕ) :
    analyticTaylorCoefficient (removedPoleRemainder f S a r) m =
      analyticTaylorCoefficient (fun z => (f z ^ r)⁻¹) m -
        ∑ ρ ∈ S, ∑ k ∈ Finset.range r, a ρ (k+1) * ((m+k).choose k : ℂ) * ρ⁻¹ ^ m := by
  have h0 : (0 : ℂ) ∉ S := fun h => hS 0 h rfl
  have hnear : removedPoleRemainder f S a r =ᶠ[𝓝 0] rawPoleRemainder f S a r := by
    filter_upwards [hf.continuous.continuousAt.eventually_ne hf0,
      S.finite_toSet.isClosed.isOpen_compl.mem_nhds h0] with z hz hzs
    exact removedPoleRemainder_eq_raw hf hS a r hz hzs
  have hp (ρ : ℂ) (hρ : ρ ∈ S) : AnalyticAt ℂ (polePrincipalPart a r ρ) 0 :=
    polePrincipalPart_analyticAt (hS ρ hρ) (hS ρ hρ).symm a r
  rw [← analyticTaylorSeries_coeff]
  rw [analyticTaylorSeries_congr hnear]
  change PowerSeries.coeff m (analyticTaylorSeries (fun z => (f z ^ r)⁻¹ -
    ∑ ρ ∈ S, polePrincipalPart a r ρ z)) = _
  rw [
    analyticTaylorSeries_sub (f := fun z => (f z ^ r)⁻¹)
      (by simpa only using! (((hf.analyticAt 0).pow r).inv (pow_ne_zero r hf0)))
      (Finset.analyticAt_fun_sum _ hp),
    analyticTaylorSeries_finsetSum S hp, map_sub, map_sum, analyticTaylorSeries_coeff]
  congr 1
  apply Finset.sum_congr rfl
  intro ρ hρ
  simpa only [analyticTaylorSeries_coeff] using analyticTaylorCoefficient_principalPart (hS ρ hρ) a r m

/-- The complete finite principal-part expansion with an explicit Cauchy
constant, valid for every coefficient. The local O(1) assumptions are exactly
the meaning of the principal parts specified in Theorem 13.1. -/
theorem nearest_pole_taylor_bound {f : ℂ → ℂ} (hf : Differentiable ℂ f) (hf0 : f 0 ≠ 0)
    {S : Finset ℂ} (hS : ∀ ρ ∈ S, ρ ≠ 0) (a : ℂ → ℕ → ℂ) (r : ℕ)
    {R R₂ : ℝ} (hR : 0 < R) (hR₂ : R < R₂)
    (hzeros : ∀ z : ℂ, ‖z‖ < R₂ → f z = 0 → z ∈ S)
    (hlocal : ∀ ρ ∈ S, ∃ C : ℝ, ∀ᶠ z in 𝓝[≠] ρ,
      ‖(f z ^ r)⁻¹ - polePrincipalPart a r ρ z‖ ≤ C) :
    ∃ C : ℝ, ∀ m : ℕ,
      ‖analyticTaylorCoefficient (fun z => (f z ^ r)⁻¹) m -
        ∑ ρ ∈ S, ∑ k ∈ Finset.range r, a ρ (k+1) * ((m+k).choose k : ℂ) * ρ⁻¹ ^ m‖ ≤ C / R ^ m := by
  let H := removedPoleRemainder f S a r
  have hH : AnalyticOnNhd ℂ H (ball 0 R₂) := removedPoleRemainder_analyticOnNhd hf hS a r
    (fun z hz => hzeros z (mem_ball_zero_iff.mp hz)) hlocal
  have hdiff : DiffContOnCl ℂ H (ball 0 R) := hH.differentiableOn.diffContOnCl_ball
    (fun z hz => mem_ball_zero_iff.mpr ((mem_closedBall_zero_iff.mp hz).trans_lt hR₂))
  have hc : ContinuousOn H (sphere 0 R) := hH.continuousOn.mono
    (fun z hz => mem_ball_zero_iff.mpr ((by simpa only [mem_sphere, dist_zero_right] using hz : ‖z‖ = R).trans_lt hR₂))
  obtain ⟨C, hC⟩ := (isCompact_sphere (0 : ℂ) R).bddAbove_image hc.norm
  refine ⟨C, fun m => ?_⟩
  rw [← removedPoleRemainder_taylor hf hf0 hS a r m]
  exact analyticTaylorCoefficient_norm_le hR hdiff (fun z hz => hC (mem_image_of_mem _ hz)) m

theorem reciprocalCoeff_nearest_pole_bound {N : ℕ} (hN : 0 < N)
    {S : Finset ℂ} (hS : ∀ ρ ∈ S, ρ ≠ 0) (a : ℂ → ℕ → ℂ) (r : ℕ)
    {R R₂ : ℝ} (hR : 0 < R) (hR₂ : R < R₂)
    (hzeros : ∀ z : ℂ, ‖z‖ < R₂ → canonicalSignedDenominator N z = 0 → z ∈ S)
    (hlocal : ∀ ρ ∈ S, ∃ C : ℝ, ∀ᶠ z in 𝓝[≠] ρ,
      ‖(canonicalSignedDenominator N z ^ r)⁻¹ - polePrincipalPart a r ρ z‖ ≤ C) :
    ∃ C : ℝ, ∀ n : ℕ,
      ‖reciprocalCoeff N n (r : ℂ) - ((N*n).factorial : ℂ) *
        ∑ ρ ∈ S, ∑ k ∈ Finset.range r, a ρ (k+1) * ((N*n+k).choose k : ℂ) * ρ⁻¹ ^ (N*n)‖ ≤
      C * ((N*n).factorial : ℝ) * R⁻¹ ^ (N*n) := by
  have hf : Differentiable ℂ (canonicalSignedDenominator N) := fun z => (analyticAt_entireSigned ..).differentiableAt
  obtain ⟨C, hC⟩ := nearest_pole_taylor_bound hf (by rw [canonicalSignedDenominator_zero hN]; exact one_ne_zero)
    hS a r hR hR₂ hzeros hlocal
  refine ⟨C, fun n => ?_⟩
  rw [reciprocalCoeff_analyticTaylor hN, ← mul_sub, norm_mul, Complex.norm_natCast]
  have h := mul_le_mul_of_nonneg_left (hC (N*n)) (show (0 : ℝ) ≤ (N*n).factorial by positivity)
  simpa only [div_eq_mul_inv, inv_pow, mul_assoc, mul_comm, mul_left_comm] using h

end
end Komorebi.PaperIV
