import CoupledUpperGrowth
import Mathlib.Topology.Order.LiminfLimsup

/-! # Real types and the radial exponent for the canonical coupled pair -/

set_option autoImplicit false
set_option maxHeartbeats 2000000

noncomputable section
open Filter Set
open scoped Topology Matrix

namespace Komorebi.SpecialFunctions.Coupled.Scales

def realComponent (s : Scales) (i : Fin 2) (R : ℝ) : ℝ := ![s.UReal R, s.VReal R] i
def growthRatio (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) (R : ℝ) : ℝ :=
  Real.log (s.realComponent i R) / R ^ (s.characteristicExponent hs hstrict)
def lowerType (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) : ℝ :=
  Filter.liminf (s.growthRatio hs hstrict i) atTop
def upperType (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) : ℝ :=
  Filter.limsup (s.growthRatio hs hstrict i) atTop
def radialExponent (s : Scales) (i : Fin 2) (R : ℝ) : ℝ :=
  Real.log (Real.log (s.realComponent i R)) / Real.log R
def radialOrder (s : Scales) (i : Fin 2) : ℝ := Filter.limsup (s.radialExponent i) atTop

theorem realComponent_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R : ℝ} (hR : 0 < R) : 0 < s.realComponent i R := by
  have hh := s.real_axis_lower_linear hs hstrict hR.le
  fin_cases i
  · exact hR.trans_le hh.1
  · exact hR.trans_le hh.2

theorem canonical_growth_ratio_bounds (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R : ℝ} (hR : Real.exp 1 ≤ R) :
    s.canonicalLowerCoefficient hs hstrict i ≤ s.growthRatio hs hstrict i R ∧
    s.growthRatio hs hstrict i R ≤ s.canonicalUpperCoefficient hs hstrict i := by
  have hh := s.canonical_two_sided_growth_ratio hs hstrict hR
  fin_cases i
  · exact hh.1
  · exact hh.2

