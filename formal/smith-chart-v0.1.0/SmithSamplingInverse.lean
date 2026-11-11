import SmithSamplingIntegral

open Set Metric Real

namespace SmithSamplingInverse

theorem chart_cdf_exists_unique {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {u : ℝ} (hu : u ∈ Icc 0 1) :
    ∃! θ, θ ∈ Icc 0 (2 * Real.pi) ∧ SmithPoisson.chartCdf ρ θ = u := by
  have hm : u ∈ Icc (SmithPoisson.chartCdf ρ 0) (SmithPoisson.chartCdf ρ (2 * Real.pi)) := by
    simpa [SmithPoisson.chart_cdf_zero, SmithPoisson.chart_cdf_two_pi hρ0 hρ1] using hu
  obtain ⟨θ, hθ, hvalue⟩ := intermediate_value_Icc (by positivity : (0 : ℝ) ≤ 2 * Real.pi)
    (SmithPoisson.chart_cdf_continuous hρ0 hρ1).continuousOn hm
  refine ⟨θ, ⟨hθ, hvalue⟩, ?_⟩
  intro x hx
  exact (SmithPoisson.chart_cdf_strictMono hρ0 hρ1).injective (hx.2.trans hvalue.symm)

noncomputable def chartQuantile {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (u : Icc (0 : ℝ) 1) : ℝ :=
  Classical.choose (chart_cdf_exists_unique hρ0 hρ1 u.property)

theorem chart_quantile_spec {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (u : Icc (0 : ℝ) 1) :
    chartQuantile hρ0 hρ1 u ∈ Icc 0 (2 * Real.pi) ∧
      SmithPoisson.chartCdf ρ (chartQuantile hρ0 hρ1 u) = u := by
  exact (Classical.choose_spec (chart_cdf_exists_unique hρ0 hρ1 u.property)).1

theorem chart_quantile_strictMono {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    StrictMono (chartQuantile hρ0 hρ1) := by
  intro u v huv
  apply ((SmithPoisson.chart_cdf_strictMono hρ0 hρ1).lt_iff_lt).mp
  rw [(chart_quantile_spec hρ0 hρ1 u).2, (chart_quantile_spec hρ0 hρ1 v).2]
  exact huv

theorem chart_cdf_mem_unit {ρ θ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hθ : θ ∈ Icc 0 (2 * Real.pi)) : SmithPoisson.chartCdf ρ θ ∈ Icc 0 1 := by
  constructor
  · calc
      0 = SmithPoisson.chartCdf ρ 0 := (SmithPoisson.chart_cdf_zero ρ).symm
      _ ≤ SmithPoisson.chartCdf ρ θ := (SmithPoisson.chart_cdf_strictMono hρ0 hρ1).monotone hθ.1
  · calc
      SmithPoisson.chartCdf ρ θ ≤ SmithPoisson.chartCdf ρ (2 * Real.pi) :=
        (SmithPoisson.chart_cdf_strictMono hρ0 hρ1).monotone hθ.2
      _ = 1 := SmithPoisson.chart_cdf_two_pi hρ0 hρ1

/-- The abstract quantile is the inverse of the integral CDF on its angular interval. -/
theorem chart_quantile_left_inverse {ρ θ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    (hθ : θ ∈ Icc 0 (2 * Real.pi)) :
    chartQuantile hρ0 hρ1 ⟨SmithPoisson.chartCdf ρ θ, chart_cdf_mem_unit hρ0 hρ1 hθ⟩ = θ := by
  apply (SmithPoisson.chart_cdf_strictMono hρ0 hρ1).injective
  exact (chart_quantile_spec hρ0 hρ1
    ⟨SmithPoisson.chartCdf ρ θ, chart_cdf_mem_unit hρ0 hρ1 hθ⟩).2

end SmithSamplingInverse
