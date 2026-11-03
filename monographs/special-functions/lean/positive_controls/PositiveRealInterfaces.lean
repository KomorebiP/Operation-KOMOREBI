import CoupledPositiveReal
open Komorebi.SpecialFunctions.Coupled
open Scales

example (x : ℝ) : workedScales.U (x : ℂ) = (workedScales.UReal x : ℂ) :=
  (workedScales.real_axis_identification workedScales_positive (by norm_num [workedScales]) x).1

example : 2 ≤ workedScales.UReal 2 ∧ 2 ≤ workedScales.VReal 2 :=
  workedScales.real_axis_lower_linear workedScales_positive (by norm_num [workedScales]) (by norm_num)

example {z : ℂ} (hz : ‖z‖ ≤ 2) : ‖workedScales.U z‖ ≤ workedScales.UReal 2 :=
  (workedScales.complex_norm_le_real_axis workedScales_positive (by norm_num [workedScales]) hz).1

example : IsGreatest ((fun z => ‖workedScales.U z‖) '' Metric.sphere (0 : ℂ) 0) 0 := by
  simpa only [workedScales.real_axis_zero.1] using
    (workedScales.maximum_modulus_real_axis workedScales_positive
      (by norm_num [workedScales]) (R := 0) (by norm_num)).1

example : workedScales.UReal (workedScales.q * (1 - 1)) *
    workedScales.VReal (workedScales.r * (1 - 1)) ≤ workedScales.UReal 1 :=
  (workedScales.real_axis_unit_lower workedScales_positive (by norm_num [workedScales])
    (R := 1) (by norm_num)).1

example : Real.log (workedScales.UReal (workedScales.q * (12 - 1))) +
    Real.log (workedScales.VReal (workedScales.r * (12 - 1))) ≤
    Real.log (workedScales.UReal 12) :=
  (workedScales.real_axis_log_unit_lower workedScales_positive (by norm_num [workedScales])
    (R := 12) (by norm_num)).1

example : workedScales.minScale = 1 / 5 ∧ workedScales.lowerThreshold = 11 := by
  norm_num [minScale, lowerThreshold, workedScales]

example : 2 ≤ workedScales.q * (11 - 1) ∧ 2 ≤ workedScales.r * (11 - 1) ∧
    2 ≤ workedScales.a * (11 - 1) ∧ 2 ≤ workedScales.b * (11 - 1) :=
  workedScales.lower_child_radii workedScales_positive (R := 11)
    (by norm_num [minScale, lowerThreshold, workedScales])
