import Komorebi.SufficientResolution.ContinuousStability
import Komorebi.SufficientResolution.ApproximateExamples

/-!
# Exact sharpness and failure without growth control

Real scalar examples use the actual Banach-algebra flow, derived from the ODE.
These are universal theorems in real parameters, not sampled numerical tests.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousApproxExamples

open ContinuousFlow ContinuousDefect ExponentialBudgets
open ApproximateExamples (scalar scalar_apply norm_scalar scalar_one)

/-- Identify the actual flow by its differential equation and initial value. -/
theorem scalar_flow_apply (a t x : ℝ) : flow (scalar a) t x = Real.exp (a*t)*x := by
  have hd : ∀ s, HasDerivAt (fun u => Real.exp (a*u)*x)
      (scalar a (Real.exp (a*s)*x)) s := by
    intro s
    have h := (((hasDerivAt_id s).const_mul a).exp).mul_const x
    convert h using 1
    all_goals first | rfl | (dsimp [scalar]; ring)
  have h := homogeneous_solution (scalar a) (fun s => Real.exp (a*s)*x) hd t
  simpa using h.symm

theorem scalar_flow (a t : ℝ) : flow (scalar a) t = scalar (Real.exp (a*t)) := by
  apply ContinuousLinearMap.ext
  intro x
  exact scalar_flow_apply a t x

theorem norm_scalar_flow (a t : ℝ) : ‖flow (scalar a) t‖ = Real.exp (a*t) := by
  rw [scalar_flow, norm_scalar, abs_of_pos (Real.exp_pos _)]

theorem scalar_generatorDefect (a b : ℝ) :
    generatorDefect (scalar 1) (scalar a) (scalar b) = scalar (a-b) := by
  apply ContinuousLinearMap.ext
  intro x
  simp [generatorDefect, sub_mul]

theorem scalar_evolutionDefect (a b t : ℝ) :
    evolutionDefect (scalar 1) (scalar a) (scalar b) t =
      scalar (Real.exp (a*t) - Real.exp (b*t)) := by
  apply ContinuousLinearMap.ext
  intro x
  simp [evolutionDefect, scalar_flow, sub_mul]

/-- The two-rate envelope is exactly attained, including negative growth rates. -/
theorem scalar_response_sharp (a b t : ℝ) (hba : b ≤ a) (ht : 0 ≤ t) :
    ‖evolutionDefect (scalar 1) (scalar a) (scalar b) t‖ = (a-b)*response a b t := by
  rw [scalar_evolutionDefect, norm_scalar]
  rw [abs_of_nonneg (sub_nonneg.mpr (Real.exp_le_exp.mpr
    (mul_le_mul_of_nonneg_right hba ht)))]
  by_cases h : a = b
  · subst b
    simp
  · rw [response_of_ne a b t h]
    have hab : a-b ≠ 0 := sub_ne_zero.mpr h
    field_simp

/-- Small generator mismatch alone does not imply uniformly small future error. -/
theorem unstable_generator_exact (ε : ℝ) (he : 0 ≤ ε) :
    ‖generatorDefect (scalar 1) (scalar ε) (scalar 0)‖ = ε := by
  rw [scalar_generatorDefect, norm_scalar, sub_zero, abs_of_nonneg he]

theorem unstable_error_exact (ε t : ℝ) (he : 0 ≤ ε) (ht : 0 ≤ t) :
    ‖evolutionDefect (scalar 1) (scalar ε) (scalar 0) t‖ = Real.exp (ε*t)-1 := by
  rw [scalar_evolutionDefect, norm_scalar]
  simp only [zero_mul, Real.exp_zero]
  exact abs_of_nonneg (sub_nonneg.mpr (Real.one_le_exp (mul_nonneg he ht)))

theorem unstable_error_lower (ε t : ℝ) (he : 0 ≤ ε) (ht : 0 ≤ t) :
    ε*t ≤ ‖evolutionDefect (scalar 1) (scalar ε) (scalar 0) t‖ := by
  rw [unstable_error_exact ε t he ht]
  linarith [Real.add_one_le_exp (ε*t)]

/-- For every positive defect allowance and every bound, some future time exceeds it. -/
theorem unstable_error_unbounded (ε : ℝ) (he : 0 < ε) (B : ℝ) :
    ∃ t : ℝ, 0 ≤ t ∧ B < ‖evolutionDefect (scalar 1) (scalar ε) (scalar 0) t‖ := by
  obtain ⟨n, hn⟩ := exists_nat_gt (B/ε)
  refine ⟨(n:ℝ), Nat.cast_nonneg n, ?_⟩
  have hm : B < ε*(n:ℝ) := by
    have h := (div_lt_iff₀ he).mp hn
    simpa only [mul_comm] using h
  exact hm.trans_le (unstable_error_lower ε n he.le (Nat.cast_nonneg n))

/-- Stable scalar realization has exactly the saturation factor in the theorem. -/
theorem stable_error_exact (rate t : ℝ) (hr : 0 ≤ rate) (ht : 0 ≤ t) :
    ‖evolutionDefect (scalar 1) (scalar 0) (scalar (-rate)) t‖ =
      1-Real.exp (-rate*t) := by
  rw [scalar_evolutionDefect, norm_scalar]
  simp only [zero_mul, Real.exp_zero]
  apply abs_of_nonneg
  have h : -rate*t ≤ 0 := by nlinarith
  exact sub_nonneg.mpr (Real.exp_le_one_iff.mpr h)

end Komorebi.SufficientResolution.ContinuousApproxExamples