theorem canonical_growth_ratio_eventually (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    ∀ᶠ R in atTop, s.canonicalLowerCoefficient hs hstrict i ≤ s.growthRatio hs hstrict i R ∧
      s.growthRatio hs hstrict i R ≤ s.canonicalUpperCoefficient hs hstrict i := by
  filter_upwards [eventually_ge_atTop (Real.exp 1)] with R hR
  exact s.canonical_growth_ratio_bounds hs hstrict i hR

theorem canonical_growth_ratio_bounded (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    atTop.IsBoundedUnder (· ≤ ·) (s.growthRatio hs hstrict i) ∧
    atTop.IsBoundedUnder (· ≥ ·) (s.growthRatio hs hstrict i) := by
  have hh := s.canonical_growth_ratio_eventually hs hstrict i
  exact ⟨⟨s.canonicalUpperCoefficient hs hstrict i, hh.mono (fun _ h => h.2)⟩,
    ⟨s.canonicalLowerCoefficient hs hstrict i, hh.mono (fun _ h => h.1)⟩⟩

theorem real_type_sandwich {f : ℝ → ℝ} {lo hi : ℝ}
    (hh : ∀ᶠ R in atTop, lo ≤ f R ∧ f R ≤ hi) :
    lo ≤ Filter.liminf f atTop ∧ Filter.liminf f atTop ≤ Filter.limsup f atTop ∧
      Filter.limsup f atTop ≤ hi := by
  have hlo := hh.mono (fun _ h => h.1)
  have hhi := hh.mono (fun _ h => h.2)
  have hbA : atTop.IsBoundedUnder (· ≤ ·) f := ⟨hi, hhi⟩
  have hbB : atTop.IsBoundedUnder (· ≥ ·) f := ⟨lo, hlo⟩
  exact ⟨le_liminf_of_le hbA.isCoboundedUnder_ge hlo,
    liminf_le_limsup hbA hbB, limsup_le_of_le hbB.isCoboundedUnder_le hhi⟩

theorem canonical_type_bounds (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    s.canonicalLowerCoefficient hs hstrict i ≤ s.lowerType hs hstrict i ∧
    s.lowerType hs hstrict i ≤ s.upperType hs hstrict i ∧
    s.upperType hs hstrict i ≤ s.canonicalUpperCoefficient hs hstrict i :=
  real_type_sandwich (s.canonical_growth_ratio_eventually hs hstrict i)

theorem canonical_types_positive (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    0 < s.lowerType hs hstrict i ∧ 0 < s.upperType hs hstrict i := by
  have hh := s.canonical_type_bounds hs hstrict i
  have hl := (s.canonicalLowerCoefficient_positive hs hstrict i).trans_le hh.1
  exact ⟨hl, hl.trans_le hh.2.1⟩

theorem loglog_ratio_sandwich {f : ℝ → ℝ} {ρ lo hi R : ℝ}
    (hlo : 0 < lo) (hhi : 0 < hi) (hR : 1 < R)
    (hh : lo ≤ Real.log (f R) / R ^ ρ ∧ Real.log (f R) / R ^ ρ ≤ hi) :
    ρ + Real.log lo / Real.log R ≤ Real.log (Real.log (f R)) / Real.log R ∧
      Real.log (Real.log (f R)) / Real.log R ≤ ρ + Real.log hi / Real.log R := by
  have hR0 : 0 < R := by linarith only [hR]
  have hp := Real.rpow_pos_of_pos hR0 ρ
  have hlogR := Real.log_pos hR
  have hL := (le_div_iff₀ hp).mp hh.1
  have hU := (div_le_iff₀ hp).mp hh.2
  have hlogF := (mul_pos hlo hp).trans_le hL
  have hLL := Real.log_le_log (mul_pos hlo hp) hL
  have hUU := Real.log_le_log hlogF hU
  rw [Real.log_mul (ne_of_gt hlo) (ne_of_gt hp), Real.log_rpow hR0] at hLL
  rw [Real.log_mul (ne_of_gt hhi) (ne_of_gt hp), Real.log_rpow hR0] at hUU
  constructor
  · simpa only [add_div, mul_div_cancel_right₀ _ (ne_of_gt hlogR), add_comm] using
      div_le_div_of_nonneg_right hLL hlogR.le
  · simpa only [add_div, mul_div_cancel_right₀ _ (ne_of_gt hlogR), add_comm] using
      div_le_div_of_nonneg_right hUU hlogR.le

theorem tendsto_loglog_of_ratio_bounds {f : ℝ → ℝ} {ρ lo hi : ℝ}
    (hlo : 0 < lo) (hhi : 0 < hi)
    (hh : ∀ᶠ R in atTop, lo ≤ Real.log (f R) / R ^ ρ ∧
      Real.log (f R) / R ^ ρ ≤ hi) :
    Tendsto (fun R => Real.log (Real.log (f R)) / Real.log R) atTop (𝓝 ρ) := by
  have hc (c : ℝ) : Tendsto (fun R : ℝ => ρ + Real.log c / Real.log R) atTop (𝓝 ρ) := by
    simpa only [add_zero] using
      (tendsto_const_nhds (x := ρ)).add (Real.tendsto_log_atTop.const_div_atTop (Real.log c))
  have hb : ∀ᶠ R in atTop,
      ρ + Real.log lo / Real.log R ≤ Real.log (Real.log (f R)) / Real.log R ∧
      Real.log (Real.log (f R)) / Real.log R ≤ ρ + Real.log hi / Real.log R := by
    filter_upwards [hh, eventually_gt_atTop (1 : ℝ)] with R hR hR1
    exact loglog_ratio_sandwich hlo hhi hR1 hR
  exact tendsto_of_tendsto_of_tendsto_of_le_of_le' (hc lo) (hc hi)
    (hb.mono (fun _ h => h.1)) (hb.mono (fun _ h => h.2))

theorem canonical_radial_exponent_limit (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    Tendsto (s.radialExponent i) atTop (𝓝 (s.characteristicExponent hs hstrict)) :=
  tendsto_loglog_of_ratio_bounds (s.canonicalLowerCoefficient_positive hs hstrict i)
    (s.canonicalUpperCoefficient_positive hs hstrict i)
    (s.canonical_growth_ratio_eventually hs hstrict i)

theorem canonical_radial_order (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    s.radialOrder i = s.characteristicExponent hs hstrict :=
  (s.canonical_radial_exponent_limit hs hstrict i).limsup_eq

def complexComponent (s : Scales) (i : Fin 2) (z : ℂ) : ℂ := ![s.U z, s.V z] i

theorem component_spherical_maximum (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R : ℝ} (hR : 0 ≤ R) :
    IsGreatest ((fun z => ‖s.complexComponent i z‖) '' Metric.sphere (0 : ℂ) R)
      (s.realComponent i R) := by
  have hh := s.maximum_modulus_real_axis hs hstrict hR
  fin_cases i
  · exact hh.1
  · exact hh.2

theorem component_real_norm (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R : ℝ} (hR : 0 ≤ R) : ‖s.complexComponent i (R : ℂ)‖ = s.realComponent i R := by
  have hh := s.real_axis_norm hs hstrict hR
  fin_cases i
  · exact hh.1
  · exact hh.2

theorem norm_growth_ratio_eventually_eq (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    (fun R : ℝ => Real.log ‖s.complexComponent i (R : ℂ)‖ /
      R ^ (s.characteristicExponent hs hstrict)) =ᶠ[atTop] s.growthRatio hs hstrict i := by
  filter_upwards [eventually_ge_atTop (0 : ℝ)] with R hR
  rw [s.component_real_norm hs hstrict i hR]
  rfl

theorem norm_type_identification (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    Filter.liminf (fun R : ℝ => Real.log ‖s.complexComponent i (R : ℂ)‖ /
      R ^ (s.characteristicExponent hs hstrict)) atTop = s.lowerType hs hstrict i ∧
    Filter.limsup (fun R : ℝ => Real.log ‖s.complexComponent i (R : ℂ)‖ /
      R ^ (s.characteristicExponent hs hstrict)) atTop = s.upperType hs hstrict i := by
  have hh := s.norm_growth_ratio_eventually_eq hs hstrict i
  exact ⟨Filter.liminf_congr hh, Filter.limsup_congr hh⟩

theorem canonical_norm_radial_limit (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    Tendsto (fun R : ℝ => Real.log (Real.log ‖s.complexComponent i (R : ℂ)‖) / Real.log R)
      atTop (𝓝 (s.characteristicExponent hs hstrict)) := by
  apply (s.canonical_radial_exponent_limit hs hstrict i).congr'
  filter_upwards [eventually_ge_atTop (0 : ℝ)] with R hR
  rw [s.component_real_norm hs hstrict i hR]
  rfl

def maximumModulus (s : Scales) (i : Fin 2) (R : ℝ) : ℝ :=
  sSup ((fun z => ‖s.complexComponent i z‖) '' Metric.sphere (0 : ℂ) R)

theorem maximumModulus_eq (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2)
    {R : ℝ} (hR : 0 ≤ R) : s.maximumModulus i R = s.realComponent i R := by
  have hh := s.component_spherical_maximum hs hstrict i hR
  exact hh.isLUB.csSup_eq ⟨_, hh.1⟩

theorem maximum_growth_ratio_eventually_eq (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    (fun R : ℝ => Real.log (s.maximumModulus i R) /
      R ^ (s.characteristicExponent hs hstrict)) =ᶠ[atTop] s.growthRatio hs hstrict i := by
  filter_upwards [eventually_ge_atTop (0 : ℝ)] with R hR
  rw [s.maximumModulus_eq hs hstrict i hR]
  rfl

theorem maximum_type_identification (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    Filter.liminf (fun R : ℝ => Real.log (s.maximumModulus i R) /
      R ^ (s.characteristicExponent hs hstrict)) atTop = s.lowerType hs hstrict i ∧
    Filter.limsup (fun R : ℝ => Real.log (s.maximumModulus i R) /
      R ^ (s.characteristicExponent hs hstrict)) atTop = s.upperType hs hstrict i := by
  have hh := s.maximum_growth_ratio_eventually_eq hs hstrict i
  exact ⟨Filter.liminf_congr hh, Filter.limsup_congr hh⟩

theorem canonical_maximum_type_bounds (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    s.canonicalLowerCoefficient hs hstrict i ≤
      Filter.liminf (fun R : ℝ => Real.log (s.maximumModulus i R) /
        R ^ (s.characteristicExponent hs hstrict)) atTop ∧
    Filter.liminf (fun R : ℝ => Real.log (s.maximumModulus i R) /
      R ^ (s.characteristicExponent hs hstrict)) atTop ≤
      Filter.limsup (fun R : ℝ => Real.log (s.maximumModulus i R) /
        R ^ (s.characteristicExponent hs hstrict)) atTop ∧
    Filter.limsup (fun R : ℝ => Real.log (s.maximumModulus i R) /
      R ^ (s.characteristicExponent hs hstrict)) atTop ≤ s.canonicalUpperCoefficient hs hstrict i := by
  have hh := s.maximum_type_identification hs hstrict i
  rw [hh.1, hh.2]
  exact s.canonical_type_bounds hs hstrict i

theorem canonical_maximum_radial_limit (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    Tendsto (fun R : ℝ => Real.log (Real.log (s.maximumModulus i R)) / Real.log R)
      atTop (𝓝 (s.characteristicExponent hs hstrict)) := by
  apply (s.canonical_radial_exponent_limit hs hstrict i).congr'
  filter_upwards [eventually_ge_atTop (0 : ℝ)] with R hR
  rw [s.maximumModulus_eq hs hstrict i hR]
  rfl

theorem canonical_maximum_order (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) (i : Fin 2) :
    Filter.limsup (fun R : ℝ => Real.log (Real.log (s.maximumModulus i R)) / Real.log R)
      atTop = s.characteristicExponent hs hstrict :=
  (s.canonical_maximum_radial_limit hs hstrict i).limsup_eq

end Komorebi.SpecialFunctions.Coupled.Scales
