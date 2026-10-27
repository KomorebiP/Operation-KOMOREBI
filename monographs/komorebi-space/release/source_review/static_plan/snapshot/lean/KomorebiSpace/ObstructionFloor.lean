import Mathlib.Topology.MetricSpace.HausdorffDistance
import Mathlib.Analysis.Normed.Group.Basic
import Mathlib.Algebra.Group.Subgroup.Basic
import Mathlib.Tactic.Linarith

set_option autoImplicit false

/-!
# The irreducible residual floor

Distance zero means membership in the closure of admissible boundaries. Actual
flattening follows only if this boundary subgroup is closed.
-/
universe u
namespace KomorebiSpace
namespace ObstructionFloor
open Filter
open scoped Topology
variable {R : Type u} [NormedAddCommGroup R]

noncomputable def floor (B : AddSubgroup R) (ω : R) : ℝ := Metric.infDist ω (B : Set R)

theorem nonnegative (B : AddSubgroup R) (ω : R) : 0 ≤ floor B ω := Metric.infDist_nonneg

theorem lower_bound (B : AddSubgroup R) (ω a : R) (ha : a ∈ B) :
    floor B ω ≤ ‖ω-a‖ := by
  simpa only [floor, dist_eq_norm] using (Metric.infDist_le_dist_of_mem (x := ω) ha)

theorem zero_iff_closure (B : AddSubgroup R) (ω : R) :
    floor B ω = 0 ↔ ω ∈ closure (B : Set R) :=
  (Metric.mem_closure_iff_infDist_zero (s := (B : Set R)) ⟨0, B.zero_mem⟩).symm

theorem zero_iff_mem_of_closed (B : AddSubgroup R) (hB : IsClosed (B : Set R)) (ω : R) :
    floor B ω = 0 ↔ ω ∈ B := by
  rw [zero_iff_closure, hB.closure_eq]
  rfl

/-- Every sequence of admissible corrections is blocked by a persistent positive floor. -/
theorem persistent_obstruction (B : ℕ → AddSubgroup R) (Ω a : ℕ → R)
    (ha : ∀ n, a n ∈ B n) (c : ℝ) (hc : 0 < c)
    (hfloor : ∀ᶠ n in atTop, c ≤ floor (B n) (Ω n)) :
    ¬ Tendsto (fun n => ‖Ω n-a n‖) atTop (𝓝 0) := by
  intro hv
  have hle : c ≤ 0 := ge_of_tendsto hv
    (hfloor.mono fun n hn => hn.trans (lower_bound (B n) (Ω n) (a n) (ha n)))
  linarith

end ObstructionFloor
end KomorebiSpace
