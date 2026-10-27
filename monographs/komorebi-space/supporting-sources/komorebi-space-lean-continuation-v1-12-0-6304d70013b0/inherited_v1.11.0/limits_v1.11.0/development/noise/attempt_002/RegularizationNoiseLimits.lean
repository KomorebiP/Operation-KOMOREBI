import KomorebiSpace.RegularizationLimits
import Mathlib.Analysis.Normed.Group.Continuity

set_option autoImplicit false

/-!
# Noisy data and inexact stopping limits

The data and solver errors are measured for one fixed bounded linear operator
between the declared real Hilbert spaces. Parameter choices are limits along
arbitrary filters; in particular, they include a full positive real family.
-/

noncomputable section
universe u v w
namespace KomorebiSpace.RegularizationNoiseLimits
open Filter
open scoped Topology RealInnerProductSpace
open RegularizedHilbertRepair
open RegularizationLimits

/-- The one-dimensional operator attaining the universal correction-noise gain. -/
def scalarSharpOperator (α : ℝ) : ℝ →L[ℝ] ℝ :=
  Real.sqrt α • ContinuousLinearMap.id ℝ ℝ

theorem scalarSharpOperator_adjoint (α : ℝ) :
    (scalarSharpOperator α).adjoint = scalarSharpOperator α := by
  symm
  apply (ContinuousLinearMap.eq_adjoint_iff _ _).2
  intro x y
  simp [scalarSharpOperator, real_inner_comm, mul_comm, mul_left_comm]

/-- Sharpness holds at every positive parameter and for every scalar datum. -/
theorem scalar_correction_formula (α : ℝ) (hα : 0 < α) (r : ℝ) :
    correction (scalarSharpOperator α) α hα r = r / (2 * Real.sqrt α) := by
  symm
  apply normal_unique
  rw [normal_apply, scalarSharpOperator_adjoint]
  simp only [scalarSharpOperator, smul_apply,
    ContinuousLinearMap.id_apply, smul_eq_mul]
  have hs : Real.sqrt α ≠ 0 := ne_of_gt (Real.sqrt_pos.mpr hα)
  have hsq := Real.sq_sqrt hα.le
  field_simp
  rw [hsq]
  ring

theorem data_noise_coefficient_attained (α : ℝ) (hα : 0 < α) (r s : ℝ) :
    ‖correction (scalarSharpOperator α) α hα r -
      correction (scalarSharpOperator α) α hα s‖ = ‖r-s‖ / (2 * Real.sqrt α) := by
  rw [scalar_correction_formula, scalar_correction_formula, ← sub_div, norm_div]
  rw [Real.norm_of_nonneg (by positivity : 0 ≤ 2 * Real.sqrt α)]

variable {H : Type u} {Y : Type v}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]
variable (T : H →L[ℝ] Y)

/-- The stipulated data-error budget gives the sharp correction bound. -/
theorem noise_path_bound (r s : Y) {α δ : ℝ} (hα : 0 < α)
    (hdata : ‖s-r‖ ≤ δ) :
    ‖path T s α - path T r α‖ ≤ δ / (2 * Real.sqrt α) := by
  rw [path_of_pos T s hα, path_of_pos T r hα]
  exact (data_noise_bound T α hα s r).trans
    (div_le_div_of_nonneg_right hdata (by positivity))

/-- The fitted-data response has gain at most one. -/
theorem noise_fitted_path_bound (r s : Y) {α δ : ℝ} (hα : 0 < α)
    (hdata : ‖s-r‖ ≤ δ) :
    ‖T (path T s α - path T r α)‖ ≤ δ := by
  rw [path_of_pos T s hα, path_of_pos T r hα]
  exact (data_fitted_bound T α hα s r).trans hdata

/-- The two budgets apply to the measured problem and to the same fixed operator. -/
theorem solver_data_path_bound (r s : Y) (a : H) {α δ ε : ℝ} (hα : 0 < α)
    (hdata : ‖s-r‖ ≤ δ) (hsolver : ‖gradient T α s a‖ ≤ ε) :
    ‖a-path T r α‖ ≤ ε/α + δ/(2*Real.sqrt α) := by
  rw [path_of_pos T r hα]
  exact (solver_and_data_bound T α hα r s a).trans
    (add_le_add (div_le_div_of_nonneg_right hsolver hα.le)
      (div_le_div_of_nonneg_right hdata (by positivity)))

