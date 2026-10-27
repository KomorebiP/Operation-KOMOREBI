import AVOC.Core
import Mathlib.Algebra.Order.BigOperators.Group.Finset
import Mathlib.Basic.Real.Basic
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

/-- The finite unresolved-dependency debt used by the formal state model.
`weight` captures downstream centrality/harm and `uncertainty` the unresolved
amount. -/
def researchDebt {C : Type*} (unresolved : Finset C)
    (weight uncertainty : C → ℝ) : ℝ :=
  ∑ c ∈ unresolved, weight c * uncertainty c

/-- Shrinking the unresolved set cannot increase research debt when every
retained/removed debt contribution is nonnegative. -/
theorem researchDebt_nonincreasing_of_subset
    {C : Type*} [DecidableEq C]
    {smaller larger : Finset C} (weight uncertainty : C → ℝ)
    (hsub : smaller ⊆ larger)
    (hnonneg : ∀ c ∈ larger, 0 ≤ weight c * uncertainty c) :
    researchDebt smaller weight uncertainty ≤
      researchDebt larger weight uncertainty := by
  unfold researchDebt
  exact Finset.sum_le_sum_of_subset_of_nonneg hsub (by
    intro c hc _
    exact hnonneg c hc)

/-- Resolving a claim with strictly positive debt contribution strictly lowers
debt in the additive ledger model. -/
theorem resolving_positive_claim_strictly_lowers_debt
    {C : Type*} [DecidableEq C]
    (unresolved : Finset C) (weight uncertainty : C → ℝ) {c : C}
    (hc : c ∈ unresolved) (hpos : 0 < weight c * uncertainty c) :
    researchDebt (unresolved.erase c) weight uncertainty <
      researchDebt unresolved weight uncertainty := by
  have hsum := Finset.sum_erase_add unresolved
    (fun x => weight x * uncertainty x) hc
  unfold researchDebt
  linarith

/-- A compact claim-status alphabet.  It records epistemic state; the ordering
is evidence strength, not logical implication between claims. -/
inductive ClaimStatus where
  | proposal
  | formalized
  | computed
  | proved
  | replicated
  deriving DecidableEq, Repr

/-- Numeric evidence rank for monotone status checks. -/
def ClaimStatus.rank : ClaimStatus → ℕ
  | .proposal => 0
  | .formalized => 1
  | .computed => 2
  | .proved => 3
  | .replicated => 4

/-- `AtLeast s t` means status `s` carries at least the declared evidence rank
of threshold `t`. -/
def ClaimStatus.AtLeast (s threshold : ClaimStatus) : Prop :=
  threshold.rank ≤ s.rank

/-- Evidence thresholds compose transitively. -/
theorem ClaimStatus.atLeast_trans {a b c : ClaimStatus}
    (hab : a.AtLeast b) (hbc : b.AtLeast c) : a.AtLeast c := by
  exact Nat.le_trans hbc hab

end Komorebi.AVOC
