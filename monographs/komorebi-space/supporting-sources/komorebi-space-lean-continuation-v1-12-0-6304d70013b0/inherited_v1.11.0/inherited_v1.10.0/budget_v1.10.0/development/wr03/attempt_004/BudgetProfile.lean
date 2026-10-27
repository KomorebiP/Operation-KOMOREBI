import KomorebiSpace.BoundedApproximateRealization
import Mathlib.Analysis.InnerProductSpace.Projection.Basic
import Mathlib.Analysis.InnerProductSpace.Projection.Minimal
import Mathlib.Analysis.Convex.Function
import Mathlib.Topology.MetricSpace.HausdorffDistance
import Mathlib.Topology.Sequences
import Mathlib.Tactic

/-!
# The attained residual at a fixed correction budget (WR03)

The fixed-budget image is closed without a closed-range assumption, by the
accepted same-budget realization theorem. Hilbert projection then gives the
minimum at every nonnegative budget, including zero.
-/

noncomputable section

open Filter Set Metric
open scoped Topology

namespace KomorebiSpace.BudgetProfile

variable {H Y : Type*}
variable [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]
variable [NormedAddCommGroup Y] [InnerProductSpace ℝ Y] [CompleteSpace Y]

/-- The residual distance to the image of the actual correction ball. -/
def beta (T : H →L[ℝ] Y) (r : Y) (M : ℝ) : ℝ :=
  Metric.infDist r (T '' Metric.closedBall 0 M)

omit [CompleteSpace H] [CompleteSpace Y] in
theorem convex_budget_image (T : H →L[ℝ] Y) (M : ℝ) :
    Convex ℝ (T '' Metric.closedBall 0 M) :=
  (convex_closedBall (0 : H) M).linear_image T.toLinearMap

/-- Closedness of each budget image does not assert closedness of the whole range. -/
theorem isClosed_budget_image (T : H →L[ℝ] Y) (M : ℝ) :
    IsClosed (T '' Metric.closedBall 0 M) := by
  apply IsSeqClosed.isClosed
  intro u y hu hlim
  choose a ha using hu
  have hb : ∀ n, ‖a n‖ ≤ M := by
    intro n
    simpa only [Metric.mem_closedBall, dist_zero_right] using (ha n).1
  have hT : Tendsto (fun n => T (a n)) atTop (𝓝 y) := by
    simpa only [(ha _).2] using hlim
  obtain ⟨x, hx, hnorm⟩ :=
    BoundedApproximateRealization.exists_solution_of_bounded_approximation T a y M hb hT
  exact ⟨x, by simpa only [Metric.mem_closedBall, dist_zero_right] using hnorm, hx⟩

omit [CompleteSpace H] [CompleteSpace Y] in
theorem budget_image_nonempty (T : H →L[ℝ] Y) {M : ℝ} (hM : 0 ≤ M) :
    (T '' Metric.closedBall 0 M).Nonempty :=
  ⟨T 0, 0, by simpa using hM, rfl⟩

omit [CompleteSpace H] [CompleteSpace Y] in
theorem beta_nonneg (T : H →L[ℝ] Y) (r : Y) (M : ℝ) : 0 ≤ beta T r M :=
  Metric.infDist_nonneg

omit [CompleteSpace H] [CompleteSpace Y] in
theorem beta_le_residual (T : H →L[ℝ] Y) (r : Y) {M : ℝ} {a : H}
    (ha : ‖a‖ ≤ M) : beta T r M ≤ ‖r - T a‖ := by
  exact (Metric.infDist_le_dist_of_mem
    (show T a ∈ T '' Metric.closedBall 0 M from
      ⟨a, by simpa only [Metric.mem_closedBall, dist_zero_right] using ha, rfl⟩)).trans_eq
    (dist_eq_norm _ _)

/-- Every nonnegative budget has an attaining correction, with the same budget. -/
theorem exists_budget_minimizer (T : H →L[ℝ] Y) (r : Y) {M : ℝ}
    (hM : 0 ≤ M) : ∃ a : H, ‖a‖ ≤ M ∧ ‖r - T a‖ = beta T r M := by
  obtain ⟨y, ⟨a, ha, rfl⟩, hy⟩ := exists_norm_eq_iInf_of_complete_convex
    (budget_image_nonempty T hM) (isClosed_budget_image T M).isComplete
    (convex_budget_image T M) r
  refine ⟨a, by simpa only [Metric.mem_closedBall, dist_zero_right] using ha, ?_⟩
  simpa only [beta, Metric.infDist_eq_iInf, dist_eq_norm] using hy

/-- The subspace determining the unrestricted residual floor. -/
def rangeClosure (T : H →L[ℝ] Y) : Submodule ℝ Y :=
  T.range.topologicalClosure

omit [CompleteSpace H] [CompleteSpace Y] in
theorem rangeClosure_coe (T : H →L[ℝ] Y) :
    (rangeClosure T : Set Y) = closure (Set.range T) := rfl

instance rangeClosure_completeSpace (T : H →L[ℝ] Y) : CompleteSpace (rangeClosure T) :=
  (T.range.isClosed_topologicalClosure).completeSpace_coe

/-- Projection onto the closure of the range, not onto an assumed closed range. -/
def projectedDatum (T : H →L[ℝ] Y) (r : Y) : Y :=
  (rangeClosure T).starProjection r

omit [CompleteSpace H] in
theorem projectedDatum_mem (T : H →L[ℝ] Y) (r : Y) :
    projectedDatum T r ∈ rangeClosure T :=
  (rangeClosure T).starProjection_apply_mem r

