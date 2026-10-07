import KomorebiPadic.RepresentativeCompiler

/-!
# Executable finite radix compiler

The representative theorem reduces barrier crossing to a nonempty finite set
of exact natural-number costs.  This file packages that set, its minimum, and
a Boolean decision procedure whose correctness follows from the formal barrier
criterion.
-/

namespace KomorebiPadic

/-- The exact finite index set of nonempty radix blocks. -/
def radixIndexSet (p Q : ℕ) : Finset ℕ :=
  Finset.range ((Q - 1) / p + 1)

/-- The finite set of all representative barrier costs. -/
def radixCostSet (p h Q : ℕ) : Finset ℕ :=
  (radixIndexSet p Q).image (radixBarrierCost p h Q)

/-- The representative-cost set is always nonempty because the index set
contains `0`.  The mathematical barrier interpretation still assumes `Q > 0`. -/
theorem radixCostSet_nonempty (p h Q : ℕ) :
    (radixCostSet p h Q).Nonempty := by
  refine ⟨radixBarrierCost p h Q 0, ?_⟩
  apply Finset.mem_image.2
  refine ⟨0, ?_, rfl⟩
  simp [radixIndexSet]

/-- Minimum exact cost among all radix representatives. -/
def minRadixBarrierCost (p h Q : ℕ) : ℕ :=
  (radixCostSet p h Q).min' (radixCostSet_nonempty p h Q)

/-- The finite minimum is below `r` exactly when one bounded radix index has
cost below `r`. -/
theorem minRadixBarrierCost_lt_iff
    {p r h Q : ℕ} :
    minRadixBarrierCost p h Q < r ↔
      ∃ a : ℕ, a ≤ (Q - 1) / p ∧ radixBarrierCost p h Q a < r := by
  constructor
  · intro hmin
    have hmem : minRadixBarrierCost p h Q ∈ radixCostSet p h Q := by
      exact Finset.min'_mem _ _
    rw [radixCostSet, Finset.mem_image] at hmem
    rcases hmem with ⟨a, ha, hcost⟩
    refine ⟨a, ?_, ?_⟩
    · simp [radixIndexSet] at ha
      omega
    · rw [hcost]
      exact hmin
  · rintro ⟨a, ha, hcost⟩
    have ha' : a ∈ radixIndexSet p Q := by
      simp [radixIndexSet]
      omega
    have hmem : radixBarrierCost p h Q a ∈ radixCostSet p h Q := by
      exact Finset.mem_image.2 ⟨a, ha', rfl⟩
    exact lt_of_le_of_lt (Finset.min'_le _ _ hmem) hcost

/-- The representative minimum decides concrete barrier crossing. -/
theorem binomialPadic_crossesBarrier_iff_minCost
    {p r h Q : ℕ} (hp : p.Prime) (hQ : 0 < Q) :
    CrossesBarrier (binomialPadicEdgeSystem p r h hp.one_lt) p Q ↔
      minRadixBarrierCost p h Q < r := by
  rw [binomialPadic_crossesBarrier_iff_radix_range hp hQ]
  exact minRadixBarrierCost_lt_iff.symm

/-- Executable Boolean barrier decision based on the exact representative
minimum. -/
def radixCompilerCrosses (p r h Q : ℕ) : Bool :=
  decide (minRadixBarrierCost p h Q < r)

/-- Kernel-checked correctness of the executable finite compiler. -/
theorem radixCompilerCrosses_eq_true_iff
    {p r h Q : ℕ} (hp : p.Prime) (hQ : 0 < Q) :
    radixCompilerCrosses p r h Q = true ↔
      CrossesBarrier (binomialPadicEdgeSystem p r h hp.one_lt) p Q := by
  simp only [radixCompilerCrosses, decide_eq_true_eq]
  exact (binomialPadic_crossesBarrier_iff_minCost hp hQ).symm

end KomorebiPadic
