import PaperX.IdealCharacterMellinMeasurable
import PaperX.IdealClassCharacterBound
import PaperX.RealAxisMellinMoment

/-! Logarithmic first moments and first-order Mellin endpoint control for sums
over actual integral ideals weighted by ordinary class characters. The power
saving and measurability are proved from the number field, not supplied as
analytic hypotheses. -/

set_option autoImplicit false
noncomputable section

open Ideal NumberField MeasureTheory Filter Set Asymptotics
open scoped nonZeroDivisors Classical BigOperators Topology

namespace PaperX.IdealClassCharacter

open PaperX.IdealClassQuantitative PaperX.RealAxisMellinMoment

variable (K : Type*) [Field K] [NumberField K]

/-- Any ordinary-class weighted sum over actual bounded ideals is measurable. -/
theorem measurable_weightedSum (w : ClassGroup (𝓞 K) → ℂ) :
    Measurable (weightedSum K w) := by
  change Measurable (fun x => weightedSum K w x)
  simp_rw [weightedSum_eq_sum_classCount]
  exact Finset.measurable_sum _ fun C _ =>
    measurable_const.mul
      ((measurable_of_countable (fun n : ℕ => (n : ℂ))).comp (measurable_classCount K C))

/-- The actual real-parameter Mellin integral, with parameter h=s-1. -/
def classMellin (w : ClassGroup (𝓞 K) → ℂ) (h : ℝ) : ℂ :=
  mellinIntegral (weightedSum K w) h

/-- Cancellation of the common main term yields the logarithmic first moment. -/
theorem integrable_weightedSum_logMoment (w : ClassGroup (𝓞 K) → ℂ)
    (hw : ∑ C, w C = 0) :
    Integrable (fun x : ℝ =>
      (1 + Real.log x) * ‖(x ^ (-2 : ℝ)) • weightedSum K w x‖)
      (volume.restrict (Ioi 1)) := by
  obtain ⟨M, _, hM⟩ := exists_weightedSum_bound K w hw
  exact integrable_weighted_moment_of_power_bound
    (measurable_weightedSum K w).aestronglyMeasurable (countExponent_lt_one K)
    (fun x hx => hM x hx.le)

/-- The Mellin endpoint error is O(h) for actual zero-mean class weights. -/
theorem classMellin_sub_isBigO (w : ClassGroup (𝓞 K) → ℂ)
    (hw : ∑ C, w C = 0) :
    (fun h => classMellin K w h - classMellin K w 0)
      =O[𝓝[>] (0 : ℝ)] (fun h : ℝ => h) := by
  obtain ⟨M, _, hM⟩ := exists_weightedSum_bound K w hw
  exact mellinIntegral_sub_isBigO_of_power_bound
    (measurable_weightedSum K w).aestronglyMeasurable (countExponent_lt_one K)
    (fun x hx => hM x hx.le)

/-- The finite logarithmic moment is an explicit error constant, valid for
every nonnegative real parameter. -/
theorem classMellin_sub_norm_le (w : ClassGroup (𝓞 K) → ℂ)
    (hw : ∑ C, w C = 0) {h : ℝ} (hh : 0 ≤ h) :
    ‖classMellin K w h - classMellin K w 0‖ ≤
      h * ∫ x in Ioi (1 : ℝ),
        (1 + Real.log x) * ‖(x ^ (-2 : ℝ)) • weightedSum K w x‖ := by
  have hA : AEStronglyMeasurable
      (fun x : ℝ => (x ^ (-2 : ℝ)) • weightedSum K w x)
      (volume.restrict (Ioi 1)) := by
    have hm : Measurable (fun x : ℝ => x ^ (-2 : ℝ)) := by fun_prop
    exact hm.aestronglyMeasurable.smul (measurable_weightedSum K w).aestronglyMeasurable
  have hu : ∀ᵐ x ∂volume.restrict (Ioi (1 : ℝ)), 0 ≤ Real.log x := by
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with x hx
    exact Real.log_nonneg (le_of_lt hx)
  simpa only [classMellin, mellinIntegral_eq_endpointIntegral] using
    PaperX.RealAxisEndpointIntegral.endpointIntegral_sub_norm_le
      (volume.restrict (Ioi 1)) hA Real.measurable_log hu
      (integrable_weightedSum_logMoment K w hw) hh

/-- In particular, every nontrivial ordinary class character has a finite
logarithmic first moment. -/
theorem integrable_character_logMoment (χ : ClassGroup (𝓞 K) →* ℂ)
    (hχ : χ ≠ 1) :
    Integrable (fun x : ℝ =>
      (1 + Real.log x) * ‖(x ^ (-2 : ℝ)) • weightedSum K χ x‖)
      (volume.restrict (Ioi 1)) :=
  integrable_weightedSum_logMoment K χ (sum_character_eq_zero χ hχ)

/-- The endpoint bound applies to the actual ideal sum of each nontrivial
ordinary class character. This does not assert that its endpoint value is nonzero. -/
theorem characterMellin_sub_isBigO (χ : ClassGroup (𝓞 K) →* ℂ)
    (hχ : χ ≠ 1) :
    (fun h => classMellin K χ h - classMellin K χ 0)
      =O[𝓝[>] (0 : ℝ)] (fun h : ℝ => h) :=
  classMellin_sub_isBigO K χ (sum_character_eq_zero χ hχ)

end PaperX.IdealClassCharacter
