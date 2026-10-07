import Mathlib.Data.Nat.Init
import Lean.Elab.Tactic.Omega

/-!
# Arithmetic spine for the prime-power correction graph

The branch indexed by `k` has visible defect cost `k * (h + 1)` and an
additional nonnegative binomial/carry cost.  This file isolates the elementary
precision bookkeeping used by the correction-state compiler.
-/

namespace KomorebiPadic

/-- Total precision cost of a correction branch. -/
def branchCost (h k carry : ℕ) : ℕ :=
  k * (h + 1) + carry

/-- A branch is active when its total cost is strictly below precision `r`. -/
def ActiveAt (r h k carry : ℕ) : Prop :=
  branchCost h k carry < r

/-- The valuation-only correction-order bound. -/
def coarseK (r h : ℕ) : ℕ :=
  (r - 1) / (h + 1)

/-- Every active branch satisfies the valuation-only inequality. -/
theorem activeAt_implies_visible_cost_lt
    {r h k carry : ℕ} (ha : ActiveAt r h k carry) :
    k * (h + 1) < r := by
  unfold ActiveAt branchCost at ha
  omega

/-- Every active branch has correction order at most `coarseK r h`. -/
theorem activeAt_implies_le_coarseK
    {r h k carry : ℕ} (ha : ActiveAt r h k carry) :
    k ≤ coarseK r h := by
  apply (Nat.le_div_iff_mul_le (by omega : 0 < h + 1)).2
  unfold ActiveAt branchCost at ha
  omega

/-- Every order below `coarseK` has visible cost below precision. -/
theorem visible_cost_lt_of_le_coarseK
    {r h k : ℕ} (hr : 0 < r) (hk : k ≤ coarseK r h) :
    k * (h + 1) < r := by
  have hmul : k * (h + 1) ≤ r - 1 :=
    (Nat.le_div_iff_mul_le (by omega : 0 < h + 1)).1 hk
  omega

/-- Adding a nonnegative carry cost can only delete branches. -/
theorem activeAt_mono_carry
    {r h k c₁ c₂ : ℕ} (hc : c₁ ≤ c₂)
    (ha : ActiveAt r h k c₂) :
    ActiveAt r h k c₁ := by
  unfold ActiveAt branchCost at *
  omega

/-- A zero-carry branch is active exactly when its visible cost fits. -/
theorem activeAt_zero_carry_iff {r h k : ℕ} :
    ActiveAt r h k 0 ↔ k * (h + 1) < r := by
  simp [ActiveAt, branchCost]

end KomorebiPadic
