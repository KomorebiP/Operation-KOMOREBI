import PaperX.RealAxisEndpointIntegral
import Mathlib.Analysis.SpecialFunctions.ImproperIntegrals
import Mathlib.MeasureTheory.Function.SpecialFunctions.Basic

/-! A power-saving bound on an actual measurable summatory function supplies the
logarithmic moment required by the real-axis endpoint theorem. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.RealAxisMellinMoment
open MeasureTheory Filter Set
open scoped Topology

/-- A logarithmic weight costs any fixed positive power. -/
theorem weighted_power_bound {x r ε C : ℝ} {z : ℂ}
    (hx : 1 < x) (hε : 0 < ε) (hz : ‖z‖ ≤ C * x ^ r) :
    (1 + Real.log x) * ‖(x ^ (-2 : ℝ)) • z‖ ≤
      (C * (1 + ε⁻¹)) * x ^ (r + ε - 2) := by
  have hx0 : 0 < x := lt_trans zero_lt_one hx
  have hxε : 1 ≤ x ^ ε := Real.one_le_rpow hx.le hε.le
  have hl : Real.log x ≤ x ^ ε / ε := Real.log_le_rpow_div hx0.le hε
  have hl0 : 0 ≤ Real.log x := Real.log_nonneg hx.le
  have hweight : 1 + Real.log x ≤ (1 + ε⁻¹) * x ^ ε := by
    calc
      1 + Real.log x ≤ x ^ ε + x ^ ε / ε := add_le_add hxε hl
      _ = (1 + ε⁻¹) * x ^ ε := by ring
  rw [norm_smul, Real.norm_eq_abs, abs_of_pos (Real.rpow_pos_of_pos hx0 _)]
  calc
    (1 + Real.log x) * (x ^ (-2 : ℝ) * ‖z‖) ≤
        ((1 + ε⁻¹) * x ^ ε) * (x ^ (-2 : ℝ) * (C * x ^ r)) := by
      apply mul_le_mul hweight
        (mul_le_mul_of_nonneg_left hz (Real.rpow_nonneg hx0.le _))
        (mul_nonneg (Real.rpow_nonneg hx0.le _) (norm_nonneg z))
      positivity
    _ = (C * (1 + ε⁻¹)) * x ^ (r + ε - 2) := by
      rw [show r + ε - 2 = ε + (-2 + r) by ring,
        Real.rpow_add hx0, Real.rpow_add hx0]
      ring

/-- Any exponent strictly below one gives the needed logarithmic first moment. -/
theorem integrable_weighted_moment_of_power_bound {S : ℝ → ℂ} {C r : ℝ}
    (hS : AEStronglyMeasurable S (volume.restrict (Ioi 1)))
    (hr : r < 1)
    (hbound : ∀ x, 1 < x → ‖S x‖ ≤ C * x ^ r) :
    Integrable (fun x : ℝ => (1 + Real.log x) * ‖(x ^ (-2 : ℝ)) • S x‖)
      (volume.restrict (Ioi 1)) := by
  let ε : ℝ := (1 - r) / 2
  have hε : 0 < ε := by dsimp [ε]; linarith
  have hexp : r + ε - 2 < -1 := by dsimp [ε]; linarith
  have hpow := integrableOn_Ioi_rpow_of_lt hexp (show (0 : ℝ) < 1 by norm_num)
  apply (hpow.const_mul (C * (1 + ε⁻¹))).mono'
  · have hm : Measurable (fun x : ℝ => x ^ (-2 : ℝ)) := by fun_prop
    have hl : Measurable (fun x : ℝ => 1 + Real.log x) := by fun_prop
    exact hl.aestronglyMeasurable.mul ((hm.aestronglyMeasurable.smul hS).norm)
  · filter_upwards [ae_restrict_mem measurableSet_Ioi] with x hx
    have hx1 : 1 < x := hx
    have hl0 : 0 ≤ Real.log x := Real.log_nonneg hx1.le
    rw [Real.norm_eq_abs, abs_of_nonneg (by positivity)]
    exact weighted_power_bound hx1 hε (hbound x hx1)

/-- The Mellin integral in the real parameter h=s-1. -/
def mellinIntegral (S : ℝ → ℂ) (h : ℝ) : ℂ :=
  (1 + h) • ∫ x in Ioi (1 : ℝ), (x ^ (-2 - h)) • S x

/-- The Mellin kernel is exactly the exponential damping kernel. -/
theorem mellinIntegral_eq_endpointIntegral (S : ℝ → ℂ) (h : ℝ) :
    mellinIntegral S h = PaperX.RealAxisEndpointIntegral.endpointIntegral
      (volume.restrict (Ioi 1)) (fun x : ℝ => (x ^ (-2 : ℝ)) • S x) Real.log h := by
  unfold mellinIntegral PaperX.RealAxisEndpointIntegral.endpointIntegral
  rw [← integral_smul]
  apply integral_congr_ae
  filter_upwards [ae_restrict_mem measurableSet_Ioi] with x hx
  have hx0 : 0 < x := lt_trans zero_lt_one hx
  rw [smul_smul, smul_smul]
  congr 1
  rw [Real.rpow_def_of_pos hx0, Real.rpow_def_of_pos hx0, mul_assoc, ← Real.exp_add]
  congr 2
  ring

/-- A power-saving summatory bound gives a first-order right endpoint error
for its actual Mellin integral. -/
theorem mellinIntegral_sub_isBigO_of_power_bound {S : ℝ → ℂ} {C r : ℝ}
    (hS : AEStronglyMeasurable S (volume.restrict (Ioi 1)))
    (hr : r < 1)
    (hbound : ∀ x, 1 < x → ‖S x‖ ≤ C * x ^ r) :
    (fun h => mellinIntegral S h - mellinIntegral S 0)
      =O[𝓝[>] (0 : ℝ)] (fun h : ℝ => h) := by
  have hA : AEStronglyMeasurable (fun x : ℝ => (x ^ (-2 : ℝ)) • S x)
      (volume.restrict (Ioi 1)) := by
    have hm : Measurable (fun x : ℝ => x ^ (-2 : ℝ)) := by fun_prop
    exact hm.aestronglyMeasurable.smul hS
  have hu : ∀ᵐ x ∂volume.restrict (Ioi (1 : ℝ)), 0 ≤ Real.log x := by
    filter_upwards [ae_restrict_mem measurableSet_Ioi] with x hx
    exact Real.log_nonneg (le_of_lt hx)
  have hW := integrable_weighted_moment_of_power_bound hS hr hbound
  simpa only [mellinIntegral_eq_endpointIntegral] using
    PaperX.RealAxisEndpointIntegral.endpointIntegral_sub_isBigO
      (volume.restrict (Ioi 1)) hA Real.measurable_log hu hW

end PaperX.RealAxisMellinMoment
