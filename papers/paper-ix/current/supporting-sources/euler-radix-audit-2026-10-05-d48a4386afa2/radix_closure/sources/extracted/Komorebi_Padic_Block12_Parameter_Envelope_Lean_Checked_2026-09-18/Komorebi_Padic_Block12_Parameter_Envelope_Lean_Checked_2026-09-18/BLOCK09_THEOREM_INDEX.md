# Block 09 theorem index

Block 09 adds a certified resource envelope for the exact counters returned by the maximum-layer compiler. All 129 theorem statements inherited from Block 08 are preserved unchanged.

## Exact quantities and bounds

| Declaration | Role |
|---|---|
| `reportedCompilerTests` | Sum of the exact quotient, final-fiber, and suffix-representative counters stored in a compiler result. |
| `maximumLayerCompilerTotalTests` | Exact reported total for `maximumLayerCompiler p r h`. |
| `radixRepresentativeBudget` | Full representative budget through an endpoint `B`: `∑ Q ∈ Icc 1 B, ((Q - 1) / p + 1)`. |
| `maximumLayerCompilerBudgetBound` | Sharper endpoint budget `B + p + radixRepresentativeBudget p B`. |
| `maximumLayerCompilerTestBound` | Closed envelope `B * B + B + p`. |
| `MaximumLayerCompilerComplexityCertificate` | Dependent certificate retaining the exact result and exact total together with proofs of all component and total bounds. |
| `maximumLayerCompilerComplexityCertificate` | Constructor for the proof-carrying certificate under `p.Prime` and `0 < r`. |

Here `B = quotientSearchBound p r h`.

## New theorems

### Per-quotient representative bounds

1. `suffixRadixBarrierResult_tested_le_fullCount`
   
   A suffix scan evaluates no more complete representative costs than the full radix range at that quotient.

2. `fullRepresentativeCount_le_quotient`
   
   For `0 < Q`, the full representative count satisfies `(Q - 1) / p + 1 ≤ Q`.

3. `suffixRadixBarrierResult_tested_le_quotient`
   
   A suffix scan at positive quotient `Q` evaluates at most `Q` complete representative costs.

### Accumulated representative budgets

4. `radixRepresentativeBudget_mono`
   
   `radixRepresentativeBudget p B` is monotone in its endpoint.

5. `barrierRepresentativeTestCount_le_stableBudget`
   
   The exact accumulated suffix counter is bounded by the full budget through the selected stable quotient.

6. `barrierRepresentativeTestCount_le_searchBoundBudget`
   
   At a prime base, the exact accumulated suffix counter is bounded by the full budget through `quotientSearchBound`.

7. `radixRepresentativeBudget_le_sq`
   
   The full representative budget satisfies `radixRepresentativeBudget p B ≤ B * B` for all natural `p, B`.

8. `barrierRepresentativeTestCount_le_stableQuotient_sq`
   
   The accumulated suffix counter is at most the square of the selected stable quotient.

9. `barrierRepresentativeTestCount_le_searchBound_sq`
   
   At a prime base, the accumulated suffix counter is at most `quotientSearchBound p r h ^ 2`.

### Quotient and total-cost bounds

10. `quotientTestCount_le_searchBound`
    
    At a prime base, the exact sequential quotient-test count is bounded by `quotientSearchBound`.

11. `maximumLayerCompilerTotalTests_le_budgetBound`
    
    Under `p.Prime` and `0 < r`, the exact total is bounded by
    `B + p + radixRepresentativeBudget p B`.

12. `maximumLayerCompilerBudgetBound_le_testBound`
    
    The sharper budget is bounded by the closed quadratic envelope `B * B + B + p`.

13. `maximumLayerCompilerTotalTests_le_bound`
    
    Under `p.Prime` and `0 < r`, the exact reported total satisfies
    `maximumLayerCompilerTotalTests p r h ≤ B * B + B + p`.

## Proof boundary

The bounds concern the explicit counters reported by the formal compiler. They do not assert wall-clock complexity, memory complexity, asymptotic optimality, or tightness of the quadratic envelope. The exact counters remain executable values and are not replaced by estimates.