omit [CompleteSpace H] [CompleteSpace Y] in
theorem apply_mem_rangeClosure (T : H →L[ℝ] Y) (a : H) :
    T a ∈ rangeClosure T :=
  subset_closure (Set.mem_range_self a)

omit [CompleteSpace H] in
theorem residual_sq_decomposition (T : H →L[ℝ] Y) (r : Y) (a : H) :
    ‖r - T a‖ ^ 2 = ‖r - projectedDatum T r‖ ^ 2 +
      ‖projectedDatum T r - T a‖ ^ 2 := by
  have horth : inner ℝ (r - projectedDatum T r) (projectedDatum T r - T a) = 0 :=
    (rangeClosure T).starProjection_inner_eq_zero r _
      ((rangeClosure T).sub_mem (projectedDatum_mem T r) (apply_mem_rangeClosure T a))
  have he := norm_add_sq_real (r - projectedDatum T r) (projectedDatum T r - T a)
  rw [sub_add_sub_cancel, horth] at he
  linarith

omit [CompleteSpace H] in
theorem projected_residual_eq_infDist (T : H →L[ℝ] Y) (r : Y) :
    ‖r - projectedDatum T r‖ = Metric.infDist r (closure (Set.range T)) := by
  rw [← rangeClosure_coe, Metric.infDist_eq_iInf]
  simpa only [projectedDatum, dist_eq_norm] using
    (Submodule.starProjection_minimal (U := rangeClosure T) r)

omit [CompleteSpace H] in
theorem floor_le_beta (T : H →L[ℝ] Y) (r : Y) {M : ℝ} (hM : 0 ≤ M) :
    ‖r - projectedDatum T r‖ ≤ beta T r M := by
  rw [projected_residual_eq_infDist]
  exact Metric.infDist_le_infDist_of_subset
    (by rintro _ ⟨a, _, rfl⟩; exact subset_closure (Set.mem_range_self a))
    (budget_image_nonempty T hM)

/-- The residual floor is reached at a finite budget exactly when the projected
datum is attained within that same budget. -/
theorem beta_eq_floor_iff (T : H →L[ℝ] Y) (r : Y) {M : ℝ} (hM : 0 ≤ M) :
    beta T r M = ‖r - projectedDatum T r‖ ↔
      ∃ a : H, T a = projectedDatum T r ∧ ‖a‖ ≤ M := by
  constructor
  · intro h
    obtain ⟨a, ha, he⟩ := exists_budget_minimizer T r hM
    have hsq := residual_sq_decomposition T r a
    rw [he, h] at hsq
    have hz : ‖projectedDatum T r - T a‖ = 0 := by nlinarith [norm_nonneg (projectedDatum T r - T a)]
    exact ⟨a, (sub_eq_zero.mp (norm_eq_zero.mp hz)).symm, ha⟩
  · rintro ⟨a, ha, hnorm⟩
    apply le_antisymm _ (floor_le_beta T r hM)
    simpa only [ha] using beta_le_residual T r hnorm

/-- Zero residual at a fixed budget is exact feasibility, even for nonclosed range. -/
theorem beta_eq_zero_iff (T : H →L[ℝ] Y) (r : Y) {M : ℝ} (hM : 0 ≤ M) :
    beta T r M = 0 ↔ ∃ a : H, T a = r ∧ ‖a‖ ≤ M := by
  constructor
  · intro h
    obtain ⟨a, ha, he⟩ := exists_budget_minimizer T r hM
    exact ⟨a, (sub_eq_zero.mp (norm_eq_zero.mp (he.trans h))).symm, ha⟩
  · rintro ⟨a, ha, hnorm⟩
    apply le_antisymm _ (beta_nonneg T r M)
    simpa only [ha, sub_self, norm_zero] using beta_le_residual T r hnorm

omit [CompleteSpace H] in
/-- As real budgets tend to infinity, the profile tends to distance from the
closure of the range. No closed-range assumption is used. -/
theorem beta_tendsto_infDist (T : H →L[ℝ] Y) (r : Y) :
    Tendsto (beta T r) atTop (𝓝 (Metric.infDist r (closure (Set.range T)))) := by
  apply Metric.tendsto_nhds.mpr
  intro ε hε
  have hlt : Metric.infDist r (Set.range T) <
      Metric.infDist r (closure (Set.range T)) + ε := by
    rw [Metric.infDist_closure]
    exact lt_add_of_pos_right _ hε
  obtain ⟨_, ⟨a, rfl⟩, ha⟩ :=
    (Metric.infDist_lt_iff (Set.range_nonempty T)).mp hlt
  filter_upwards [Filter.eventually_ge_atTop ‖a‖] with M hM
  have hl : Metric.infDist r (closure (Set.range T)) ≤ beta T r M := by
    rw [← projected_residual_eq_infDist]
    exact floor_le_beta T r ((norm_nonneg a).trans hM)
  have hu := beta_le_residual T r hM
  rw [dist_eq_norm] at ha
  rw [Real.dist_eq, abs_of_nonneg (sub_nonneg.mpr hl)]
  linarith

omit [CompleteSpace H] in
theorem beta_tendsto_floor (T : H →L[ℝ] Y) (r : Y) :
    Tendsto (beta T r) atTop (𝓝 ‖r - projectedDatum T r‖) := by
  rw [projected_residual_eq_infDist]
  exact beta_tendsto_infDist T r

end KomorebiSpace.BudgetProfile
