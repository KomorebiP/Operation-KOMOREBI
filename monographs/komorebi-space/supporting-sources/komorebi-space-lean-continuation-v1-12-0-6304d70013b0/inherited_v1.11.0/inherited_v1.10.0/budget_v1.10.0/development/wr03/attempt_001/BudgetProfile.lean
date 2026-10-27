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

end KomorebiSpace.BudgetProfile
