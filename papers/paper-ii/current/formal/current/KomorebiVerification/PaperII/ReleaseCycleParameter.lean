import KomorebiVerification.PaperII.ReleaseAnalyticContour
import Mathlib.Analysis.Calculus.ParametricIntervalIntegral
import Mathlib.Analysis.Calculus.MeanValue

set_option autoImplicit false
noncomputable section

namespace Komorebi.PaperII.ReleaseCycleParameter
open MeasureTheory Set Filter
open scoped Topology BigOperators
open Komorebi.PaperII.ReleaseAnalyticContour

theorem isCompact_trace (Γ : IntegralCycle) : IsCompact Γ.trace := by
  have heq : Γ.trace = ⋃ i : Fin Γ.count, Γ.curve i '' uIcc (0 : ℝ) 1 := by
    ext z
    simp only [IntegralCycle.trace, mem_ofPred_eq, mem_iUnion, mem_image]
  rw [heq]
  exact isCompact_iUnion fun i => isCompact_uIcc.image_of_continuousOn (Γ.continuousOn_curve i)

theorem exists_ball_away_trace (Γ : IntegralCycle) {w : ℂ} (hw : w ∉ Γ.trace) :
    ∃ ε > 0, ∀ z ∈ Γ.trace, ∀ w' ∈ Metric.ball w ε,
      ε ≤ ‖z - w'‖ := by
  obtain ⟨r, hr, hball⟩ := Metric.isOpen_iff.mp (isCompact_trace Γ).isClosed.isOpen_compl w hw
  refine ⟨r / 2, half_pos hr, ?_⟩
  intro z hz w' hw'
  have hzout : r ≤ ‖z - w‖ := by
    by_contra! hlt
    exact hball (by simpa only [Metric.mem_ball, dist_eq_norm] using hlt) hz
  have hw'lt : ‖w' - w‖ < r / 2 := by simpa only [Metric.mem_ball, dist_eq_norm] using hw'
  have htri : ‖z - w‖ ≤ ‖z - w'‖ + ‖w' - w‖ := by
    convert norm_add_le (z - w') (w' - w) using 1; ring_nf
  linarith

section Parameter
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
variable [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]

omit [IsScalarTower ℝ ℂ E] [CompleteSpace E] in
/-- Differentiation of the actual finite Banach-valued cycle integral.
The domination is a constant times the integrable velocity, so no pointwise
bound on the velocity or piecewise smoothness is required. -/
theorem hasDerivAt_lineIntegral (Γ : IntegralCycle) {f f' : ℂ → ℂ → E}
    {w : ℂ} {s : Set ℂ} (hs : s ∈ 𝓝 w)
    (hf : ∀ w' ∈ s, ContinuousOn (f w') Γ.trace)
    (hf' : ContinuousOn (f' w) Γ.trace)
    (hderiv : ∀ w' ∈ s, ∀ z ∈ Γ.trace,
      HasDerivAt (fun a => f a z) (f' w' z) w')
    (M : ℝ) (hbound : ∀ w' ∈ s, ∀ z ∈ Γ.trace, ‖f' w' z‖ ≤ M) :
    HasDerivAt (fun a => Γ.lineIntegral (f a)) (Γ.lineIntegral (f' w)) w := by
  unfold IntegralCycle.lineIntegral
  apply HasDerivAt.fun_sum
  intro i hi
  apply (intervalIntegral.hasDerivAt_integral_of_dominated_loc_of_deriv_le
    (bound := fun t => ‖Γ.velocity i t‖ * M) hs ?_ ?_ ?_ ?_ ?_ ?_).2
  · filter_upwards [hs] with a ha
    simpa only [uIoc_of_le (by norm_num : (0 : ℝ) ≤ 1)] using
      (Γ.integrable_lineIntegrand (hf a ha) i).1.aestronglyMeasurable
  · exact Γ.integrable_lineIntegrand (hf w (mem_of_mem_nhds hs)) i
  · simpa only [uIoc_of_le (by norm_num : (0 : ℝ) ≤ 1)] using
      (Γ.integrable_lineIntegrand hf' i).1.aestronglyMeasurable
  · filter_upwards with t ht a ha
    have htrace : Γ.curve i t ∈ Γ.trace :=
      ⟨i, t, by simpa using Ioc_subset_Icc_self ht, rfl⟩
    rw [norm_smul]
    exact mul_le_mul_of_nonneg_left (hbound a ha _ htrace) (norm_nonneg _)
  · exact (Γ.velocity_integrable i).norm.mul_const M
  · filter_upwards with t ht a ha
    exact (hderiv a ha (Γ.curve i t)
      ⟨i, t, by simpa using Ioc_subset_Icc_self ht, rfl⟩).const_smul (Γ.velocity i t)

end Parameter

end Komorebi.PaperII.ReleaseCycleParameter