/-- The pointwise stopping certificate separates solver error, noise, and bias. -/
theorem stopping_three_term_bound (r s : Y) (a aMin : H) {α δ ε : ℝ} (hα : 0 < α)
    (hdata : ‖s-r‖ ≤ δ) (hsolver : ‖gradient T α s a‖ ≤ ε) :
    ‖a-aMin‖ ≤ ε/α + δ/(2*Real.sqrt α) + ‖path T r α-aMin‖ := by
  exact (norm_sub_le a (path T r α) aMin).trans
    (add_le_add_right (solver_data_path_bound T r s a hα hdata hsolver) _)

variable {I : Type w} {l : Filter I}

theorem noise_half_ratio_tendsto {α δ : I → ℝ}
    (hnoise : Tendsto (fun i => δ i / Real.sqrt (α i)) l (𝓝 0)) :
    Tendsto (fun i => δ i / (2 * Real.sqrt (α i))) l (𝓝 0) := by
  have he : (fun i => δ i / (2 * Real.sqrt (α i))) =
      (fun i => (δ i / Real.sqrt (α i)) / 2) := by
    funext i
    ring
  rw [he]
  simpa only [zero_div] using hnoise.div_const 2

/-- Vanishing propagated data error transfers an exact-data strong limit. -/
theorem noisy_tendsto_of_exact_tendsto (r : Y) (s : I → Y) (aMin : H)
    (α δ : I → ℝ) (hα : ∀ᶠ i in l, 0 < α i)
    (hdata : ∀ᶠ i in l, ‖s i-r‖ ≤ δ i)
    (hnoise : Tendsto (fun i => δ i / Real.sqrt (α i)) l (𝓝 0))
    (hbias : Tendsto (fun i => path T r (α i)) l (𝓝 aMin)) :
    Tendsto (fun i => path T (s i) (α i)) l (𝓝 aMin) := by
  have hbound : ∀ᶠ i in l, ‖path T (s i) (α i)-path T r (α i)‖ ≤
      δ i / (2*Real.sqrt (α i)) := by
    filter_upwards [hα, hdata] with i hi hd
    exact noise_path_bound T r (s i) hi hd
  have hdiff := squeeze_zero_norm' hbound (noise_half_ratio_tendsto hnoise)
  simpa only [sub_add_cancel, zero_add] using hdiff.add hbias

/-- Solver residuals and data errors may vary independently along any filter. -/
theorem inexact_tendsto_of_exact_tendsto (r : Y) (s : I → Y) (a : I → H) (aMin : H)
    (α δ ε : I → ℝ) (hα : ∀ᶠ i in l, 0 < α i)
    (hdata : ∀ᶠ i in l, ‖s i-r‖ ≤ δ i)
    (hsolver : ∀ᶠ i in l, ‖gradient T (α i) (s i) (a i)‖ ≤ ε i)
    (hnoise : Tendsto (fun i => δ i / Real.sqrt (α i)) l (𝓝 0))
    (hsolve : Tendsto (fun i => ε i / α i) l (𝓝 0))
    (hbias : Tendsto (fun i => path T r (α i)) l (𝓝 aMin)) :
    Tendsto a l (𝓝 aMin) := by
  have hbound : ∀ᶠ i in l, ‖a i-path T r (α i)‖ ≤
      ε i/α i + δ i/(2*Real.sqrt (α i)) := by
    filter_upwards [hα, hdata, hsolver] with i hi hd hs
    exact solver_data_path_bound T r (s i) (a i) hi hd hs
  have hsum : Tendsto (fun i => ε i/α i + δ i/(2*Real.sqrt (α i))) l (𝓝 0) := by
    simpa only [zero_add] using hsolve.add (noise_half_ratio_tendsto hnoise)
  have hdiff := squeeze_zero_norm' hbound hsum
  simpa only [sub_add_cancel, zero_add] using hdiff.add hbias

end KomorebiSpace.RegularizationNoiseLimits
