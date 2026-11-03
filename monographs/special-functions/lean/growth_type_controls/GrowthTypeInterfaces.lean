import CoupledGrowthTypes
open Filter Komorebi.SpecialFunctions.Coupled
open Scales
open scoped Topology Matrix
noncomputable section

example : 2 ≤ Filter.liminf (fun _ : ℝ => (2 : ℝ)) atTop ∧
    Filter.liminf (fun _ : ℝ => (2 : ℝ)) atTop ≤ Filter.limsup (fun _ : ℝ => (2 : ℝ)) atTop ∧
    Filter.limsup (fun _ : ℝ => (2 : ℝ)) atTop ≤ 2 :=
  real_type_sandwich (Eventually.of_forall (fun _ => ⟨le_rfl, le_rfl⟩))

-- The radial exponent is one while the normalized growth ratio is two.
example : Tendsto (fun R : ℝ => Real.log (Real.log (Real.exp (2 * R))) / Real.log R)
    atTop (𝓝 1) := by
  apply tendsto_loglog_of_ratio_bounds (lo := 2) (hi := 2) (by norm_num) (by norm_num)
  filter_upwards [eventually_ge_atTop (1 : ℝ)] with R hR
  have he : 2 * R / R = 2 := mul_div_cancel_right₀ 2 (by linarith)
  simpa only [Real.log_exp, Real.rpow_one, he] using And.intro (le_rfl : (2 : ℝ) ≤ 2) le_rfl

example : Tendsto (fun R : ℝ => Real.log (Real.log (Real.exp (R ^ (1 / 2 : ℝ)))) / Real.log R)
    atTop (𝓝 (1 / 2 : ℝ)) := by
  apply tendsto_loglog_of_ratio_bounds (lo := 1) (hi := 1) (by norm_num) (by norm_num)
  filter_upwards [eventually_ge_atTop (1 : ℝ)] with R hR
  have hp := Real.rpow_pos_of_pos (by linarith : 0 < R) (1 / 2 : ℝ)
  simpa only [Real.log_exp, div_self (ne_of_gt hp)] using And.intro (le_rfl : (1 : ℝ) ≤ 1) le_rfl

example (i : Fin 2) :
    workedScales.canonicalLowerCoefficient workedScales_positive (by norm_num [workedScales]) i ≤
      workedScales.lowerType workedScales_positive (by norm_num [workedScales]) i ∧
    workedScales.lowerType workedScales_positive (by norm_num [workedScales]) i ≤
      workedScales.upperType workedScales_positive (by norm_num [workedScales]) i ∧
    workedScales.upperType workedScales_positive (by norm_num [workedScales]) i ≤
      workedScales.canonicalUpperCoefficient workedScales_positive (by norm_num [workedScales]) i :=
  workedScales.canonical_type_bounds workedScales_positive (by norm_num [workedScales]) i

example : workedScales.maximumModulus 0 0 = 0 := by
  rw [workedScales.maximumModulus_eq workedScales_positive (by norm_num [workedScales]) 0 le_rfl]
  exact workedScales.real_axis_zero.1

example (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    0 < s.lowerType hs hstrict i ∧
    Tendsto (fun R : ℝ => Real.log (Real.log (s.maximumModulus i R)) / Real.log R)
      atTop (𝓝 (s.characteristicExponent hs hstrict)) :=
  ⟨(s.canonical_types_positive hs hstrict i).1, s.canonical_maximum_radial_limit hs hstrict i⟩
