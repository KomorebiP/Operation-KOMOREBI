import Mathlib.MeasureTheory.Integral.Bochner.Basic
import Mathlib.Analysis.SpecialFunctions.Exp
import Mathlib.Analysis.Asymptotics.Defs
import Mathlib.Tactic

/-! A logarithmic first moment gives a quantitative right endpoint bound for
an actual exponentially damped integral. Arithmetic character sums are not supplied
by this theorem. -/

set_option autoImplicit false
noncomputable section
namespace PaperX.RealAxisEndpointIntegral
open MeasureTheory Filter
open scoped Topology

/-- The elementary damping error, including the prefactor from partial summation. -/
theorem kernel_sub_one_le {h u : ℝ} (hh : 0 ≤ h) (hu : 0 ≤ u) :
    |(1 + h) * Real.exp (-h * u) - 1| ≤ h * (1 + u) := by
  have he0 : 0 ≤ Real.exp (-h * u) := (Real.exp_pos _).le
  have he1 : Real.exp (-h * u) ≤ 1 := Real.exp_le_one_iff.mpr (by nlinarith)
  have he2 := Real.add_one_le_exp (-h * u)
  apply abs_le.mpr
  constructor <;> nlinarith

variable {α : Type*} [MeasurableSpace α] (μ : Measure α)

/-- The actual integral that appears after writing x^(-h) as exp(-h log x). -/
def endpointIntegral (A : α → ℂ) (u : α → ℝ) (h : ℝ) : ℂ :=
  ∫ x, ((1 + h) * Real.exp (-h * u x)) • A x ∂μ

/-- At the endpoint the damping factor is exactly one. -/
theorem endpointIntegral_zero (A : α → ℂ) (u : α → ℝ) :
    endpointIntegral μ A u 0 = ∫ x, A x ∂μ := by
  simp [endpointIntegral]

/-- The weighted first moment already implies integrability of the base function. -/
theorem integrable_of_weighted_moment {A : α → ℂ} {u : α → ℝ}
    (hA : AEStronglyMeasurable A μ) (hu : ∀ᵐ x ∂μ, 0 ≤ u x)
    (hW : Integrable (fun x => (1 + u x) * ‖A x‖) μ) : Integrable A μ := by
  apply hW.mono' hA
  filter_upwards [hu] with x hx
  nlinarith [norm_nonneg (A x)]

/-- Every nonnegative damping parameter gives an integrable kernel. -/
theorem integrable_kernel {A : α → ℂ} {u : α → ℝ}
    (hA : AEStronglyMeasurable A μ) (humeas : Measurable u)
    (hu : ∀ᵐ x ∂μ, 0 ≤ u x)
    (hW : Integrable (fun x => (1 + u x) * ‖A x‖) μ)
    {h : ℝ} (hh : 0 ≤ h) :
    Integrable (fun x => ((1 + h) * Real.exp (-h * u x)) • A x) μ := by
  have hAi := integrable_of_weighted_moment μ hA hu hW
  apply (hAi.norm.const_mul (1 + h)).mono'
  · exact ((measurable_const.mul ((measurable_const.mul humeas).exp)).aestronglyMeasurable).smul hA
  · filter_upwards [hu] with x hx
    rw [norm_smul, Real.norm_eq_abs, abs_of_nonneg (by positivity)]
    have he : Real.exp (-h * u x) ≤ 1 := Real.exp_le_one_iff.mpr (by nlinarith)
    simpa only [mul_one] using mul_le_mul_of_nonneg_right
      (mul_le_mul_of_nonneg_left he (by linarith : 0 ≤ 1 + h)) (norm_nonneg (A x))

/-- A single finite weighted integral controls the right endpoint error linearly. -/
theorem endpointIntegral_sub_norm_le {A : α → ℂ} {u : α → ℝ}
    (hA : AEStronglyMeasurable A μ) (humeas : Measurable u)
    (hu : ∀ᵐ x ∂μ, 0 ≤ u x)
    (hW : Integrable (fun x => (1 + u x) * ‖A x‖) μ)
    {h : ℝ} (hh : 0 ≤ h) :
    ‖endpointIntegral μ A u h - endpointIntegral μ A u 0‖ ≤
      h * ∫ x, (1 + u x) * ‖A x‖ ∂μ := by
  have hAi := integrable_of_weighted_moment μ hA hu hW
  have hKi := integrable_kernel μ hA humeas hu hW hh
  rw [endpointIntegral_zero, endpointIntegral, ← integral_sub hKi hAi]
  calc
    ‖∫ x, ((1 + h) * Real.exp (-h * u x)) • A x - A x ∂μ‖ ≤
        ∫ x, ‖((1 + h) * Real.exp (-h * u x)) • A x - A x‖ ∂μ :=
      norm_integral_le_integral_norm _
    _ ≤ ∫ x, h * ((1 + u x) * ‖A x‖) ∂μ := by
      apply integral_mono_ae (hKi.sub hAi).norm (hW.const_mul h)
      filter_upwards [hu] with x hx
      have he := kernel_sub_one_le hh hx
      change ‖((1 + h) * Real.exp (-h * u x)) • A x - A x‖ ≤ _
      have hid : ((1 + h) * Real.exp (-h * u x)) • A x - A x =
          ((1 + h) * Real.exp (-h * u x) - 1) • A x := by rw [sub_smul, one_smul]
      rw [hid, norm_smul, Real.norm_eq_abs]
      exact (mul_le_mul_of_nonneg_right he (norm_nonneg (A x))).trans_eq (by ring)
    _ = h * ∫ x, (1 + u x) * ‖A x‖ ∂μ := integral_const_mul _ _

/-- The endpoint difference is O(h) along positive h tending to zero. -/
theorem endpointIntegral_sub_isBigO {A : α → ℂ} {u : α → ℝ}
    (hA : AEStronglyMeasurable A μ) (humeas : Measurable u)
    (hu : ∀ᵐ x ∂μ, 0 ≤ u x)
    (hW : Integrable (fun x => (1 + u x) * ‖A x‖) μ) :
    (fun h => endpointIntegral μ A u h - endpointIntegral μ A u 0)
      =O[𝓝[>] (0 : ℝ)] (fun h : ℝ => h) := by
  refine Asymptotics.isBigO_iff.mpr ⟨∫ x, (1 + u x) * ‖A x‖ ∂μ, ?_⟩
  filter_upwards [self_mem_nhdsWithin] with h hh
  have hh0 : 0 ≤ h := le_of_lt hh
  simpa only [Real.norm_eq_abs, abs_of_nonneg hh0, mul_comm] using
    endpointIntegral_sub_norm_le μ hA humeas hu hW hh0

end PaperX.RealAxisEndpointIntegral
