import Mathlib.MeasureTheory.Function.ConditionalExpectation.Basic

/-! P11: finer information improves the ideal squared-error predictor.

The predictors below are actual conditional expectations. Orthogonality is
derived from the conditional-expectation projection, rather than supplied as
an extra hypothesis. The result holds in every complete real Hilbert space,
so in particular in the manuscript's finite-dimensional setting.
-/
set_option autoImplicit false

open MeasureTheory
open scoped ENNReal MeasureTheory

namespace Komorebi.LSM.StatisticalRefinement

variable {Ω E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]
  {m₀ : MeasurableSpace Ω} {μ : Measure Ω}

/-- Expected squared error between two square-integrable random variables. -/
noncomputable def squaredRisk (Y Z : Lp E 2 μ) : ℝ :=
  ∫ ω, ‖Y ω - Z ω‖ ^ 2 ∂μ

theorem integral_sq_norm (Y : Lp E 2 μ) :
    (∫ ω, ‖Y ω‖ ^ 2 ∂μ) = ‖Y‖ ^ 2 := by
  rw [← real_inner_self_eq_norm_sq Y, L2.inner_def]
  simp_rw [real_inner_self_eq_norm_sq]

theorem squaredRisk_eq_norm_sq (Y Z : Lp E 2 μ) :
    squaredRisk Y Z = ‖Y - Z‖ ^ 2 := by
  rw [← integral_sq_norm (Y - Z)]
  apply integral_congr_ae
  filter_upwards [Lp.coeFn_sub Y Z] with ω hω
  exact congrArg (fun x : E => ‖x‖ ^ 2) hω.symm

variable [CompleteSpace E]

/-- Conditional-expectation residuals are orthogonal to every observable in
the conditioning information set. -/
theorem residual_orthogonal {m : MeasurableSpace Ω} (hm : m ≤ m₀)
    (Y Z : Lp E 2 μ) (hZ : AEStronglyMeasurable[m] Z μ) :
    inner ℝ (Y - (condExpL2 E ℝ hm Y : Lp E 2 μ)) Z = 0 := by
  rw [inner_sub_left, inner_condExpL2_eq_inner_fun hm Y Z hZ, sub_self]

/-- P11 in L2, with both predictors constructed by conditional expectation. -/
theorem conditional_expectation_pythagoras {mF mG : MeasurableSpace Ω}
    (hF : mF ≤ m₀) (hG : mG ≤ m₀) (hFG : mF ≤ mG) (Y : Lp E 2 μ) :
    squaredRisk Y (condExpL2 E ℝ hF Y : Lp E 2 μ) =
      squaredRisk Y (condExpL2 E ℝ hG Y : Lp E 2 μ) +
      squaredRisk (condExpL2 E ℝ hG Y : Lp E 2 μ)
        (condExpL2 E ℝ hF Y : Lp E 2 μ) := by
  let F : Lp E 2 μ := condExpL2 E ℝ hF Y
  let G : Lp E 2 μ := condExpL2 E ℝ hG Y
  have hFmeas : AEStronglyMeasurable[mG] F μ :=
    (aestronglyMeasurable_condExpL2 hF Y).mono hFG
  have hGmeas : AEStronglyMeasurable[mG] G μ :=
    aestronglyMeasurable_condExpL2 hG Y
  have hdiff : AEStronglyMeasurable[mG] (G - F) μ :=
    (hGmeas.sub hFmeas).congr (Lp.coeFn_sub G F).symm
  have horth : inner ℝ (Y - G) (G - F) = 0 :=
    residual_orthogonal hG Y (G - F) hdiff
  have hsplit : Y - F = (Y - G) + (G - F) := by abel
  simp only [squaredRisk_eq_norm_sq]
  change ‖Y - F‖ ^ 2 = ‖Y - G‖ ^ 2 + ‖G - F‖ ^ 2
  rw [hsplit]
  simpa only [pow_two] using
    norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero _ _ horth

/-- A finer sigma algebra cannot increase the ideal squared prediction risk. -/
theorem conditional_expectation_risk_mono {mF mG : MeasurableSpace Ω}
    (hF : mF ≤ m₀) (hG : mG ≤ m₀) (hFG : mF ≤ mG) (Y : Lp E 2 μ) :
    squaredRisk Y (condExpL2 E ℝ hG Y : Lp E 2 μ) ≤
      squaredRisk Y (condExpL2 E ℝ hF Y : Lp E 2 μ) := by
  rw [conditional_expectation_pythagoras hF hG hFG Y]
  exact le_add_of_nonneg_right (by rw [squaredRisk_eq_norm_sq]; positivity)

