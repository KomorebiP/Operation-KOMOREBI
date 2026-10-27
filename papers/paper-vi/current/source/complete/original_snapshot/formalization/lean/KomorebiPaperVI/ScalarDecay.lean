import Mathlib.Analysis.SpecialFunctions.Gaussian.GaussianIntegral
import Mathlib.Analysis.SpecialFunctions.ImproperIntegrals
import Mathlib.Analysis.SpecialFunctions.Pow.Asymptotics

/-! Author: Komorebi P. Complex exponential-polynomial decay and actual integrability. -/
namespace KomorebiPaperVI.ScalarDecay
open Set Filter MeasureTheory
open scoped Topology
set_option backward.isDefEq.respectTransparency false

theorem norm_exp_pow (a : ℂ) (k : ℕ) (t : ℝ) (ht : 0 ≤ t) :
    ‖Complex.exp (a*t)*(t:ℂ)^k‖=t^k*Real.exp (a.re*t) := by
  simp [Complex.norm_exp,Complex.mul_re,Complex.norm_real,Real.norm_eq_abs,
    abs_of_nonneg ht,mul_comm]

theorem exp_pow_integrable (a : ℂ) (ha : a.re < 0) (k : ℕ) :
    IntegrableOn (fun t : ℝ => Complex.exp (a*t)*(t:ℂ)^k) (Ioi 0) := by
  have hi := integrableOn_rpow_mul_exp_neg_mul_rpow
    (s := (k:ℝ)) (p := (1:ℝ)) (b := -a.re) (by linarith [Nat.cast_nonneg (α := ℝ) k]) zero_lt_one (by linarith)
  simp only [Real.rpow_natCast,Real.rpow_one,neg_neg] at hi
  apply hi.mono' (by fun_prop)
  filter_upwards [ae_restrict_mem measurableSet_Ioi] with t ht
  rw [norm_exp_pow a k t ht.le]

theorem exp_pow_tendsto_zero (a : ℂ) (ha : a.re < 0) (k : ℕ) :
    Tendsto (fun t : ℝ => Complex.exp (a*t)*(t:ℂ)^k) atTop (𝓝 0) := by
  apply tendsto_zero_iff_norm_tendsto_zero.mpr
  have hh := tendsto_rpow_mul_exp_neg_mul_atTop_nhds_zero (k:ℝ) (-a.re) (by linarith)
  simp only [Real.rpow_natCast,neg_neg] at hh
  apply hh.congr'
  filter_upwards [eventually_ge_atTop (0:ℝ)] with t ht
  exact (norm_exp_pow a k t ht).symm

end KomorebiPaperVI.ScalarDecay
