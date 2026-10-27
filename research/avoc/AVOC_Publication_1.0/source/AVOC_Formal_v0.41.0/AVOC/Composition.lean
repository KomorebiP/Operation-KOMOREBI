import AVOC.Core
import Mathlib.Algebra.Order.BigOperators.Group.Finset

namespace Komorebi.AVOC

/-- Finite local-composition cost bound.  If every local node costs at most
`bound`, total local cost is at most number-of-nodes times `bound`. -/
theorem local_decomposition_cost_bound
    {ι : Type*} (nodes : Finset ι) (cost : ι → ℕ) (bound : ℕ)
    (h : ∀ i ∈ nodes, cost i ≤ bound) :
    (∑ i ∈ nodes, cost i) ≤ nodes.card * bound := by
  simpa [Nat.nsmul_eq_mul] using Finset.sum_le_card_nsmul nodes cost bound h

/-- A direct finite version of the local proof-DAG bound.  If a node explores
at most `candidateBound` candidates, each candidate costs at most `verifyCost`,
and local composition adds at most `composeCost`, then the total cost over the
finite node set is bounded by the declared per-node envelope. -/
theorem local_search_cost_bound
    {ι : Type*} (nodes : Finset ι) (nodeCost : ι → ℕ)
    (candidateBound verifyCost composeCost : ℕ)
    (h : ∀ i ∈ nodes,
      nodeCost i ≤ candidateBound * verifyCost + composeCost) :
    (∑ i ∈ nodes, nodeCost i) ≤
      nodes.card * (candidateBound * verifyCost + composeCost) := by
  exact local_decomposition_cost_bound nodes nodeCost
    (candidateBound * verifyCost + composeCost) h

/-- Reusing an already verified local node can only reduce the additive cost
model when its replacement cost is no larger than its original cost. -/
theorem local_reuse_nonincreasing
    {ι : Type*} [DecidableEq ι]
    (nodes : Finset ι) (oldCost newCost : ι → ℕ)
    (h : ∀ i ∈ nodes, newCost i ≤ oldCost i) :
    (∑ i ∈ nodes, newCost i) ≤ ∑ i ∈ nodes, oldCost i := by
  exact Finset.sum_le_sum h

end Komorebi.AVOC