section FunctionRepresentatives

variable [IsFiniteMeasure μ]

/-- The L2 risk is the ordinary integral against the actual conditional
expectation of any square-integrable representative. -/
theorem squaredRisk_toLp_condExp {m : MeasurableSpace Ω} (hm : m ≤ m₀)
    {Y : Ω → E} (hY : MemLp Y 2 μ) :
    squaredRisk hY.toLp (condExpL2 E ℝ hm hY.toLp : Lp E 2 μ) =
      ∫ ω, ‖Y ω - μ[Y | m] ω‖ ^ 2 ∂μ := by
  unfold squaredRisk
  apply integral_congr_ae
  filter_upwards [hY.coeFn_toLp,
    hY.condExpL2_ae_eq_condExp (𝕜 := ℝ) hm] with ω hω hcond
  rw [hω, hcond]

theorem squaredRisk_condExp_difference {mF mG : MeasurableSpace Ω}
    (hF : mF ≤ m₀) (hG : mG ≤ m₀) {Y : Ω → E} (hY : MemLp Y 2 μ) :
    squaredRisk (condExpL2 E ℝ hG hY.toLp : Lp E 2 μ)
      (condExpL2 E ℝ hF hY.toLp : Lp E 2 μ) =
      ∫ ω, ‖μ[Y | mG] ω - μ[Y | mF] ω‖ ^ 2 ∂μ := by
  unfold squaredRisk
  apply integral_congr_ae
  filter_upwards [hY.condExpL2_ae_eq_condExp (𝕜 := ℝ) hF,
    hY.condExpL2_ae_eq_condExp (𝕜 := ℝ) hG] with ω hcondF hcondG
  rw [hcondF, hcondG]

/-- P11 exactly as an expected-squared-error identity for a
square-integrable Hilbert-valued random variable and nested information.
Probability measures are included among these finite measures. -/
theorem ideal_statistical_benefit {mF mG : MeasurableSpace Ω}
    (hF : mF ≤ m₀) (hG : mG ≤ m₀) (hFG : mF ≤ mG)
    {Y : Ω → E} (hY : MemLp Y 2 μ) :
    (∫ ω, ‖Y ω - μ[Y | mF] ω‖ ^ 2 ∂μ) =
      (∫ ω, ‖Y ω - μ[Y | mG] ω‖ ^ 2 ∂μ) +
      (∫ ω, ‖μ[Y | mG] ω - μ[Y | mF] ω‖ ^ 2 ∂μ) := by
  rw [← squaredRisk_toLp_condExp hF hY,
    ← squaredRisk_toLp_condExp hG hY, ← squaredRisk_condExp_difference hF hG hY]
  exact conditional_expectation_pythagoras hF hG hFG hY.toLp

theorem ideal_statistical_risk_mono {mF mG : MeasurableSpace Ω}
    (hF : mF ≤ m₀) (hG : mG ≤ m₀) (hFG : mF ≤ mG)
    {Y : Ω → E} (hY : MemLp Y 2 μ) :
    (∫ ω, ‖Y ω - μ[Y | mG] ω‖ ^ 2 ∂μ) ≤
      ∫ ω, ‖Y ω - μ[Y | mF] ω‖ ^ 2 ∂μ := by
  rw [ideal_statistical_benefit hF hG hFG hY]
  exact le_add_of_nonneg_right (integral_nonneg fun ω => sq_nonneg _)

/-- The manuscript's finite second-moment hypothesis, expressed as
integrability of the nonnegative squared norm, implies the same identity. -/
theorem ideal_statistical_benefit_of_integrable_sq_norm
    {mF mG : MeasurableSpace Ω} (hF : mF ≤ m₀) (hG : mG ≤ m₀)
    (hFG : mF ≤ mG) {Y : Ω → E} (hYmeas : AEStronglyMeasurable[m₀] Y μ)
    (hYsq : Integrable (fun ω => ‖Y ω‖ ^ 2) μ) :
    (∫ ω, ‖Y ω - μ[Y | mF] ω‖ ^ 2 ∂μ) =
      (∫ ω, ‖Y ω - μ[Y | mG] ω‖ ^ 2 ∂μ) +
      (∫ ω, ‖μ[Y | mG] ω - μ[Y | mF] ω‖ ^ 2 ∂μ) :=
  ideal_statistical_benefit hF hG hFG
    ((memLp_two_iff_integrable_sq_norm hYmeas).mpr hYsq)

end FunctionRepresentatives

end Komorebi.LSM.StatisticalRefinement
