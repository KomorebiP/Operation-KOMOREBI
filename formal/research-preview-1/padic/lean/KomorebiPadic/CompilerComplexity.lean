import KomorebiPadic.MaximumLayerCompiler

/-!
# Certified end-to-end compiler complexity

The executable maximum-layer compiler reports three exact counters:

* quotient barrier decisions;
* final-fiber target-membership decisions;
* complete radix representative costs evaluated by the suffix-window scans.

This module retains those exact values and proves two universal envelopes.  The
first uses the exact full-representative budget at the coarse quotient bound.
The second is the closed quadratic bound `B * B + B + p`, where
`B = quotientSearchBound p r h`.
-/

namespace KomorebiPadic

open scoped BigOperators

/-- Sum of the three exact evaluation counters reported by the compiler. -/
def reportedCompilerTests (out : MaximumLayerCompilerResult) : ℕ :=
  out.quotientTests + out.finalFiberTests + out.barrierRepresentativeTests

/-- Exact total number of reported compiler evaluations. -/
def maximumLayerCompilerTotalTests (p r h : ℕ) : ℕ :=
  reportedCompilerTests (maximumLayerCompiler p r h)

/-- Full representative budget through quotient `B`.  This is an upper bound,
not a replacement for the exact suffix-window counter. -/
def radixRepresentativeBudget (p B : ℕ) : ℕ :=
  (Finset.Icc 1 B).sum fun Q => (Q - 1) / p + 1

/-- Sharper universal bound retaining the full per-quotient representative
budget at the coarse quotient-search endpoint. -/
def maximumLayerCompilerBudgetBound (p r h : ℕ) : ℕ :=
  let B := quotientSearchBound p r h
  B + p + radixRepresentativeBudget p B

/-- Closed quadratic evaluation bound obtained from the coarse quotient bound. -/
def maximumLayerCompilerTestBound (p r h : ℕ) : ℕ :=
  let B := quotientSearchBound p r h
  B * B + B + p

/-- A suffix barrier test never evaluates more complete representatives than
are present in its full radix range. -/
theorem suffixRadixBarrierResult_tested_le_fullCount (p h Q : ℕ) :
    (suffixRadixBarrierResult p h Q).tested ≤ (Q - 1) / p + 1 :=
  (suffixRadixBarrierResult_tested_bounds p h Q).2

/-- A positive quotient has at most `Q` radix representatives. -/
theorem fullRepresentativeCount_le_quotient
    {p Q : ℕ} (hQ : 0 < Q) :
    (Q - 1) / p + 1 ≤ Q := by
  have hdiv : (Q - 1) / p ≤ Q - 1 := Nat.div_le_self (Q - 1) p
  omega

/-- Consequently, a suffix barrier test never evaluates more than its quotient
index. -/
theorem suffixRadixBarrierResult_tested_le_quotient
    {p h Q : ℕ} (hQ : 0 < Q) :
    (suffixRadixBarrierResult p h Q).tested ≤ Q :=
  (suffixRadixBarrierResult_tested_le_fullCount p h Q).trans
    (fullRepresentativeCount_le_quotient hQ)

/-- The full representative budget is monotone in its terminal quotient. -/
theorem radixRepresentativeBudget_mono
    {p A B : ℕ} (hAB : A ≤ B) :
    radixRepresentativeBudget p A ≤ radixRepresentativeBudget p B := by
  unfold radixRepresentativeBudget
  apply Finset.sum_le_sum_of_subset
  intro Q hQ
  have hmem := Finset.mem_Icc.mp hQ
  exact Finset.mem_Icc.mpr ⟨hmem.1, hmem.2.trans hAB⟩

/-- The exact suffix-window counter is bounded by the full representative
budget through the selected stable quotient. -/
theorem barrierRepresentativeTestCount_le_stableBudget
    (p r h : ℕ) :
    barrierRepresentativeTestCount p r h ≤
      radixRepresentativeBudget p (stableQuotient p r h) := by
  unfold barrierRepresentativeTestCount radixRepresentativeBudget
  apply Finset.sum_le_sum
  intro Q _
  exact suffixRadixBarrierResult_tested_le_fullCount p h Q

/-- At a prime base, the exact suffix-window counter is bounded by the full
representative budget through the coarse search endpoint. -/
theorem barrierRepresentativeTestCount_le_searchBoundBudget
    {p r h : ℕ} (hp : p.Prime) :
    barrierRepresentativeTestCount p r h ≤
      radixRepresentativeBudget p (quotientSearchBound p r h) := by
  exact (barrierRepresentativeTestCount_le_stableBudget p r h).trans
    (radixRepresentativeBudget_mono
      (firstNoncrossingQuotient_le_bound (p := p) (r := r) (h := h) hp))

/-- The full representative budget is at most `B²`. -/
theorem radixRepresentativeBudget_le_sq
    {p B : ℕ} :
    radixRepresentativeBudget p B ≤ B * B := by
  unfold radixRepresentativeBudget
  calc
    (Finset.Icc 1 B).sum (fun Q => (Q - 1) / p + 1)
        ≤ (Finset.Icc 1 B).sum (fun _ => B) := by
          apply Finset.sum_le_sum
          intro Q hQmem
          have hmem := Finset.mem_Icc.mp hQmem
          exact (fullRepresentativeCount_le_quotient (by omega)).trans hmem.2
    _ = (Finset.Icc 1 B).card * B := by
          exact Finset.sum_const_nat (fun _ _ => rfl)
    _ = B * B := by
          rw [Nat.card_Icc]
          simp

