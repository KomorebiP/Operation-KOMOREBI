/-
Copyright (c) 2026 Komorebi P. All rights reserved.
Authors: Komorebi P.
-/
import KomorebiPaperIV.PoleCoefficientBounds
import Mathlib.RingTheory.PowerSeries.Basic
import Mathlib.Analysis.Analytic.IteratedFDeriv

namespace Komorebi.PaperIV
noncomputable section
open Set Filter
open scoped Topology

def analyticTaylorSeries (f : ℂ → ℂ) : PowerSeries ℂ := PowerSeries.mk (analyticTaylorCoefficient f)

@[simp] theorem analyticTaylorSeries_coeff (f : ℂ → ℂ) (n : ℕ) :
    PowerSeries.coeff n (analyticTaylorSeries f) = analyticTaylorCoefficient f n := by
  simp [analyticTaylorSeries]

@[simp] theorem analyticTaylorSeries_constantCoeff (f : ℂ → ℂ) :
    (analyticTaylorSeries f).constantCoeff = f 0 := by simp [analyticTaylorSeries, analyticTaylorCoefficient]

theorem analyticTaylorSeries_congr {f g : ℂ → ℂ} (h : f =ᶠ[𝓝 0] g) :
    analyticTaylorSeries f = analyticTaylorSeries g := by
  ext n
  simp only [analyticTaylorSeries_coeff, analyticTaylorCoefficient, h.iteratedDeriv_eq n]

theorem analyticTaylorSeries_mul {f g : ℂ → ℂ} (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0) :
    analyticTaylorSeries (fun z => f z * g z) = analyticTaylorSeries f * analyticTaylorSeries g := by
  ext n
  rw [analyticTaylorSeries_coeff, analyticTaylorCoefficient,
    iteratedDeriv_fun_mul hf.contDiffAt hg.contDiffAt, PowerSeries.coeff_mul,
    Finset.Nat.sum_antidiagonal_eq_sum_range_succ_mk, Finset.sum_div]
  apply Finset.sum_congr rfl
  intro k hk
  have hkn : k ≤ n := Nat.le_of_lt_succ (Finset.mem_range.mp hk)
  have hfac : (n.choose k : ℂ) * (k.factorial : ℂ) * ((n - k).factorial : ℂ) = n.factorial := by
    exact_mod_cast Nat.choose_mul_factorial_mul_factorial hkn
  simp only [analyticTaylorSeries_coeff, analyticTaylorCoefficient]
  have hn : (n.factorial : ℂ) ≠ 0 := by exact_mod_cast n.factorial_ne_zero
  have hk0 : (k.factorial : ℂ) ≠ 0 := by exact_mod_cast k.factorial_ne_zero
  have hnk : ((n-k).factorial : ℂ) ≠ 0 := by exact_mod_cast (n-k).factorial_ne_zero
  field_simp
  linear_combination (iteratedDeriv k f 0 * iteratedDeriv (n-k) g 0) * hfac

theorem analyticTaylorSeries_add {f g : ℂ → ℂ} (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0) :
    analyticTaylorSeries (fun z => f z + g z) = analyticTaylorSeries f + analyticTaylorSeries g := by
  ext n
  simp [analyticTaylorCoefficient, iteratedDeriv_fun_add hf.contDiffAt hg.contDiffAt, add_div]

@[simp] theorem analyticTaylorSeries_const (c : ℂ) :
    analyticTaylorSeries (fun _ => c) = PowerSeries.C c := by
  ext n
  cases n with
  | zero => simp [analyticTaylorCoefficient]
  | succ n => simp [analyticTaylorCoefficient, iteratedDeriv_const]

theorem analyticTaylorSeries_pow {f : ℂ → ℂ} (hf : AnalyticAt ℂ f 0) (r : ℕ) :
    analyticTaylorSeries (fun z => f z ^ r) = analyticTaylorSeries f ^ r := by
  induction r with
  | zero => simp
  | succ r ih => simp_rw [pow_succ]; rw [analyticTaylorSeries_mul (f := fun z => f z ^ r) (by fun_prop) hf, ih]

theorem analyticTaylorSeries_inverse_product {f : ℂ → ℂ} (hf : AnalyticAt ℂ f 0) (h0 : f 0 ≠ 0) :
    analyticTaylorSeries f * analyticTaylorSeries (fun z => (f z)⁻¹) = 1 := by
  rw [← analyticTaylorSeries_mul (g := fun z => (f z)⁻¹) hf (by fun_prop)]
  have h : (fun z => f z * (f z)⁻¹) =ᶠ[𝓝 0] (fun _ => (1 : ℂ)) := by
    filter_upwards [hf.continuousAt.eventually_ne h0] with z hz
    exact mul_inv_cancel₀ hz
  rw [analyticTaylorSeries_congr h]
  simp

end
end Komorebi.PaperIV
