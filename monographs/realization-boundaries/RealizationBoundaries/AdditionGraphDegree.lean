import RealizationBoundaries.CanonicalOperationDegree

/-! # Total function graph oracles and exact operation degrees -/
set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace RealizationBoundaries

/-- The ordinary membership oracle for the graph of a total natural function. -/
def operationGraphOracle (op : ℕ → ℕ) (k : ℕ) : Bool :=
  decide (op k.unpair.1 = k.unpair.2)

/-- A total function is computed from its graph by a terminating positive
search for the unique output. -/
theorem operationGraph_computes_function (op : ℕ → ℕ) :
    OracleComputable (operationGraphOracle op) op := by
  let test : ℕ → ℕ := fun k => if op k.unpair.1 = k.unpair.2 then 0 else 1
  have ht : OracleComputable (operationGraphOracle op) test := by
    exact (OracleComputable.oracle.isZero).of_eq (fun k => by
      by_cases h : op k.unpair.1 = k.unpair.2 <;> simp [test, operationGraphOracle, h])
  have total : ∀ n, ∃ t, test (Nat.pair n t) = 0 := by
    intro n
    exact ⟨op n, by simp [test]⟩
  apply (OracleComputable.find ht total).of_eq
  intro n
  have hh := Nat.find_spec (total n)
  have he : op n = Nat.find (total n) := by simpa [test] using hh
  exact he.symm

/-- Computing a function computes its graph by a finite equality test. -/
theorem operationGraph_reduces_of_computable (op : ℕ → ℕ) (X : ℕ → Bool)
    (hop : OracleComputable X op) : SelectorReducible (operationGraphOracle op) X := by
  apply RecursiveIn.iff_nat.mpr
  have hh := (hop.comp OracleComputable.left).ncEq OracleComputable.right
  exact hh.of_eq (fun k => by simp [operationGraphOracle])

/-- The graph and operation conventions define the same relative total
computability contract. -/
theorem operationGraph_reducible_iff (op : ℕ → ℕ) (X : ℕ → Bool) :
    SelectorReducible (operationGraphOracle op) X ↔ OracleComputable X op := by
  constructor
  · intro h
    exact (operationGraph_computes_function op).change_oracle h
  · exact operationGraph_reduces_of_computable op X

/-- The graph of the fixed canonical addition operation has exactly the selector
oracle's Turing degree, in the official native relation. -/
theorem canonicalPairedAddition_graph_equivalent (a : ℕ → Bool) :
    TuringEquivalent (selectorOracle (operationGraphOracle (canonicalPairedAddition a)))
      (selectorOracle a) := by
  constructor
  · exact operationGraph_reduces_of_computable _ a
      ((canonicalPairedAddition_oracle_iff a a).mpr (TuringReducible.refl _))
  · exact (canonicalPairedAddition_oracle_iff a _).mp
      (operationGraph_computes_function _)

/-- Equivalently, the operation graph is computable in exactly the oracles that
compute the selector. -/
theorem canonicalPairedAddition_graph_oracle_iff (a X : ℕ → Bool) :
    SelectorReducible (operationGraphOracle (canonicalPairedAddition a)) X ↔
      SelectorReducible a X :=
  (operationGraph_reducible_iff _ _).trans (canonicalPairedAddition_oracle_iff a X)

end RealizationBoundaries
