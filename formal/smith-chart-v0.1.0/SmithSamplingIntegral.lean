import Mathlib.Topology.Order.IntermediateValue
import Mathlib.Analysis.Complex.Basic
import Mathlib.Tactic.FieldSimp
import Mathlib.Tactic.Linarith
import Mathlib.Analysis.Complex.Poisson
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FunProp
import Mathlib.MeasureTheory.Integral.IntervalIntegral.Periodic
import Mathlib.Analysis.Calculus.Deriv.MeanValue

open Set Metric Real

namespace SmithSamplingExistence

theorem equal_mass_partition {a b : ℝ} (hab : a < b) {F : ℝ → ℝ}
    (hcont : ContinuousOn F (Icc a b)) (hmono : StrictMonoOn F (Icc a b))
    (hzero : F a = 0) (hone : F b = 1) {N : ℕ} (hN : 0 < N) :
    ∃ cuts : Fin (N + 1) → ℝ,
      (∀ i, cuts i ∈ Icc a b) ∧
      (∀ i, F (cuts i) = (i.val : ℝ) / N) ∧
      StrictMono cuts ∧ cuts 0 = a ∧ cuts (Fin.last N) = b ∧
      ∀ i : Fin N, F (cuts i.succ) - F (cuts i.castSucc) = 1 / N := by
  have hNpos : (0 : ℝ) < N := by exact_mod_cast hN
  have hexists (i : Fin (N + 1)) : ∃ x ∈ Icc a b, F x = (i.val : ℝ) / N := by
    have hi : i.val ≤ N := by omega
    have hireal : (i.val : ℝ) ≤ N := by exact_mod_cast hi
    have hm : (i.val : ℝ) / N ∈ Icc (F a) (F b) := by
      rw [hzero, hone]
      exact ⟨div_nonneg (Nat.cast_nonneg _) hNpos.le, (div_le_one hNpos).2 hireal⟩
    exact intermediate_value_Icc hab.le hcont hm
  choose cuts hmem hval using hexists
  refine ⟨cuts, hmem, hval, ?_, ?_, ?_, ?_⟩
  · intro i j hij
    apply (hmono.lt_iff_lt (hmem i) (hmem j)).mp
    rw [hval, hval]
    have hv : (i.val : ℝ) < j.val := by exact_mod_cast hij
    exact div_lt_div_of_pos_right hv hNpos
  · apply (hmono.eq_iff_eq (hmem 0) (left_mem_Icc.mpr hab.le)).mp
    simp [hval, hzero]
  · apply (hmono.eq_iff_eq (hmem (Fin.last N)) (right_mem_Icc.mpr hab.le)).mp
    rw [hval, hone]
    simp [hNpos.ne']
  · intro i
    rw [hval, hval]
    simp only [Fin.val_succ, Fin.val_castSucc, Nat.cast_add, Nat.cast_one]
    field_simp; ring

end SmithSamplingExistence

namespace SmithPoisson

theorem poisson_kernel_circle_average {w : ℂ} (hw : ‖w‖ < 1) :
    Real.circleAverage (fun z => (poissonKernel 0 w z : ℂ)) 0 1 = 1 := by
  have hw' : w ∈ Metric.ball (0 : ℂ) (1 : ℝ) := by
    simpa [Metric.mem_ball, dist_zero_right] using hw
  have hf : DiffContOnCl ℂ (fun _ : ℂ => (1 : ℂ)) (Metric.ball 0 (1 : ℝ)) := by
    exact diffContOnCl_const
  have h := hf.circleAverage_poissonKernel_smul hw'
  have hfun : (poissonKernel 0 w • (fun _ : ℂ => (1 : ℂ))) =
      (fun z => (poissonKernel 0 w z : ℂ)) := by
    funext z
    simp
  rw [hfun] at h
  exact h

theorem poisson_kernel_real_circle_average {w : ℂ} (hw : ‖w‖ < 1) :
    Real.circleAverage (poissonKernel 0 w) 0 1 = 1 := by
  have h := congrArg Complex.re (poisson_kernel_circle_average hw)
  simp only [Real.circleAverage, intervalIntegral.integral_ofReal, Complex.smul_re,
    Complex.ofReal_re, Complex.one_re] at h ⊢
  exact h

theorem poisson_kernel_trig (q θ : ℝ) :
    poissonKernel 0 (q : ℂ) (circleMap 0 1 θ) =
      (1 - q ^ 2) / (1 - 2 * q * Real.cos θ + q ^ 2) := by
  have hd : ‖circleMap 0 1 θ - (q : ℂ)‖ ^ 2 =
      1 - 2 * q * Real.cos θ + q ^ 2 := by
    rw [← Complex.normSq_eq_norm_sq, Complex.normSq_apply]
    simp only [Complex.sub_re, Complex.sub_im, Complex.ofReal_re, Complex.ofReal_im,
      circleMap_zero_re, circleMap_zero_im, one_mul, sub_zero]
    nlinarith [Real.cos_sq_add_sin_sq θ]
  unfold poissonKernel
  simp only [sub_zero, norm_circleMap_zero, abs_one, one_pow, Complex.norm_real,
    Real.norm_eq_abs, sq_abs, hd]

theorem poisson_trig_integral {q : ℝ} (hq : |q| < 1) :
    (∫ θ in (0 : ℝ)..2 * Real.pi,
      (1 - q ^ 2) / (1 - 2 * q * Real.cos θ + q ^ 2)) = 2 * Real.pi := by
  have hw : ‖(q : ℂ)‖ < 1 := by simpa using hq
  have h := poisson_kernel_real_circle_average hw
  simp only [Real.circleAverage, smul_eq_mul, poisson_kernel_trig] at h
  have hp : (2 * Real.pi : ℝ) ≠ 0 := by positivity
  have hh := congrArg (fun x : ℝ => (2 * Real.pi) * x) h
  simpa [mul_assoc, hp] using hh

theorem integral_double_periodic {f : ℝ → ℝ}
    (hper : Function.Periodic f (2 * Real.pi)) (hf : Continuous f) :
    (∫ x in (0 : ℝ)..2 * Real.pi, f (2 * x)) =
      ∫ x in (0 : ℝ)..2 * Real.pi, f x := by
  have hfi : ∀ a b, IntervalIntegrable f MeasureTheory.volume a b :=
    fun a b => hf.intervalIntegrable _ _
  have hi : (∫ x in (0 : ℝ)..2 * (2 * Real.pi), f x) =
      2 * ∫ x in (0 : ℝ)..2 * Real.pi, f x := by
    simpa using hper.intervalIntegral_add_zsmul_eq (2 : ℤ) (0 : ℝ) hfi
  rw [intervalIntegral.integral_comp_mul_left f (by norm_num : (2 : ℝ) ≠ 0)]
  simp only [mul_zero, hi, smul_eq_mul]
  ring

/-- The chart's doubled-angle Poisson density integrates to one. -/
theorem doubled_poisson_density_integral {q : ℝ} (hq0 : 0 ≤ q) (hq1 : q < 1) :
    (∫ θ in (0 : ℝ)..2 * Real.pi,
      (1 - q ^ 2) / (2 * Real.pi * (1 - 2 * q * Real.cos (2 * θ) + q ^ 2))) = 1 := by
  have hden (θ : ℝ) : 0 < 1 - 2 * q * Real.cos θ + q ^ 2 := by
    have hm := mul_nonneg hq0 (sub_nonneg.mpr (Real.cos_le_one θ))
    have hs := sq_pos_of_pos (sub_pos.mpr hq1)
    nlinarith
  let f : ℝ → ℝ := fun θ => (1 - q ^ 2) / (1 - 2 * q * Real.cos θ + q ^ 2)
  have hf : Continuous f := by
    dsimp [f]
    apply Continuous.div (by fun_prop) (by fun_prop)
    intro θ
    exact (hden θ).ne'
  have hper : Function.Periodic f (2 * Real.pi) := by
    intro θ
    dsimp [f]
    rw [Real.cos_add_two_pi]
  have hdouble : (∫ θ in (0 : ℝ)..2 * Real.pi, f (2 * θ)) = 2 * Real.pi := by
    rw [integral_double_periodic hper hf]
    exact poisson_trig_integral (by simpa [abs_of_nonneg hq0] using hq1)
  have heq : (fun θ : ℝ =>
      (1 - q ^ 2) / (2 * Real.pi * (1 - 2 * q * Real.cos (2 * θ) + q ^ 2))) =
      (fun θ => (2 * Real.pi)⁻¹ * f (2 * θ)) := by
    funext θ
    dsimp [f]
    simp [div_eq_mul_inv, mul_inv_rev, mul_assoc, mul_comm, mul_left_comm]
  rw [heq, intervalIntegral.integral_const_mul, hdouble]
  exact inv_mul_cancel₀ (by positivity)

noncomputable def chartDensity (ρ θ : ℝ) : ℝ :=
  (1 - ρ ^ 4) / (2 * Real.pi * (1 - 2 * ρ ^ 2 * Real.cos (2 * θ) + ρ ^ 4))

theorem chart_density_integral {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    (∫ θ in (0 : ℝ)..2 * Real.pi, chartDensity ρ θ) = 1 := by
  have hq0 : 0 ≤ ρ ^ 2 := sq_nonneg _
  have hq1 : ρ ^ 2 < 1 := by
    nlinarith [mul_nonneg hρ0 (sub_nonneg.mpr hρ1.le)]
  simpa only [chartDensity, ← pow_mul, Nat.reduceMul] using
    (doubled_poisson_density_integral hq0 hq1)

theorem chart_denominator_pos {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) (θ : ℝ) :
    0 < 1 - 2 * ρ ^ 2 * Real.cos (2 * θ) + ρ ^ 4 := by
  have hq1 : ρ ^ 2 < 1 := by
    nlinarith [mul_nonneg hρ0 (sub_nonneg.mpr hρ1.le)]
  have hm := mul_nonneg (sq_nonneg ρ) (sub_nonneg.mpr (Real.cos_le_one (2 * θ)))
  have hs := sq_pos_of_pos (sub_pos.mpr hq1)
  nlinarith

theorem chart_density_pos {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) (θ : ℝ) :
    0 < chartDensity ρ θ := by
  have hq1 : ρ ^ 2 < 1 := by
    nlinarith [mul_nonneg hρ0 (sub_nonneg.mpr hρ1.le)]
  have hn : 0 < 1 - ρ ^ 4 := by
    nlinarith [mul_nonneg (sq_nonneg ρ) (sub_nonneg.mpr hq1.le)]
  unfold chartDensity
  exact div_pos hn (mul_pos (by positivity) (chart_denominator_pos hρ0 hρ1 θ))

theorem chart_density_continuous {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    Continuous (chartDensity ρ) := by
  unfold chartDensity
  apply Continuous.div (by fun_prop) (by fun_prop)
  intro θ
  exact mul_ne_zero (by positivity) (ne_of_gt (chart_denominator_pos hρ0 hρ1 θ))

noncomputable def chartCdf (ρ x : ℝ) : ℝ := ∫ θ in (0 : ℝ)..x, chartDensity ρ θ

theorem chart_cdf_hasDerivAt {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) (x : ℝ) :
    HasDerivAt (chartCdf ρ) (chartDensity ρ x) x := by
  have hc := chart_density_continuous hρ0 hρ1
  unfold chartCdf
  exact intervalIntegral.integral_hasDerivAt_right (hc.intervalIntegrable _ _)
    hc.aestronglyMeasurable.stronglyMeasurableAtFilter hc.continuousAt

theorem chart_cdf_continuous {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    Continuous (chartCdf ρ) := by
  exact continuous_iff_continuousAt.mpr fun x => (chart_cdf_hasDerivAt hρ0 hρ1 x).continuousAt

theorem chart_cdf_strictMono {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    StrictMono (chartCdf ρ) := by
  apply strictMono_of_deriv_pos
  intro x
  rw [(chart_cdf_hasDerivAt hρ0 hρ1 x).deriv]
  exact chart_density_pos hρ0 hρ1 x

theorem chart_cdf_zero (ρ : ℝ) : chartCdf ρ 0 = 0 := by simp [chartCdf]

theorem chart_cdf_two_pi {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1) :
    chartCdf ρ (2 * Real.pi) = 1 := chart_density_integral hρ0 hρ1

/-- Existence of an ordered equal-mass partition for the chart's actual density. -/
theorem chart_equal_mass_partition {ρ : ℝ} (hρ0 : 0 ≤ ρ) (hρ1 : ρ < 1)
    {N : ℕ} (hN : 0 < N) :
    ∃ cuts : Fin (N + 1) → ℝ,
      (∀ i, cuts i ∈ Icc 0 (2 * Real.pi)) ∧
      StrictMono cuts ∧ cuts 0 = 0 ∧ cuts (Fin.last N) = 2 * Real.pi ∧
      ∀ i : Fin N, (∫ θ in cuts i.castSucc..cuts i.succ, chartDensity ρ θ) = 1 / N := by
  obtain ⟨cuts, hmem, hval, hmono, hzero, hlast, hmass⟩ :=
    SmithSamplingExistence.equal_mass_partition (by positivity : (0 : ℝ) < 2 * Real.pi)
      (chart_cdf_continuous hρ0 hρ1).continuousOn
      ((chart_cdf_strictMono hρ0 hρ1).strictMonoOn (Icc 0 (2 * Real.pi))) (chart_cdf_zero ρ)
      (chart_cdf_two_pi hρ0 hρ1) hN
  refine ⟨cuts, hmem, hmono, hzero, hlast, ?_⟩
  intro i
  have hc := chart_density_continuous hρ0 hρ1
  have ha : IntervalIntegrable (chartDensity ρ) MeasureTheory.volume 0 (cuts i.castSucc) :=
    hc.intervalIntegrable _ _
  have hb : IntervalIntegrable (chartDensity ρ) MeasureTheory.volume (cuts i.castSucc) (cuts i.succ) :=
    hc.intervalIntegrable _ _
  have hadd := intervalIntegral.integral_add_adjacent_intervals ha hb
  have hi := hmass i
  dsimp [chartCdf] at hi
  linarith

/-- At zero radius the sampling density is uniform. -/
theorem chart_density_zero_radius (θ : ℝ) : chartDensity 0 θ = (2 * Real.pi)⁻¹ := by
  simp [chartDensity, div_eq_mul_inv]

/-- At zero radius the cumulative distribution is the uniform angular coordinate. -/
theorem chart_cdf_zero_radius (θ : ℝ) : chartCdf 0 θ = θ / (2 * Real.pi) := by
  simp [chartCdf, chartDensity, div_eq_mul_inv, mul_comm]; ring

end SmithPoisson