/-- Across quotients `1, ..., Q*`, the exact representative count is at most
`Q*²`. -/
theorem barrierRepresentativeTestCount_le_stableQuotient_sq
    {p r h : ℕ} :
    barrierRepresentativeTestCount p r h ≤
      stableQuotient p r h * stableQuotient p r h := by
  exact (barrierRepresentativeTestCount_le_stableBudget p r h).trans
    radixRepresentativeBudget_le_sq

/-- The exact representative counter is bounded by the square of the coarse
quotient search bound. -/
theorem barrierRepresentativeTestCount_le_searchBound_sq
    {p r h : ℕ} (hp : p.Prime) :
    barrierRepresentativeTestCount p r h ≤
      quotientSearchBound p r h * quotientSearchBound p r h := by
  exact (barrierRepresentativeTestCount_le_searchBoundBudget hp).trans
    radixRepresentativeBudget_le_sq

/-- The exact quotient-test counter is bounded by the coarse quotient bound. -/
theorem quotientTestCount_le_searchBound
    {p r h : ℕ} (hp : p.Prime) :
    quotientTestCount p r h ≤ quotientSearchBound p r h := by
  rw [quotientTestCount, stableQuotientSearchResult_tested hp]
  exact firstNoncrossingQuotient_le_bound hp

/-- Upper bound using the exact full-representative budget at the coarse search
endpoint. -/
theorem maximumLayerCompilerTotalTests_le_budgetBound
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerBudgetBound p r h := by
  have hq := quotientTestCount_le_searchBound (p := p) (r := r) (h := h) hp
  have hf := (finalFiberBoundaryTestCount_bounds
    (p := p) (r := r) (h := h) hp hr).2
  have hb := barrierRepresentativeTestCount_le_searchBoundBudget
    (p := p) (r := r) (h := h) hp
  unfold maximumLayerCompilerTotalTests reportedCompilerTests
  simp only [maximumLayerCompiler]
  unfold maximumLayerCompilerBudgetBound
  dsimp
  omega

/-- The budget bound is itself below the closed quadratic envelope. -/
theorem maximumLayerCompilerBudgetBound_le_testBound
    {p r h : ℕ} :
    maximumLayerCompilerBudgetBound p r h ≤
      maximumLayerCompilerTestBound p r h := by
  have hbudget := radixRepresentativeBudget_le_sq
    (p := p) (B := quotientSearchBound p r h)
  unfold maximumLayerCompilerBudgetBound maximumLayerCompilerTestBound
  dsimp
  omega

/-- Closed upper bound for the sum of all exact reported evaluation counters. -/
theorem maximumLayerCompilerTotalTests_le_bound
    {p r h : ℕ} (hp : p.Prime) (hr : 0 < r) :
    maximumLayerCompilerTotalTests p r h ≤
      maximumLayerCompilerTestBound p r h :=
  (maximumLayerCompilerTotalTests_le_budgetBound hp hr).trans
    maximumLayerCompilerBudgetBound_le_testBound

/-- A dependent certificate retaining the exact result and exact total while
carrying proofs of the sharp budget and closed quadratic bounds. -/
structure MaximumLayerCompilerComplexityCertificate (p r h : ℕ) where
  result : MaximumLayerCompilerResult
  totalTests : ℕ
  result_exact : result = maximumLayerCompiler p r h
  total_exact : totalTests = reportedCompilerTests result
  quotientTests_le : result.quotientTests ≤ quotientSearchBound p r h
  finalFiberTests_le : result.finalFiberTests ≤ p
  representativeTests_le_budget :
    result.barrierRepresentativeTests ≤
      radixRepresentativeBudget p (quotientSearchBound p r h)
  representativeTests_le_square :
    result.barrierRepresentativeTests ≤
      quotientSearchBound p r h * quotientSearchBound p r h
  totalTests_le_budget : totalTests ≤ maximumLayerCompilerBudgetBound p r h
  totalTests_le_closed : totalTests ≤ maximumLayerCompilerTestBound p r h

/-- Construct the proof-carrying exact complexity certificate. -/
def maximumLayerCompilerComplexityCertificate
    (p r h : ℕ) (hp : p.Prime) (hr : 0 < r) :
    MaximumLayerCompilerComplexityCertificate p r h where
  result := maximumLayerCompiler p r h
  totalTests := maximumLayerCompilerTotalTests p r h
  result_exact := rfl
  total_exact := rfl
  quotientTests_le := by
    simpa [maximumLayerCompiler] using
      quotientTestCount_le_searchBound (p := p) (r := r) (h := h) hp
  finalFiberTests_le := by
    simpa [maximumLayerCompiler] using
      (finalFiberBoundaryTestCount_bounds
        (p := p) (r := r) (h := h) hp hr).2
  representativeTests_le_budget := by
    simpa [maximumLayerCompiler] using
      barrierRepresentativeTestCount_le_searchBoundBudget
        (p := p) (r := r) (h := h) hp
  representativeTests_le_square := by
    simpa [maximumLayerCompiler] using
      barrierRepresentativeTestCount_le_searchBound_sq
        (p := p) (r := r) (h := h) hp
  totalTests_le_budget := maximumLayerCompilerTotalTests_le_budgetBound hp hr
  totalTests_le_closed := maximumLayerCompilerTotalTests_le_bound hp hr

end KomorebiPadic
