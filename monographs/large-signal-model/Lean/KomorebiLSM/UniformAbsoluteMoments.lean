import KomorebiLSM.UniformIntervalMoments

set_option autoImplicit false
namespace Komorebi.LSM.UniformAbsoluteMoments
open MeasureTheory
open UniformIntervalMoments

/-- The actual normalized integral of the absolute observation coordinate. -/
theorem integral_abs : (∫ u,|u|∂measure)=(1/2 : ℝ) := by
  rw [UniformIntervalMoments.integral_eq]
  have hi (a b : ℝ) : IntervalIntegrable (fun u : ℝ => |u|) volume a b :=
    continuous_abs.intervalIntegrable a b
  have hneg : (∫ u in (-1 : ℝ)..0,|u|)=∫ u in (-1 : ℝ)..0,-u := by
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le (by norm_num : (-1 : ℝ)≤0)] at hu
    exact abs_of_nonpos hu.2
  have hpos : (∫ u in (0 : ℝ)..1,|u|)=∫ u in (0 : ℝ)..1,u := by
    apply intervalIntegral.integral_congr
    intro u hu
    rw [Set.uIcc_of_le (by norm_num : (0 : ℝ)≤1)] at hu
    exact abs_of_nonneg hu.1
  rw [← intervalIntegral.integral_add_adjacent_intervals (hi (-1) 0) (hi 0 1),hneg,hpos]
  rw [intervalIntegral.integral_neg]
  norm_num [integral_id]

theorem abs_power_integrable (k : ℕ) : Integrable (fun u : ℝ => |u|^k) measure :=
  continuous_integrable (continuous_abs.pow k)

/-- Exact moments used by the literal degree-two fixture, without signed cancellation. -/
theorem integral_abs_power (k : Fin 3) : (∫ u,|u|^(k : ℕ)∂measure)=1/((k : ℕ)+1 : ℝ) := by
  fin_cases k
  · norm_num
  · convert integral_abs using 1 <;> norm_num
  · have h : (∫ u,u^2∂measure)=(1/3 : ℝ) := by
      change moment 2=1/3
      norm_num [moment_formula]
    simpa only [sq_abs] using h.trans (by norm_num : (1/3 : ℝ)=1/((2 : ℕ)+1 : ℝ))

end Komorebi.LSM.UniformAbsoluteMoments
