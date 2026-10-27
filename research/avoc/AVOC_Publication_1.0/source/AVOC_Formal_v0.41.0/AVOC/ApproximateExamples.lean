import AVOC.ApproximateComposition
import Mathlib.Data.Fintype.Basic

namespace Komorebi.AVOC

/-- One-step distortion budget is exactly the immediate reward error. -/
theorem approxBudget_one (ε δ R : ℚ) :
    approxBudget ε δ R 1 = ε := by
  simp [approxBudget]

/-- Two-step distortion exposes the first transition-error term. -/
theorem approxBudget_two (ε δ R : ℚ) :
    approxBudget ε δ R 2 = 2 * ε + δ * R := by
  simp [approxBudget]
  ring

/-- With exact projected transitions, the budget is purely linear in reward error. -/
theorem approxBudget_reward_only (ε R : ℚ) (n : ℕ) :
    approxBudget ε 0 R n = (n : ℚ) * ε := by
  rw [approxBudget_closed_form]
  ring

/-- With exact rewards, only the triangular transition term remains. -/
theorem approxBudget_transition_only (δ R : ℚ) (n : ℕ) :
    approxBudget 0 δ R n = δ * R * ((n : ℚ) * ((n : ℚ) - 1) / 2) := by
  rw [approxBudget_closed_form]
  ring

/-- Zero distortion recovers zero value-loss budget at every horizon. -/
theorem approxBudget_zero (R : ℚ) (n : ℕ) :
    approxBudget 0 0 R n = 0 := by
  rw [approxBudget_closed_form]
  ring

/-- Opposite point masses on Bool. -/
def tightP : Bool → ℚ := fun b => if b then 1 else 0
/-- Opposite point mass. -/
def tightQ : Bool → ℚ := fun b => if b then 0 else 1
/-- Extremal bounded test taking values `±1`. -/
def tightV : Bool → ℚ := fun b => if b then 1 else -1

/-- The finite L1 row distance of the opposite point masses is exactly `2`. -/
theorem tight_l1_distance : l1RowDistance tightP tightQ = 2 := by
  unfold l1RowDistance
  rw [Fintype.sum_bool]
  norm_num [tightP, tightQ]

/-- The L1 expectation inequality is sharp at bound `B=1` on the Bool example. -/
theorem tight_weighted_sum_difference :
    |(∑ b : Bool, tightP b * tightV b) -
      ∑ b : Bool, tightQ b * tightV b| = 2 := by
  rw [Fintype.sum_bool, Fintype.sum_bool]
  norm_num [tightP, tightQ, tightV]

end Komorebi.AVOC
