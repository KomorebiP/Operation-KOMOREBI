import SmithSamplingIntegral
import SmithSamplingInverse
import Mathlib.Analysis.SpecialFunctions.Trigonometric.ArctanDeriv
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith

open Set Real

namespace SmithExplicitInverse

noncomputable def principalCdf (q θ : ℝ) : ℝ :=
  (2 * Real.pi)⁻¹ * Real.arctan (((1 + q) / (1 - q)) * Real.tan θ)

theorem principalCdf_hasDerivAt {q θ : ℝ} (hq0 : 0 ≤ q) (hq1 : q < 1)
    (hθ : θ ∈ Ioo (-(Real.pi / 2)) (Real.pi / 2)) :
    HasDerivAt (principalCdf q)
      ((1 - q ^ 2) / (2 * Real.pi * (1 - 2 * q * Real.cos (2 * θ) + q ^ 2))) θ := by
  have hc : Real.cos θ ≠ 0 := (Real.cos_pos_of_mem_Ioo hθ).ne'
  have hq : 1 - q ≠ 0 := (sub_pos.mpr hq1).ne'
  have hp : (2 * Real.pi : ℝ) ≠ 0 := by positivity
  have hd : 1 - 2 * q * Real.cos (2 * θ) + q ^ 2 ≠ 0 := by
    have hm := mul_nonneg hq0 (sub_nonneg.mpr (Real.cos_le_one (2 * θ)))
    have hs := sq_pos_of_pos (sub_pos.mpr hq1)
    nlinarith
  have hd' : 1 - 2 * q * (Real.cos θ ^ 2 - Real.sin θ ^ 2) + q ^ 2 ≠ 0 := by
    simpa [Real.cos_two_mul'] using hd
  have hd'' : 1 - q * 2 * (Real.cos θ ^ 2 - Real.sin θ ^ 2) + q ^ 2 ≠ 0 := by
    have he : 1 - q * 2 * (Real.cos θ ^ 2 - Real.sin θ ^ 2) + q ^ 2 =
        1 - 2 * q * (Real.cos θ ^ 2 - Real.sin θ ^ 2) + q ^ 2 := by ring
    rw [he]
    exact hd'
  have ha : 1 + (((1 + q) / (1 - q)) * Real.tan θ) ^ 2 ≠ 0 := by positivity
  have h := (((Real.hasDerivAt_tan hc).const_mul ((1 + q) / (1 - q))).arctan).const_mul
    ((2 * Real.pi)⁻¹)
  convert h using 1
  all_goals try rfl
  rw [Real.tan_eq_sin_div_cos, Real.cos_two_mul']
  field_simp [hc, hq, hp, hd, hd', hd'', ha]
  have hs : Real.sin θ ^ 2 = 1 - Real.cos θ ^ 2 := by
    nlinarith [Real.cos_sq_add_sin_sq θ]
  rw [hs]
  ring

/-- The arctangent expression equals the integral CDF on the principal branch. -/
theorem principalCdf_eq_chartCdf {ρ θ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hθ : θ ∈ Ioo (-(Real.pi / 2)) (Real.pi / 2)) :
    principalCdf (ρ ^ 2) θ = SmithPoisson.chartCdf ρ θ := by
  have hq0 : 0 ≤ ρ ^ 2 := sq_nonneg _
  have hq1 : ρ ^ 2 < 1 := by
    nlinarith [mul_nonneg hρ0 (sub_nonneg.mpr hρ1.le)]
  have hd1 : DifferentiableOn ℝ (principalCdf (ρ ^ 2))
      (Ioo (-(Real.pi / 2)) (Real.pi / 2)) := by
    intro x hx
    exact (principalCdf_hasDerivAt hq0 hq1 hx).differentiableAt.differentiableWithinAt
  have hd2 : DifferentiableOn ℝ (SmithPoisson.chartCdf ρ)
      (Ioo (-(Real.pi / 2)) (Real.pi / 2)) := by
    intro x _
    exact (SmithPoisson.chart_cdf_hasDerivAt hρ0 hρ1 x).differentiableAt.differentiableWithinAt
  have hdeq : EqOn (deriv (principalCdf (ρ ^ 2))) (deriv (SmithPoisson.chartCdf ρ))
      (Ioo (-(Real.pi / 2)) (Real.pi / 2)) := by
    intro x hx
    rw [(principalCdf_hasDerivAt hq0 hq1 hx).deriv,
      (SmithPoisson.chart_cdf_hasDerivAt hρ0 hρ1 x).deriv]
    simp only [SmithPoisson.chartDensity, ← pow_mul, Nat.reduceMul]
  have hzero : (0 : ℝ) ∈ Ioo (-(Real.pi / 2)) (Real.pi / 2) := by
    have hp : 0 < Real.pi / 2 := by positivity
    exact ⟨neg_lt_zero.mpr hp, hp⟩
  have hvalue : principalCdf (ρ ^ 2) 0 = SmithPoisson.chartCdf ρ 0 := by
    simp [principalCdf, SmithPoisson.chart_cdf_zero]
  exact (isOpen_Ioo.eqOn_of_deriv_eq isPreconnected_Ioo hd1 hd2 hdeq hzero hvalue) hθ

noncomputable def principalQuantile (ρ u : ℝ) : ℝ :=
  Real.arctan (((1 - ρ ^ 2) / (1 + ρ ^ 2)) * Real.tan (2 * Real.pi * u))

theorem principal_quantile_spec {ρ u : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hu : u ∈ Ico (0 : ℝ) (1 / 4)) :
    principalQuantile ρ u ∈ Icc 0 (2 * Real.pi) ∧
      SmithPoisson.chartCdf ρ (principalQuantile ρ u) = u := by
  have hq1 : ρ ^ 2 < 1 := by
    nlinarith [mul_nonneg hρ0 (sub_nonneg.mpr hρ1.le)]
  have hp : 0 < Real.pi := Real.pi_pos
  have hx0 : 0 ≤ 2 * Real.pi * u := mul_nonneg (by positivity) hu.1
  have hx1 : 2 * Real.pi * u < Real.pi / 2 := by
    nlinarith [mul_pos hp (sub_pos.mpr hu.2)]
  have hxlow : -(Real.pi / 2) < 2 * Real.pi * u := by linarith
  have ht : 0 ≤ Real.tan (2 * Real.pi * u) :=
    Real.tan_nonneg_of_nonneg_of_le_pi_div_two hx0 hx1.le
  have hbeta : 0 ≤ (1 - ρ ^ 2) / (1 + ρ ^ 2) :=
    div_nonneg (sub_nonneg.mpr hq1.le) (by positivity)
  have hθ0 : 0 ≤ principalQuantile ρ u := by
    exact Real.arctan_nonneg.mpr (mul_nonneg hbeta ht)
  have hθ : principalQuantile ρ u ∈ Ioo (-(Real.pi / 2)) (Real.pi / 2) :=
    Real.arctan_mem_Ioo _
  have hθrange : principalQuantile ρ u ∈ Icc 0 (2 * Real.pi) := by
    exact ⟨hθ0, by linarith [hθ.2]⟩
  refine ⟨hθrange, ?_⟩
  rw [← principalCdf_eq_chartCdf hρ0 hρ1 hθ]
  unfold principalCdf principalQuantile
  rw [Real.tan_arctan]
  have hscale : ((1 + ρ ^ 2) / (1 - ρ ^ 2)) *
      (((1 - ρ ^ 2) / (1 + ρ ^ 2)) * Real.tan (2 * Real.pi * u)) =
      Real.tan (2 * Real.pi * u) := by
    have hnum : 1 - ρ ^ 2 ≠ 0 := (sub_pos.mpr hq1).ne'
    have hden : 1 + ρ ^ 2 ≠ 0 := by positivity
    field_simp [hnum, hden]
  rw [hscale, Real.arctan_tan hxlow hx1]
  field_simp [Real.pi_ne_zero]

theorem principal_quantile_eq_abstract {ρ u : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hu : u ∈ Ico (0 : ℝ) (1 / 4)) :
    SmithSamplingInverse.chartQuantile hρ0 hρ1
      ⟨u, ⟨hu.1, by linarith [hu.2]⟩⟩ = principalQuantile ρ u := by
  apply (SmithPoisson.chart_cdf_strictMono hρ0 hρ1).injective
  rw [(SmithSamplingInverse.chart_quantile_spec hρ0 hρ1 _).2]
  exact (principal_quantile_spec hρ0 hρ1 hu).2.symm

theorem chart_density_periodic_pi (ρ : ℝ) :
    Function.Periodic (SmithPoisson.chartDensity ρ) Real.pi := by
  intro θ
  unfold SmithPoisson.chartDensity
  have harg : 2 * (θ + Real.pi) = 2 * θ + 2 * Real.pi := by ring
  rw [harg, Real.cos_add_two_pi]

theorem chart_cdf_pi {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    SmithPoisson.chartCdf ρ Real.pi = 1 / 2 := by
  have hc := SmithPoisson.chart_density_continuous hρ0 hρ1
  have hfi : ∀ a b, IntervalIntegrable (SmithPoisson.chartDensity ρ) MeasureTheory.volume a b :=
    fun a b => hc.intervalIntegrable _ _
  have hdouble : (∫ θ in (0 : ℝ)..2 * Real.pi, SmithPoisson.chartDensity ρ θ) =
      2 * (∫ θ in (0 : ℝ)..Real.pi, SmithPoisson.chartDensity ρ θ) := by
    simpa using (chart_density_periodic_pi ρ).intervalIntegral_add_zsmul_eq (2 : ℤ) (0 : ℝ) hfi
  have htotal := SmithPoisson.chart_density_integral hρ0 hρ1
  unfold SmithPoisson.chartCdf
  linarith

theorem chart_cdf_add_pi {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) (θ : ℝ) :
    SmithPoisson.chartCdf ρ (θ + Real.pi) = SmithPoisson.chartCdf ρ θ + 1 / 2 := by
  have hc := SmithPoisson.chart_density_continuous hρ0 hρ1
  have ha : IntervalIntegrable (SmithPoisson.chartDensity ρ) MeasureTheory.volume 0 θ :=
    hc.intervalIntegrable _ _
  have hb : IntervalIntegrable (SmithPoisson.chartDensity ρ) MeasureTheory.volume θ (θ + Real.pi) :=
    hc.intervalIntegrable _ _
  have hadd := intervalIntegral.integral_add_adjacent_intervals ha hb
  have hshift := (chart_density_periodic_pi ρ).intervalIntegral_add_eq θ 0
  have hpi := chart_cdf_pi hρ0 hρ1
  simp only [zero_add] at hshift
  unfold SmithPoisson.chartCdf at hpi ⊢
  linarith

theorem chart_density_reflect_pi (ρ θ : ℝ) :
    SmithPoisson.chartDensity ρ (Real.pi - θ) = SmithPoisson.chartDensity ρ θ := by
  unfold SmithPoisson.chartDensity
  have harg : 2 * (Real.pi - θ) = 2 * Real.pi - 2 * θ := by ring
  rw [harg, Real.cos_two_pi_sub]

theorem chart_cdf_half_pi {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    SmithPoisson.chartCdf ρ (Real.pi / 2) = 1 / 4 := by
  have hc := SmithPoisson.chart_density_continuous hρ0 hρ1
  have ha : IntervalIntegrable (SmithPoisson.chartDensity ρ) MeasureTheory.volume 0 (Real.pi / 2) :=
    hc.intervalIntegrable _ _
  have hb : IntervalIntegrable (SmithPoisson.chartDensity ρ) MeasureTheory.volume
      (Real.pi / 2) Real.pi := hc.intervalIntegrable _ _
  have hadd := intervalIntegral.integral_add_adjacent_intervals ha hb
  have heq : (fun x : ℝ => SmithPoisson.chartDensity ρ (Real.pi - x)) =
      SmithPoisson.chartDensity ρ := by
    funext x
    exact chart_density_reflect_pi ρ x
  have hcomp := intervalIntegral.integral_comp_sub_left
    (a := (0 : ℝ)) (b := Real.pi / 2) (SmithPoisson.chartDensity ρ) Real.pi
  rw [heq] at hcomp
  have hhalf : Real.pi - Real.pi / 2 = Real.pi / 2 := by ring
  simp only [sub_zero, hhalf] at hcomp
  have hpi := chart_cdf_pi hρ0 hρ1
  unfold SmithPoisson.chartCdf at hpi ⊢
  linarith

theorem chart_cdf_three_half_pi {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    SmithPoisson.chartCdf ρ (3 * Real.pi / 2) = 3 / 4 := by
  have hshift := chart_cdf_add_pi hρ0 hρ1 (Real.pi / 2)
  rw [chart_cdf_half_pi hρ0 hρ1] at hshift
  have harg : Real.pi / 2 + Real.pi = 3 * Real.pi / 2 := by ring
  rw [harg] at hshift
  linarith

/-- The principal inverse also works for negative masses on the lifted CDF. -/
theorem principal_quantile_cdf_signed {ρ u : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hu : u ∈ Ioo (-(1 / 4) : ℝ) (1 / 4)) :
    SmithPoisson.chartCdf ρ (principalQuantile ρ u) = u := by
  have hq1 : ρ ^ 2 < 1 := by
    nlinarith [mul_nonneg hρ0 (sub_nonneg.mpr hρ1.le)]
  have hp : 0 < Real.pi := Real.pi_pos
  have hlow : -(Real.pi / 2) < 2 * Real.pi * u := by
    have h := mul_pos hp (show 0 < u + 1 / 4 by linarith [hu.1])
    nlinarith
  have hhigh : 2 * Real.pi * u < Real.pi / 2 := by
    have h := mul_pos hp (show 0 < 1 / 4 - u by linarith [hu.2])
    nlinarith
  have hθ : principalQuantile ρ u ∈ Ioo (-(Real.pi / 2)) (Real.pi / 2) :=
    Real.arctan_mem_Ioo _
  rw [← principalCdf_eq_chartCdf hρ0 hρ1 hθ]
  unfold principalCdf principalQuantile
  rw [Real.tan_arctan]
  have hscale : ((1 + ρ ^ 2) / (1 - ρ ^ 2)) *
      (((1 - ρ ^ 2) / (1 + ρ ^ 2)) * Real.tan (2 * Real.pi * u)) =
      Real.tan (2 * Real.pi * u) := by
    have hnum : 1 - ρ ^ 2 ≠ 0 := (sub_pos.mpr hq1).ne'
    have hden : 1 + ρ ^ 2 ≠ 0 := by positivity
    field_simp [hnum, hden]
  rw [hscale, Real.arctan_tan hlow hhigh]
  field_simp [Real.pi_ne_zero]

noncomputable def middleQuantile (ρ u : ℝ) : ℝ :=
  principalQuantile ρ (u - 1 / 2) + Real.pi

theorem middle_quantile_spec {ρ u : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hu : u ∈ Ioo (1 / 4 : ℝ) (3 / 4)) :
    middleQuantile ρ u ∈ Icc 0 (2 * Real.pi) ∧
      SmithPoisson.chartCdf ρ (middleQuantile ρ u) = u := by
  have hv : u - 1 / 2 ∈ Ioo (-(1 / 4) : ℝ) (1 / 4) := by
    constructor <;> linarith [hu.1, hu.2]
  have hθ : principalQuantile ρ (u - 1 / 2) ∈
      Ioo (-(Real.pi / 2)) (Real.pi / 2) := Real.arctan_mem_Ioo _
  constructor
  · unfold middleQuantile
    constructor <;> linarith [hθ.1, hθ.2, Real.pi_pos]
  · unfold middleQuantile
    rw [chart_cdf_add_pi hρ0 hρ1, principal_quantile_cdf_signed hρ0 hρ1 hv]
    ring

noncomputable def finalQuantile (ρ u : ℝ) : ℝ :=
  principalQuantile ρ (u - 1) + 2 * Real.pi

theorem final_quantile_spec {ρ u : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hu : u ∈ Ioc (3 / 4 : ℝ) 1) :
    finalQuantile ρ u ∈ Icc 0 (2 * Real.pi) ∧
      SmithPoisson.chartCdf ρ (finalQuantile ρ u) = u := by
  have hv : u - 1 ∈ Ioo (-(1 / 4) : ℝ) (1 / 4) := by
    constructor <;> linarith [hu.1, hu.2]
  have hv0 : u - 1 ≤ 0 := by linarith [hu.2]
  have hq1 : ρ ^ 2 < 1 := by
    nlinarith [mul_nonneg hρ0 (sub_nonneg.mpr hρ1.le)]
  have harg0 : 2 * Real.pi * (u - 1) ≤ 0 :=
    mul_nonpos_of_nonneg_of_nonpos (by positivity) hv0
  have harglow : -(Real.pi / 2) ≤ 2 * Real.pi * (u - 1) := by
    have h := mul_pos Real.pi_pos (show 0 < (u - 1) + 1 / 4 by linarith [hv.1])
    nlinarith
  have htan : Real.tan (2 * Real.pi * (u - 1)) ≤ 0 :=
    Real.tan_nonpos_of_nonpos_of_neg_pi_div_two_le harg0 harglow
  have hbeta : 0 ≤ (1 - ρ ^ 2) / (1 + ρ ^ 2) :=
    div_nonneg (sub_nonneg.mpr hq1.le) (by positivity)
  have hθ0 : principalQuantile ρ (u - 1) ≤ 0 := by
    exact Real.arctan_le_zero.mpr (mul_nonpos_of_nonneg_of_nonpos hbeta htan)
  have hθ : principalQuantile ρ (u - 1) ∈
      Ioo (-(Real.pi / 2)) (Real.pi / 2) := Real.arctan_mem_Ioo _
  constructor
  · unfold finalQuantile
    constructor <;> linarith [hθ.1, hθ0, Real.pi_pos]
  · unfold finalQuantile
    have harg : principalQuantile ρ (u - 1) + 2 * Real.pi =
        (principalQuantile ρ (u - 1) + Real.pi) + Real.pi := by ring
    rw [harg, chart_cdf_add_pi hρ0 hρ1, chart_cdf_add_pi hρ0 hρ1,
      principal_quantile_cdf_signed hρ0 hρ1 hv]
    ring

/-- An explicit branch-aware inverse of the chart's integral CDF. -/
noncomputable def explicitQuantile (ρ u : ℝ) : ℝ :=
  if u < 1 / 4 then principalQuantile ρ u
  else if u = 1 / 4 then Real.pi / 2
  else if u < 3 / 4 then middleQuantile ρ u
  else if u = 3 / 4 then 3 * Real.pi / 2
  else finalQuantile ρ u

theorem explicit_quantile_spec {ρ u : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hu : u ∈ Icc (0 : ℝ) 1) :
    explicitQuantile ρ u ∈ Icc 0 (2 * Real.pi) ∧
      SmithPoisson.chartCdf ρ (explicitQuantile ρ u) = u := by
  unfold explicitQuantile
  split_ifs with h1 h2 h3 h4
  · exact principal_quantile_spec hρ0 hρ1 ⟨hu.1, h1⟩
  · subst u
    exact ⟨⟨by positivity, by linarith [Real.pi_pos]⟩, chart_cdf_half_pi hρ0 hρ1⟩
  · have hl : (1 / 4 : ℝ) < u := lt_of_le_of_ne (le_of_not_gt h1) (Ne.symm h2)
    exact middle_quantile_spec hρ0 hρ1 ⟨hl, h3⟩
  · subst u
    exact ⟨⟨by positivity, by linarith [Real.pi_pos]⟩, chart_cdf_three_half_pi hρ0 hρ1⟩
  · have hl : (3 / 4 : ℝ) < u := lt_of_le_of_ne (le_of_not_gt h3) (Ne.symm h4)
    exact final_quantile_spec hρ0 hρ1 ⟨hl, hu.2⟩

/-- The explicit branches agree with the unique abstract inverse on `[0,1]`. -/
theorem explicit_quantile_eq_abstract {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (u : Icc (0 : ℝ) 1) :
    SmithSamplingInverse.chartQuantile hρ0 hρ1 u = explicitQuantile ρ u := by
  apply (SmithPoisson.chart_cdf_strictMono hρ0 hρ1).injective
  calc
    SmithPoisson.chartCdf ρ (SmithSamplingInverse.chartQuantile hρ0 hρ1 u) = u :=
      (SmithSamplingInverse.chart_quantile_spec hρ0 hρ1 u).2
    _ = SmithPoisson.chartCdf ρ (explicitQuantile ρ u) :=
      (explicit_quantile_spec hρ0 hρ1 u.property).2.symm

/-- The explicit branches reduce to uniform angles at zero radius. -/
theorem explicit_quantile_zero_radius {u : ℝ} (hu : u ∈ Icc (0 : ℝ) 1) :
    explicitQuantile 0 u = 2 * Real.pi * u := by
  have h := (explicit_quantile_spec (ρ := 0) (by norm_num) (by norm_num) hu).2
  rw [SmithPoisson.chart_cdf_zero_radius] at h
  have hp : (2 * Real.pi : ℝ) ≠ 0 := by positivity
  have hh := (div_eq_iff hp).mp h
  simpa [mul_comm] using hh

end SmithExplicitInverse
