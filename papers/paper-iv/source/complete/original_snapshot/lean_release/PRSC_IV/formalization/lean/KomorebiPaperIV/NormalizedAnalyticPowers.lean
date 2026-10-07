/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.NormalizedZeroBell
import Mathlib.Analysis.SpecialFunctions.Complex.Analytic

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

theorem powerSeries_eq_of_derivative_constant {F G : PowerSeries ℂ}
    (h0 : F.constantCoeff = G.constantCoeff) (hd : PowerSeries.derivative ℂ F = PowerSeries.derivative ℂ G) : F = G := by
  ext n
  cases n with
  | zero => simpa only [PowerSeries.coeff_zero_eq_constantCoeff] using h0
  | succ n =>
    have h := congrArg (PowerSeries.coeff n) hd
    simp only [PowerSeries.coeff_derivative] at h
    exact mul_right_cancel₀ (by exact_mod_cast Nat.succ_ne_zero n : (n+1 : ℂ) ≠ 0) h

theorem analyticTaylorSeries_log {f : ℂ → ℂ} (hf : Differentiable ℂ f) (h0 : f 0 = 1) :
    analyticTaylorSeries (fun z => Complex.log (f z)) = PowerSeries.logOf (analyticTaylorSeries f) := by
  let L : ℂ → ℂ := fun z => Complex.log (f z)
  have hslit : f 0 ∈ Complex.slitPlane := by rw [h0]; simp
  have hL : AnalyticAt ℂ L 0 := (analyticAt_clog hslit).comp (hf.analyticAt 0)
  have he : (fun z => f z * deriv L z) =ᶠ[𝓝 0] deriv f := by
    filter_upwards [hf.continuous.continuousAt.preimage_mem_nhds (Complex.isOpen_slitPlane.mem_nhds hslit)] with z hz
    have hd := ((hf z).hasDerivAt.clog hz).deriv
    change deriv L z = deriv f z / f z at hd
    rw [hd]
    field_simp [Complex.slitPlane_ne_zero hz]
  have hprod : analyticTaylorSeries f * PowerSeries.derivative ℂ (analyticTaylorSeries L) =
      PowerSeries.derivative ℂ (analyticTaylorSeries f) := by
    rw [← analyticTaylorSeries_deriv,
      ← analyticTaylorSeries_mul (g := deriv L) (hf.analyticAt 0) hL.deriv,
      analyticTaylorSeries_congr he, analyticTaylorSeries_deriv]
  have hunit : IsUnit (analyticTaylorSeries f) := PowerSeries.isUnit_iff_constantCoeff.mpr (by simp [h0])
  have hc1 : (analyticTaylorSeries f).constantCoeff = 1 := by simp [h0]
  apply powerSeries_eq_of_derivative_constant
  · simp only [analyticTaylorSeries_constantCoeff, h0, Complex.log_one, PowerSeries.constantCoeff_logOf hc1]
  · exact hunit.mul_left_cancel (hprod.trans
      (mul_derivative_logOf (by simpa using h0)).symm)

theorem analyticTaylorSeries_exp {g : ℂ → ℂ} (hg : AnalyticAt ℂ g 0) (h0 : g 0 = 0) :
    analyticTaylorSeries (fun z => Complex.exp (g z)) =
      formalExpFamily (analyticTaylorSeries g) 1 := by
  let E : ℂ → ℂ := fun z => Complex.exp (g z)
  have hE : AnalyticAt ℂ E 0 := hg.cexp
  have he : deriv E =ᶠ[𝓝 0] (fun z => E z * deriv g z) := by
    filter_upwards [hg.eventually_analyticAt] with z hz
    exact hz.differentiableAt.hasDerivAt.cexp.deriv
  have hS0 : (analyticTaylorSeries g).constantCoeff = 0 := by simp [h0]
  apply powerSeries_linear_ode_unique (H := PowerSeries.derivative ℂ (analyticTaylorSeries g))
  · simp [h0, constantCoeff_formalExpFamily_of_zero hS0]
  · rw [← analyticTaylorSeries_deriv, analyticTaylorSeries_congr he,
      analyticTaylorSeries_mul hE hg.deriv, analyticTaylorSeries_deriv]
  · simpa using derivative_formalExpFamily hS0 (1 : ℂ)

/-- Principal logarithm gives the normalized analytic germ at zero. The
Taylor identity proves the full complex-parameter coefficient normalization. -/
def normalizedAnalyticPower (N j : ℕ) (r : ℂ) (w : ℂ) : ℂ :=
  Complex.exp (-r * Complex.log (entireNormalizedSection N j w))

theorem normalizedAnalyticPower_taylor {N : ℕ} (hN : 0 < N) (j : ℕ) (r : ℂ) :
    analyticTaylorSeries (normalizedAnalyticPower N j r) = residuePowerSeries N j r := by
  have hf : Differentiable ℂ (entireNormalizedSection N j) := fun z => (analyticAt_entireNormalizedSection hN j z).differentiableAt
  have hL : AnalyticAt ℂ (fun z => Complex.log (entireNormalizedSection N j z)) 0 :=
    (analyticAt_clog (by rw [entireNormalizedSection_zero]; simp)).comp (hf.analyticAt 0)
  have hG : AnalyticAt ℂ (fun z => -r * Complex.log (entireNormalizedSection N j z)) 0 := analyticAt_const.fun_mul hL
  change analyticTaylorSeries (fun w => Complex.exp (-r * Complex.log (entireNormalizedSection N j w))) = _
  rw [analyticTaylorSeries_exp hG (by simp [entireNormalizedSection_zero]),
    analyticTaylorSeries_mul analyticAt_const hL, analyticTaylorSeries_const,
    analyticTaylorSeries_log hf (entireNormalizedSection_zero N j),
    analyticTaylorSeries_entireNormalizedSection hN, ← normalizedResidueSectionAlg_eq_normalizedResidueSection]
  rw [residuePowerSeries, formalExpFamily_eq_exp_subst
      (by simp [PowerSeries.constantCoeff_logOf (constantCoeff_normalizedResidueSectionAlg (R := ℂ) N j)]),
    formalExpFamily_eq_exp_subst (constantCoeff_normalizedResidueNegativeLog N j)]
  simp [normalizedResidueNegativeLog]

theorem normalizedAnalyticPower_zero_sum_bell {N : ℕ} (hN : 2 ≤ N) (j n : ℕ) (r : ℂ) :
    analyticTaylorCoefficient (normalizedAnalyticPower N j r) n =
      completeExponentialBell n (fun m => r * ((m-1).factorial : ℂ) *
        zeroPowerSum (entireNormalizedSection N j) m) / (n.factorial : ℂ) := by
  have h := residuePowerCoeff_zero_sum_bell hN j n r
  rw [residuePowerCoeff, blockCoeff, ← normalizedAnalyticPower_taylor (by omega), analyticTaylorSeries_coeff] at h
  have hn : ((N*n).factorial : ℂ) ≠ 0 := by exact_mod_cast (N*n).factorial_ne_zero
  apply mul_left_cancel₀ hn
  convert h using 1
  ring

end
end Komorebi.PaperIV
