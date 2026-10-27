import KomorebiSpace.RegularizedHilbertRepair
import KomorebiSpace.BudgetProfile

/-!
# The small-parameter regularization limits (WR08)

The limit is over all positive real parameters approaching zero. The projected
datum belongs to the closure of the operator range; no closed-range assumption
is made. Unattained projected data force divergence of the correction norms.
-/

noncomputable section

open Filter Set Metric
open scoped Topology

namespace KomorebiSpace.RegularizationLimits

open BudgetProfile

variable {H Y : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- A total parameter path, using the established regularized correction at every
positive parameter. Its values elsewhere do not affect the right-hand limit. -/
def path (T : H →L[ℝ] Y) (r : Y) (α : ℝ) : H :=
  if h : 0 < α then RegularizedHilbertRepair.correction T α h r else 0

theorem path_of_pos (T : H →L[ℝ] Y) (r : Y) {α : ℝ} (hα : 0 < α) :
    path T r α = RegularizedHilbertRepair.correction T α hα r := by
  simp only [path, dite_eq_left hα]

theorem eventual_pos : ∀ᶠ α : ℝ in 𝓝[>] 0, 0 < α :=
  self_mem_nhdsWithin

/-- Canceling the orthogonal residual floor in the global objective comparison. -/
theorem objective_comparison (T : H →L[ℝ] Y) (r : Y) {α : ℝ}
    (hα : 0 < α) (a : H) :
    ‖projectedDatum T r - T (path T r α)‖ ^ 2 + α * ‖path T r α‖ ^ 2 ≤
      ‖projectedDatum T r - T a‖ ^ 2 + α * ‖a‖ ^ 2 := by
  rw [path_of_pos T r hα]
  have hb := RegularizedHilbertRepair.correction_best T α hα r a
  unfold RegularizedHilbertRepair.objective at hb
  rw [norm_sub_rev (T (RegularizedHilbertRepair.correction T α hα r)) r,
    norm_sub_rev (T a) r, residual_sq_decomposition T r,
    residual_sq_decomposition T r] at hb
  linarith

/-- The projected fitting error and weighted correction penalty vanish together. -/
theorem projected_energy_tendsto_zero (T : H →L[ℝ] Y) (r : Y) :
    Tendsto (fun α : ℝ =>
      ‖projectedDatum T r - T (path T r α)‖ ^ 2 + α * ‖path T r α‖ ^ 2)
      (𝓝[>] 0) (𝓝 0) := by
  apply Metric.tendsto_nhds.mpr
  intro ε hε
  have hhalf : 0 < ε / 2 := by linarith
  have hclosure : projectedDatum T r ∈ closure (Set.range T) :=
    projectedDatum_mem T r
  obtain ⟨_, ⟨a, rfl⟩, ha⟩ :=
    Metric.mem_closure_iff.mp hclosure (Real.sqrt (ε / 2)) (Real.sqrt_pos.mpr hhalf)
  rw [dist_eq_norm] at ha
  have hsq : ‖projectedDatum T r - T a‖ ^ 2 < ε / 2 := by
    nlinarith [Real.sq_sqrt hhalf.le, norm_nonneg (projectedDatum T r - T a),
      Real.sqrt_nonneg (ε / 2)]
  have hm : Tendsto (fun α : ℝ => α * ‖a‖ ^ 2) (𝓝[>] 0) (𝓝 0) := by
    simpa only [zero_mul] using
      (tendsto_nhdsWithin_of_tendsto_nhds
        (tendsto_id : Tendsto (fun α : ℝ => α) (𝓝 0) (𝓝 0))).mul_const (‖a‖ ^ 2)
  filter_upwards [eventual_pos, (tendsto_order.mp hm).2 (ε / 2) hhalf] with α hα hsmall
  have hlo : 0 ≤ ‖projectedDatum T r - T (path T r α)‖ ^ 2 +
      α * ‖path T r α‖ ^ 2 :=
    add_nonneg (sq_nonneg _) (mul_nonneg hα.le (sq_nonneg _))
  rw [Real.dist_eq, sub_zero, abs_of_nonneg hlo]
  have hcomp := objective_comparison T r hα a
  linarith

theorem projected_error_sq_tendsto_zero (T : H →L[ℝ] Y) (r : Y) :
    Tendsto (fun α : ℝ => ‖projectedDatum T r - T (path T r α)‖ ^ 2)
      (𝓝[>] 0) (𝓝 0) := by
  apply squeeze_zero' (Filter.Eventually.of_forall fun _ => sq_nonneg _)
    ?_ (projected_energy_tendsto_zero T r)
  filter_upwards [eventual_pos] with α hα
  exact le_add_of_nonneg_right (mul_nonneg hα.le (sq_nonneg _))

/-- The full positive-parameter family converges to the range-closure projection. -/
theorem fitted_tendsto_projectedDatum (T : H →L[ℝ] Y) (r : Y) :
    Tendsto (fun α : ℝ => T (path T r α)) (𝓝[>] 0) (𝓝 (projectedDatum T r)) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  have h := (projected_error_sq_tendsto_zero T r).sqrt
  simpa only [Real.sqrt_sq (norm_nonneg _), Real.sqrt_zero, norm_sub_rev] using h

/-- The residual norm tends to the unavoidable orthogonal residual floor. -/
theorem residual_norm_tendsto_floor (T : H →L[ℝ] Y) (r : Y) :
    Tendsto (fun α : ℝ => ‖r - T (path T r α)‖) (𝓝[>] 0)
      (𝓝 ‖r - projectedDatum T r‖) :=
  (tendsto_const_nhds.sub (fitted_tendsto_projectedDatum T r)).norm

/-- Vanishing weighted penalty does not assert bounded correction norms. -/
theorem weighted_penalty_tendsto_zero (T : H →L[ℝ] Y) (r : Y) :
    Tendsto (fun α : ℝ => α * ‖path T r α‖ ^ 2) (𝓝[>] 0) (𝓝 0) := by
  apply squeeze_zero' ?_ (Filter.Eventually.of_forall fun _ => le_add_of_nonneg_left
    (sq_nonneg _)) (projected_energy_tendsto_zero T r)
  filter_upwards [eventual_pos] with α hα
  exact mul_nonneg hα.le (sq_nonneg _)

/-- If the projected datum is unattained, the norms escape every finite budget
along the whole right-hand parameter filter, not merely along a sequence. -/
theorem norm_tendsto_atTop_of_not_mem_range (T : H →L[ℝ] Y) (r : Y)
    (hr : projectedDatum T r ∉ Set.range T) :
    Tendsto (fun α : ℝ => ‖path T r α‖) (𝓝[>] 0) atTop := by
  apply Filter.tendsto_atTop.mpr
  intro M
  by_contra h
  have hfreq : ∃ᶠ α : ℝ in 𝓝[>] 0, ‖path T r α‖ ≤ M :=
    (Filter.not_eventually.mp h).mono fun _ hn => (lt_of_not_ge hn).le
  obtain ⟨a, ha, _⟩ := BoundedApproximateRealization.exists_solution_of_frequently_bounded
    T (path T r) (projectedDatum T r) M hfreq (fitted_tendsto_projectedDatum T r)
  exact hr ⟨a, ha⟩

end KomorebiSpace.RegularizationLimits
