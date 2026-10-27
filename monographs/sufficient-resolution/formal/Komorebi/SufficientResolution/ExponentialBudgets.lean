import Mathlib.Analysis.SpecialFunctions.ExpDeriv
import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Positivity
import Mathlib.Tactic.Ring

/-! # Exact scalar response of two exponential growth envelopes -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ExponentialBudgets

open MeasureTheory

def kernel (a b t s : ℝ) : ℝ := Real.exp (b*(t-s)) * Real.exp (a*s)

def response (a b t : ℝ) : ℝ := ∫ s in (0:ℝ)..t, kernel a b t s

theorem continuous_kernel (a b t : ℝ) : Continuous (kernel a b t) :=
  (Real.continuous_exp.comp (continuous_const.mul (continuous_const.sub continuous_id))).mul
    (Real.continuous_exp.comp (continuous_const.mul continuous_id))

@[simp] theorem response_zero (a b : ℝ) : response a b 0 = 0 := by
  simp [response]

theorem kernel_pos (a b t s : ℝ) : 0 < kernel a b t s := by
  unfold kernel
  positivity

theorem response_nonneg (a b t : ℝ) (ht : 0 ≤ t) : 0 ≤ response a b t := by
  exact intervalIntegral.integral_nonneg ht (fun s _ => (kernel_pos a b t s).le)

theorem kernel_derivative (a b t s : ℝ) :
    HasDerivAt (kernel a b t) ((a-b)*kernel a b t s) s := by
  have h₁ := ((hasDerivAt_const s b).mul
    ((hasDerivAt_const s t).sub (hasDerivAt_id s))).exp
  have h₂ := ((hasDerivAt_const s a).mul (hasDerivAt_id s)).exp
  convert h₁.mul h₂ using 1
  all_goals first | rfl | (dsimp [kernel]; ring)

/-- Distinct rates, valid for oriented integrals at all real times. -/
theorem response_of_ne (a b t : ℝ) (h : a ≠ b) :
    response a b t = (Real.exp (a*t) - Real.exp (b*t))/(a-b) := by
  have hab : a-b ≠ 0 := sub_ne_zero.mpr h
  have hd : ∀ s, HasDerivAt (fun u => kernel a b t u / (a-b)) (kernel a b t s) s := by
    intro s
    simpa [hab] using (kernel_derivative a b t s).div_const (a-b)
  have hf := intervalIntegral.integral_eq_sub_of_hasDerivAt
    (fun s _ => hd s) ((continuous_kernel a b t).intervalIntegrable 0 t)
  unfold response
  rw [hf]
  simp only [kernel, sub_self, sub_zero, mul_zero, Real.exp_zero, one_mul, mul_one]
  ring

theorem kernel_equal (a t s : ℝ) : kernel a a t s = Real.exp (a*t) := by
  rw [kernel, ← Real.exp_add]
  congr 1
  ring

/-- Equal-rate limit with no division by a-b. -/
theorem response_self (a t : ℝ) : response a a t = t * Real.exp (a*t) := by
  unfold response
  simp only [kernel_equal, intervalIntegral.integral_const, sub_zero, smul_eq_mul]

@[simp] theorem response_zero_rates (t : ℝ) : response 0 0 t = t := by
  simp [response_self]

theorem kernel_mono (a b a' b' t s : ℝ) (ha : a ≤ a') (hb : b ≤ b')
    (hs : s ∈ Set.Icc 0 t) : kernel a b t s ≤ kernel a' b' t s := by
  apply mul_le_mul
  · exact Real.exp_le_exp.mpr (mul_le_mul_of_nonneg_right hb (sub_nonneg.mpr hs.2))
  · exact Real.exp_le_exp.mpr (mul_le_mul_of_nonneg_right ha hs.1)
  · exact (Real.exp_pos _).le
  · exact (Real.exp_pos _).le

theorem response_mono (a b a' b' t : ℝ) (ha : a ≤ a') (hb : b ≤ b') (ht : 0 ≤ t) :
    response a b t ≤ response a' b' t := by
  exact intervalIntegral.integral_mono_on ht
    ((continuous_kernel a b t).intervalIntegrable 0 t)
    ((continuous_kernel a' b' t).intervalIntegrable 0 t)
    (fun s hs => kernel_mono a b a' b' t s ha hb hs)

theorem response_nonexpansive (a b t : ℝ) (ha : a ≤ 0) (hb : b ≤ 0) (ht : 0 ≤ t) :
    response a b t ≤ t := by
  simpa using response_mono a b 0 0 t ha hb ht

/-- Stable reduced evolution against a nonexpansive true evolution. -/
theorem response_stable_formula (rate t : ℝ) (hrate : 0 < rate) :
    response 0 (-rate) t = (1 - Real.exp (-rate*t))/rate := by
  have h : (0:ℝ) ≠ -rate := by linarith
  simpa using response_of_ne 0 (-rate) t h

theorem response_stable_le (rate t : ℝ) (hrate : 0 < rate) :
    response 0 (-rate) t ≤ 1/rate := by
  rw [response_stable_formula rate t hrate]
  exact div_le_div_of_nonneg_right (by linarith [Real.exp_pos (-rate*t)]) hrate.le

theorem response_uniform (a b rate t : ℝ) (ha : a ≤ 0) (hb : b ≤ -rate)
    (hrate : 0 < rate) (ht : 0 ≤ t) : response a b t ≤ 1/rate := by
  exact (response_mono a b 0 (-rate) t ha hb ht).trans (response_stable_le rate t hrate)

theorem response_common_rate_le (a b c t : ℝ) (ha : a ≤ c) (hb : b ≤ c) (ht : 0 ≤ t) :
    response a b t ≤ t * Real.exp (c*t) := by
  simpa only [response_self] using response_mono a b c c t ha hb ht

end Komorebi.SufficientResolution.ExponentialBudgets
