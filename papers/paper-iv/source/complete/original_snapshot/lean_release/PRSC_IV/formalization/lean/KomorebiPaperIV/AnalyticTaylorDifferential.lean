/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.AnalyticTaylorAlgebra
import KomorebiPaperIV.ThetaZeroBell

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

theorem analyticTaylorSeries_neg (f : ℂ → ℂ) :
    analyticTaylorSeries (fun z => -f z) = -analyticTaylorSeries f := by
  ext n
  simp [analyticTaylorCoefficient, iteratedDeriv_fun_neg, neg_div]

theorem analyticTaylorSeries_deriv (f : ℂ → ℂ) :
    analyticTaylorSeries (deriv f) = PowerSeries.derivative ℂ (analyticTaylorSeries f) := by
  ext n
  rw [analyticTaylorSeries_coeff, analyticTaylorCoefficient, ← iteratedDeriv_succ',
    PowerSeries.coeff_derivative, analyticTaylorSeries_coeff, analyticTaylorCoefficient]
  rw [Nat.factorial_succ, Nat.cast_mul]
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  have hn1 : (n.succ : ℂ) ≠ 0 := by exact_mod_cast n.succ_ne_zero
  field_simp
  simp

theorem analyticTaylorSeries_zeroResolvent {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (h0 : f 0 ≠ 0) :
    analyticTaylorSeries (fun w => ∑' i, zeroPartialFraction f i w) = zeroMomentSeries f := by
  ext n
  rw [analyticTaylorSeries_coeff, analyticTaylorCoefficient, zeroPowerSum_resolvent_derivative hf hs h0]
  simp [zeroMomentSeries, Nat.factorial_ne_zero]

/-- Formal logarithmic differentiation of a proved analytic product, with
Taylor coefficients derived from the actual function. -/
theorem hadamard_taylor_zeroMoment_identity {f : ℂ → ℂ} (hf : Differentiable ℂ f)
    (hs : ZeroPowerSummable f 1) (h0 : f 0 ≠ 0) (hP : f = fullCanonicalProduct f) :
    analyticTaylorSeries f * zeroMomentSeries f = -PowerSeries.derivative ℂ (analyticTaylorSeries f) := by
  let G : ℂ → ℂ := fun w => ∑' i, zeroPartialFraction f i w
  have hG : AnalyticAt ℂ G 0 := zeroResolvent_analyticAt_zero hf hs h0
  have hnear : (fun w => f w * G w) =ᶠ[𝓝 0] (fun w => -deriv f w) := by
    filter_upwards [hf.continuous.continuousAt.eventually_ne h0] with w hw
    have h := fullCanonicalProduct_logDeriv hs h0 (w := w) (fun i he => hw (he ▸ i.1.property))
    have he : logDeriv f w = logDeriv (fullCanonicalProduct f) w := congrArg (fun F => logDeriv F w) hP
    rw [← he] at h
    change -logDeriv f w = G w at h
    rw [← h, logDeriv_apply]
    field_simp
  calc
    _ = analyticTaylorSeries f * analyticTaylorSeries G := by rw [analyticTaylorSeries_zeroResolvent hf hs h0]
    _ = analyticTaylorSeries (fun w => f w * G w) := (analyticTaylorSeries_mul (hf.analyticAt 0) hG).symm
    _ = analyticTaylorSeries (fun w => -deriv f w) := analyticTaylorSeries_congr hnear
    _ = _ := by rw [analyticTaylorSeries_neg, analyticTaylorSeries_deriv]

end
end Komorebi.PaperIV
