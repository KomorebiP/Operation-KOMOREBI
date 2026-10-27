import KomorebiPadic

namespace KomorebiPadic

/-- representative_p1_B2 -/
example : radixRepresentativeBudget 1 2 + radixRepresentativeBudgetPrimeEnvelopeGap 1 2 = radixRepresentativeBudgetPrimeEnvelope 1 2 ∧ radixRepresentativeBudget 1 2 ≤ radixRepresentativeBudgetPrimeEnvelope 1 2 ∧ (radixRepresentativeBudget 1 2 = radixRepresentativeBudgetPrimeEnvelope 1 2 ↔ lastRadixBlockQuotient 1 2 = 0 ∨ lastRadixBlockRemainder 1 2 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 2 ≤ 2 * 2 := by native_decide

/-- representative_p1_B10 -/
example : radixRepresentativeBudget 1 10 + radixRepresentativeBudgetPrimeEnvelopeGap 1 10 = radixRepresentativeBudgetPrimeEnvelope 1 10 ∧ radixRepresentativeBudget 1 10 ≤ radixRepresentativeBudgetPrimeEnvelope 1 10 ∧ (radixRepresentativeBudget 1 10 = radixRepresentativeBudgetPrimeEnvelope 1 10 ↔ lastRadixBlockQuotient 1 10 = 0 ∨ lastRadixBlockRemainder 1 10 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 10 ≤ 10 * 10 := by native_decide

/-- representative_p1_B18 -/
example : radixRepresentativeBudget 1 18 + radixRepresentativeBudgetPrimeEnvelopeGap 1 18 = radixRepresentativeBudgetPrimeEnvelope 1 18 ∧ radixRepresentativeBudget 1 18 ≤ radixRepresentativeBudgetPrimeEnvelope 1 18 ∧ (radixRepresentativeBudget 1 18 = radixRepresentativeBudgetPrimeEnvelope 1 18 ↔ lastRadixBlockQuotient 1 18 = 0 ∨ lastRadixBlockRemainder 1 18 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 18 ≤ 18 * 18 := by native_decide

/-- representative_p1_B26 -/
example : radixRepresentativeBudget 1 26 + radixRepresentativeBudgetPrimeEnvelopeGap 1 26 = radixRepresentativeBudgetPrimeEnvelope 1 26 ∧ radixRepresentativeBudget 1 26 ≤ radixRepresentativeBudgetPrimeEnvelope 1 26 ∧ (radixRepresentativeBudget 1 26 = radixRepresentativeBudgetPrimeEnvelope 1 26 ↔ lastRadixBlockQuotient 1 26 = 0 ∨ lastRadixBlockRemainder 1 26 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 26 ≤ 26 * 26 := by native_decide

/-- representative_p1_B34 -/
example : radixRepresentativeBudget 1 34 + radixRepresentativeBudgetPrimeEnvelopeGap 1 34 = radixRepresentativeBudgetPrimeEnvelope 1 34 ∧ radixRepresentativeBudget 1 34 ≤ radixRepresentativeBudgetPrimeEnvelope 1 34 ∧ (radixRepresentativeBudget 1 34 = radixRepresentativeBudgetPrimeEnvelope 1 34 ↔ lastRadixBlockQuotient 1 34 = 0 ∨ lastRadixBlockRemainder 1 34 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 34 ≤ 34 * 34 := by native_decide

/-- representative_p1_B42 -/
example : radixRepresentativeBudget 1 42 + radixRepresentativeBudgetPrimeEnvelopeGap 1 42 = radixRepresentativeBudgetPrimeEnvelope 1 42 ∧ radixRepresentativeBudget 1 42 ≤ radixRepresentativeBudgetPrimeEnvelope 1 42 ∧ (radixRepresentativeBudget 1 42 = radixRepresentativeBudgetPrimeEnvelope 1 42 ↔ lastRadixBlockQuotient 1 42 = 0 ∨ lastRadixBlockRemainder 1 42 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 42 ≤ 42 * 42 := by native_decide

/-- representative_p2_B0 -/
example : radixRepresentativeBudget 2 0 + radixRepresentativeBudgetPrimeEnvelopeGap 2 0 = radixRepresentativeBudgetPrimeEnvelope 2 0 ∧ radixRepresentativeBudget 2 0 ≤ radixRepresentativeBudgetPrimeEnvelope 2 0 ∧ (radixRepresentativeBudget 2 0 = radixRepresentativeBudgetPrimeEnvelope 2 0 ↔ lastRadixBlockQuotient 2 0 = 0 ∨ lastRadixBlockRemainder 2 0 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 0 ≤ 0 * 0 := by native_decide

/-- representative_p2_B8 -/
example : radixRepresentativeBudget 2 8 + radixRepresentativeBudgetPrimeEnvelopeGap 2 8 = radixRepresentativeBudgetPrimeEnvelope 2 8 ∧ radixRepresentativeBudget 2 8 ≤ radixRepresentativeBudgetPrimeEnvelope 2 8 ∧ (radixRepresentativeBudget 2 8 = radixRepresentativeBudgetPrimeEnvelope 2 8 ↔ lastRadixBlockQuotient 2 8 = 0 ∨ lastRadixBlockRemainder 2 8 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 8 ≤ 8 * 8 := by native_decide

/-- representative_p2_B16 -/
example : radixRepresentativeBudget 2 16 + radixRepresentativeBudgetPrimeEnvelopeGap 2 16 = radixRepresentativeBudgetPrimeEnvelope 2 16 ∧ radixRepresentativeBudget 2 16 ≤ radixRepresentativeBudgetPrimeEnvelope 2 16 ∧ (radixRepresentativeBudget 2 16 = radixRepresentativeBudgetPrimeEnvelope 2 16 ↔ lastRadixBlockQuotient 2 16 = 0 ∨ lastRadixBlockRemainder 2 16 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 16 ≤ 16 * 16 := by native_decide

/-- representative_p2_B24 -/
example : radixRepresentativeBudget 2 24 + radixRepresentativeBudgetPrimeEnvelopeGap 2 24 = radixRepresentativeBudgetPrimeEnvelope 2 24 ∧ radixRepresentativeBudget 2 24 ≤ radixRepresentativeBudgetPrimeEnvelope 2 24 ∧ (radixRepresentativeBudget 2 24 = radixRepresentativeBudgetPrimeEnvelope 2 24 ↔ lastRadixBlockQuotient 2 24 = 0 ∨ lastRadixBlockRemainder 2 24 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 24 ≤ 24 * 24 := by native_decide

/-- representative_p2_B32 -/
example : radixRepresentativeBudget 2 32 + radixRepresentativeBudgetPrimeEnvelopeGap 2 32 = radixRepresentativeBudgetPrimeEnvelope 2 32 ∧ radixRepresentativeBudget 2 32 ≤ radixRepresentativeBudgetPrimeEnvelope 2 32 ∧ (radixRepresentativeBudget 2 32 = radixRepresentativeBudgetPrimeEnvelope 2 32 ↔ lastRadixBlockQuotient 2 32 = 0 ∨ lastRadixBlockRemainder 2 32 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 32 ≤ 32 * 32 := by native_decide

/-- representative_p2_B40 -/
example : radixRepresentativeBudget 2 40 + radixRepresentativeBudgetPrimeEnvelopeGap 2 40 = radixRepresentativeBudgetPrimeEnvelope 2 40 ∧ radixRepresentativeBudget 2 40 ≤ radixRepresentativeBudgetPrimeEnvelope 2 40 ∧ (radixRepresentativeBudget 2 40 = radixRepresentativeBudgetPrimeEnvelope 2 40 ↔ lastRadixBlockQuotient 2 40 = 0 ∨ lastRadixBlockRemainder 2 40 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 40 ≤ 40 * 40 := by native_decide

/-- representative_p2_B48 -/
example : radixRepresentativeBudget 2 48 + radixRepresentativeBudgetPrimeEnvelopeGap 2 48 = radixRepresentativeBudgetPrimeEnvelope 2 48 ∧ radixRepresentativeBudget 2 48 ≤ radixRepresentativeBudgetPrimeEnvelope 2 48 ∧ (radixRepresentativeBudget 2 48 = radixRepresentativeBudgetPrimeEnvelope 2 48 ↔ lastRadixBlockQuotient 2 48 = 0 ∨ lastRadixBlockRemainder 2 48 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 48 ≤ 48 * 48 := by native_decide

/-- representative_p3_B6 -/
example : radixRepresentativeBudget 3 6 + radixRepresentativeBudgetPrimeEnvelopeGap 3 6 = radixRepresentativeBudgetPrimeEnvelope 3 6 ∧ radixRepresentativeBudget 3 6 ≤ radixRepresentativeBudgetPrimeEnvelope 3 6 ∧ (radixRepresentativeBudget 3 6 = radixRepresentativeBudgetPrimeEnvelope 3 6 ↔ lastRadixBlockQuotient 3 6 = 0 ∨ lastRadixBlockRemainder 3 6 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 6 ≤ 6 * 6 := by native_decide

/-- representative_p3_B14 -/
example : radixRepresentativeBudget 3 14 + radixRepresentativeBudgetPrimeEnvelopeGap 3 14 = radixRepresentativeBudgetPrimeEnvelope 3 14 ∧ radixRepresentativeBudget 3 14 ≤ radixRepresentativeBudgetPrimeEnvelope 3 14 ∧ (radixRepresentativeBudget 3 14 = radixRepresentativeBudgetPrimeEnvelope 3 14 ↔ lastRadixBlockQuotient 3 14 = 0 ∨ lastRadixBlockRemainder 3 14 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 14 ≤ 14 * 14 := by native_decide

/-- representative_p3_B22 -/
example : radixRepresentativeBudget 3 22 + radixRepresentativeBudgetPrimeEnvelopeGap 3 22 = radixRepresentativeBudgetPrimeEnvelope 3 22 ∧ radixRepresentativeBudget 3 22 ≤ radixRepresentativeBudgetPrimeEnvelope 3 22 ∧ (radixRepresentativeBudget 3 22 = radixRepresentativeBudgetPrimeEnvelope 3 22 ↔ lastRadixBlockQuotient 3 22 = 0 ∨ lastRadixBlockRemainder 3 22 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 22 ≤ 22 * 22 := by native_decide

/-- representative_p3_B30 -/
example : radixRepresentativeBudget 3 30 + radixRepresentativeBudgetPrimeEnvelopeGap 3 30 = radixRepresentativeBudgetPrimeEnvelope 3 30 ∧ radixRepresentativeBudget 3 30 ≤ radixRepresentativeBudgetPrimeEnvelope 3 30 ∧ (radixRepresentativeBudget 3 30 = radixRepresentativeBudgetPrimeEnvelope 3 30 ↔ lastRadixBlockQuotient 3 30 = 0 ∨ lastRadixBlockRemainder 3 30 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 30 ≤ 30 * 30 := by native_decide

/-- representative_p3_B38 -/
example : radixRepresentativeBudget 3 38 + radixRepresentativeBudgetPrimeEnvelopeGap 3 38 = radixRepresentativeBudgetPrimeEnvelope 3 38 ∧ radixRepresentativeBudget 3 38 ≤ radixRepresentativeBudgetPrimeEnvelope 3 38 ∧ (radixRepresentativeBudget 3 38 = radixRepresentativeBudgetPrimeEnvelope 3 38 ↔ lastRadixBlockQuotient 3 38 = 0 ∨ lastRadixBlockRemainder 3 38 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 38 ≤ 38 * 38 := by native_decide

/-- representative_p3_B46 -/
example : radixRepresentativeBudget 3 46 + radixRepresentativeBudgetPrimeEnvelopeGap 3 46 = radixRepresentativeBudgetPrimeEnvelope 3 46 ∧ radixRepresentativeBudget 3 46 ≤ radixRepresentativeBudgetPrimeEnvelope 3 46 ∧ (radixRepresentativeBudget 3 46 = radixRepresentativeBudgetPrimeEnvelope 3 46 ↔ lastRadixBlockQuotient 3 46 = 0 ∨ lastRadixBlockRemainder 3 46 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 46 ≤ 46 * 46 := by native_decide

/-- representative_p4_B4 -/
example : radixRepresentativeBudget 4 4 + radixRepresentativeBudgetPrimeEnvelopeGap 4 4 = radixRepresentativeBudgetPrimeEnvelope 4 4 ∧ radixRepresentativeBudget 4 4 ≤ radixRepresentativeBudgetPrimeEnvelope 4 4 ∧ (radixRepresentativeBudget 4 4 = radixRepresentativeBudgetPrimeEnvelope 4 4 ↔ lastRadixBlockQuotient 4 4 = 0 ∨ lastRadixBlockRemainder 4 4 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 4 ≤ 4 * 4 := by native_decide

/-- representative_p4_B12 -/
example : radixRepresentativeBudget 4 12 + radixRepresentativeBudgetPrimeEnvelopeGap 4 12 = radixRepresentativeBudgetPrimeEnvelope 4 12 ∧ radixRepresentativeBudget 4 12 ≤ radixRepresentativeBudgetPrimeEnvelope 4 12 ∧ (radixRepresentativeBudget 4 12 = radixRepresentativeBudgetPrimeEnvelope 4 12 ↔ lastRadixBlockQuotient 4 12 = 0 ∨ lastRadixBlockRemainder 4 12 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 12 ≤ 12 * 12 := by native_decide

/-- representative_p4_B20 -/
example : radixRepresentativeBudget 4 20 + radixRepresentativeBudgetPrimeEnvelopeGap 4 20 = radixRepresentativeBudgetPrimeEnvelope 4 20 ∧ radixRepresentativeBudget 4 20 ≤ radixRepresentativeBudgetPrimeEnvelope 4 20 ∧ (radixRepresentativeBudget 4 20 = radixRepresentativeBudgetPrimeEnvelope 4 20 ↔ lastRadixBlockQuotient 4 20 = 0 ∨ lastRadixBlockRemainder 4 20 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 20 ≤ 20 * 20 := by native_decide

/-- representative_p4_B28 -/
example : radixRepresentativeBudget 4 28 + radixRepresentativeBudgetPrimeEnvelopeGap 4 28 = radixRepresentativeBudgetPrimeEnvelope 4 28 ∧ radixRepresentativeBudget 4 28 ≤ radixRepresentativeBudgetPrimeEnvelope 4 28 ∧ (radixRepresentativeBudget 4 28 = radixRepresentativeBudgetPrimeEnvelope 4 28 ↔ lastRadixBlockQuotient 4 28 = 0 ∨ lastRadixBlockRemainder 4 28 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 28 ≤ 28 * 28 := by native_decide

/-- representative_p4_B36 -/
example : radixRepresentativeBudget 4 36 + radixRepresentativeBudgetPrimeEnvelopeGap 4 36 = radixRepresentativeBudgetPrimeEnvelope 4 36 ∧ radixRepresentativeBudget 4 36 ≤ radixRepresentativeBudgetPrimeEnvelope 4 36 ∧ (radixRepresentativeBudget 4 36 = radixRepresentativeBudgetPrimeEnvelope 4 36 ↔ lastRadixBlockQuotient 4 36 = 0 ∨ lastRadixBlockRemainder 4 36 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 36 ≤ 36 * 36 := by native_decide

/-- representative_p4_B44 -/
example : radixRepresentativeBudget 4 44 + radixRepresentativeBudgetPrimeEnvelopeGap 4 44 = radixRepresentativeBudgetPrimeEnvelope 4 44 ∧ radixRepresentativeBudget 4 44 ≤ radixRepresentativeBudgetPrimeEnvelope 4 44 ∧ (radixRepresentativeBudget 4 44 = radixRepresentativeBudgetPrimeEnvelope 4 44 ↔ lastRadixBlockQuotient 4 44 = 0 ∨ lastRadixBlockRemainder 4 44 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 44 ≤ 44 * 44 := by native_decide

/-- representative_p5_B2 -/
example : radixRepresentativeBudget 5 2 + radixRepresentativeBudgetPrimeEnvelopeGap 5 2 = radixRepresentativeBudgetPrimeEnvelope 5 2 ∧ radixRepresentativeBudget 5 2 ≤ radixRepresentativeBudgetPrimeEnvelope 5 2 ∧ (radixRepresentativeBudget 5 2 = radixRepresentativeBudgetPrimeEnvelope 5 2 ↔ lastRadixBlockQuotient 5 2 = 0 ∨ lastRadixBlockRemainder 5 2 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 2 ≤ 2 * 2 := by native_decide

/-- representative_p5_B10 -/
example : radixRepresentativeBudget 5 10 + radixRepresentativeBudgetPrimeEnvelopeGap 5 10 = radixRepresentativeBudgetPrimeEnvelope 5 10 ∧ radixRepresentativeBudget 5 10 ≤ radixRepresentativeBudgetPrimeEnvelope 5 10 ∧ (radixRepresentativeBudget 5 10 = radixRepresentativeBudgetPrimeEnvelope 5 10 ↔ lastRadixBlockQuotient 5 10 = 0 ∨ lastRadixBlockRemainder 5 10 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 10 ≤ 10 * 10 := by native_decide

/-- representative_p5_B18 -/
example : radixRepresentativeBudget 5 18 + radixRepresentativeBudgetPrimeEnvelopeGap 5 18 = radixRepresentativeBudgetPrimeEnvelope 5 18 ∧ radixRepresentativeBudget 5 18 ≤ radixRepresentativeBudgetPrimeEnvelope 5 18 ∧ (radixRepresentativeBudget 5 18 = radixRepresentativeBudgetPrimeEnvelope 5 18 ↔ lastRadixBlockQuotient 5 18 = 0 ∨ lastRadixBlockRemainder 5 18 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 18 ≤ 18 * 18 := by native_decide

/-- representative_p5_B26 -/
example : radixRepresentativeBudget 5 26 + radixRepresentativeBudgetPrimeEnvelopeGap 5 26 = radixRepresentativeBudgetPrimeEnvelope 5 26 ∧ radixRepresentativeBudget 5 26 ≤ radixRepresentativeBudgetPrimeEnvelope 5 26 ∧ (radixRepresentativeBudget 5 26 = radixRepresentativeBudgetPrimeEnvelope 5 26 ↔ lastRadixBlockQuotient 5 26 = 0 ∨ lastRadixBlockRemainder 5 26 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 26 ≤ 26 * 26 := by native_decide

/-- representative_p5_B34 -/
example : radixRepresentativeBudget 5 34 + radixRepresentativeBudgetPrimeEnvelopeGap 5 34 = radixRepresentativeBudgetPrimeEnvelope 5 34 ∧ radixRepresentativeBudget 5 34 ≤ radixRepresentativeBudgetPrimeEnvelope 5 34 ∧ (radixRepresentativeBudget 5 34 = radixRepresentativeBudgetPrimeEnvelope 5 34 ↔ lastRadixBlockQuotient 5 34 = 0 ∨ lastRadixBlockRemainder 5 34 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 34 ≤ 34 * 34 := by native_decide

/-- representative_p5_B42 -/
example : radixRepresentativeBudget 5 42 + radixRepresentativeBudgetPrimeEnvelopeGap 5 42 = radixRepresentativeBudgetPrimeEnvelope 5 42 ∧ radixRepresentativeBudget 5 42 ≤ radixRepresentativeBudgetPrimeEnvelope 5 42 ∧ (radixRepresentativeBudget 5 42 = radixRepresentativeBudgetPrimeEnvelope 5 42 ↔ lastRadixBlockQuotient 5 42 = 0 ∨ lastRadixBlockRemainder 5 42 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 42 ≤ 42 * 42 := by native_decide

/-- representative_p6_B0 -/
example : radixRepresentativeBudget 6 0 + radixRepresentativeBudgetPrimeEnvelopeGap 6 0 = radixRepresentativeBudgetPrimeEnvelope 6 0 ∧ radixRepresentativeBudget 6 0 ≤ radixRepresentativeBudgetPrimeEnvelope 6 0 ∧ (radixRepresentativeBudget 6 0 = radixRepresentativeBudgetPrimeEnvelope 6 0 ↔ lastRadixBlockQuotient 6 0 = 0 ∨ lastRadixBlockRemainder 6 0 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 0 ≤ 0 * 0 := by native_decide

/-- representative_p6_B8 -/
example : radixRepresentativeBudget 6 8 + radixRepresentativeBudgetPrimeEnvelopeGap 6 8 = radixRepresentativeBudgetPrimeEnvelope 6 8 ∧ radixRepresentativeBudget 6 8 ≤ radixRepresentativeBudgetPrimeEnvelope 6 8 ∧ (radixRepresentativeBudget 6 8 = radixRepresentativeBudgetPrimeEnvelope 6 8 ↔ lastRadixBlockQuotient 6 8 = 0 ∨ lastRadixBlockRemainder 6 8 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 8 ≤ 8 * 8 := by native_decide

/-- representative_p6_B16 -/
example : radixRepresentativeBudget 6 16 + radixRepresentativeBudgetPrimeEnvelopeGap 6 16 = radixRepresentativeBudgetPrimeEnvelope 6 16 ∧ radixRepresentativeBudget 6 16 ≤ radixRepresentativeBudgetPrimeEnvelope 6 16 ∧ (radixRepresentativeBudget 6 16 = radixRepresentativeBudgetPrimeEnvelope 6 16 ↔ lastRadixBlockQuotient 6 16 = 0 ∨ lastRadixBlockRemainder 6 16 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 16 ≤ 16 * 16 := by native_decide

/-- representative_p6_B24 -/
example : radixRepresentativeBudget 6 24 + radixRepresentativeBudgetPrimeEnvelopeGap 6 24 = radixRepresentativeBudgetPrimeEnvelope 6 24 ∧ radixRepresentativeBudget 6 24 ≤ radixRepresentativeBudgetPrimeEnvelope 6 24 ∧ (radixRepresentativeBudget 6 24 = radixRepresentativeBudgetPrimeEnvelope 6 24 ↔ lastRadixBlockQuotient 6 24 = 0 ∨ lastRadixBlockRemainder 6 24 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 24 ≤ 24 * 24 := by native_decide

/-- representative_p6_B32 -/
example : radixRepresentativeBudget 6 32 + radixRepresentativeBudgetPrimeEnvelopeGap 6 32 = radixRepresentativeBudgetPrimeEnvelope 6 32 ∧ radixRepresentativeBudget 6 32 ≤ radixRepresentativeBudgetPrimeEnvelope 6 32 ∧ (radixRepresentativeBudget 6 32 = radixRepresentativeBudgetPrimeEnvelope 6 32 ↔ lastRadixBlockQuotient 6 32 = 0 ∨ lastRadixBlockRemainder 6 32 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 32 ≤ 32 * 32 := by native_decide

/-- representative_p6_B40 -/
example : radixRepresentativeBudget 6 40 + radixRepresentativeBudgetPrimeEnvelopeGap 6 40 = radixRepresentativeBudgetPrimeEnvelope 6 40 ∧ radixRepresentativeBudget 6 40 ≤ radixRepresentativeBudgetPrimeEnvelope 6 40 ∧ (radixRepresentativeBudget 6 40 = radixRepresentativeBudgetPrimeEnvelope 6 40 ↔ lastRadixBlockQuotient 6 40 = 0 ∨ lastRadixBlockRemainder 6 40 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 40 ≤ 40 * 40 := by native_decide

/-- representative_p6_B48 -/
example : radixRepresentativeBudget 6 48 + radixRepresentativeBudgetPrimeEnvelopeGap 6 48 = radixRepresentativeBudgetPrimeEnvelope 6 48 ∧ radixRepresentativeBudget 6 48 ≤ radixRepresentativeBudgetPrimeEnvelope 6 48 ∧ (radixRepresentativeBudget 6 48 = radixRepresentativeBudgetPrimeEnvelope 6 48 ↔ lastRadixBlockQuotient 6 48 = 0 ∨ lastRadixBlockRemainder 6 48 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 48 ≤ 48 * 48 := by native_decide

/-- representative_p7_B6 -/
example : radixRepresentativeBudget 7 6 + radixRepresentativeBudgetPrimeEnvelopeGap 7 6 = radixRepresentativeBudgetPrimeEnvelope 7 6 ∧ radixRepresentativeBudget 7 6 ≤ radixRepresentativeBudgetPrimeEnvelope 7 6 ∧ (radixRepresentativeBudget 7 6 = radixRepresentativeBudgetPrimeEnvelope 7 6 ↔ lastRadixBlockQuotient 7 6 = 0 ∨ lastRadixBlockRemainder 7 6 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 6 ≤ 6 * 6 := by native_decide

/-- representative_p7_B14 -/
example : radixRepresentativeBudget 7 14 + radixRepresentativeBudgetPrimeEnvelopeGap 7 14 = radixRepresentativeBudgetPrimeEnvelope 7 14 ∧ radixRepresentativeBudget 7 14 ≤ radixRepresentativeBudgetPrimeEnvelope 7 14 ∧ (radixRepresentativeBudget 7 14 = radixRepresentativeBudgetPrimeEnvelope 7 14 ↔ lastRadixBlockQuotient 7 14 = 0 ∨ lastRadixBlockRemainder 7 14 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 14 ≤ 14 * 14 := by native_decide

/-- representative_p7_B22 -/
example : radixRepresentativeBudget 7 22 + radixRepresentativeBudgetPrimeEnvelopeGap 7 22 = radixRepresentativeBudgetPrimeEnvelope 7 22 ∧ radixRepresentativeBudget 7 22 ≤ radixRepresentativeBudgetPrimeEnvelope 7 22 ∧ (radixRepresentativeBudget 7 22 = radixRepresentativeBudgetPrimeEnvelope 7 22 ↔ lastRadixBlockQuotient 7 22 = 0 ∨ lastRadixBlockRemainder 7 22 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 22 ≤ 22 * 22 := by native_decide

/-- representative_p7_B30 -/
example : radixRepresentativeBudget 7 30 + radixRepresentativeBudgetPrimeEnvelopeGap 7 30 = radixRepresentativeBudgetPrimeEnvelope 7 30 ∧ radixRepresentativeBudget 7 30 ≤ radixRepresentativeBudgetPrimeEnvelope 7 30 ∧ (radixRepresentativeBudget 7 30 = radixRepresentativeBudgetPrimeEnvelope 7 30 ↔ lastRadixBlockQuotient 7 30 = 0 ∨ lastRadixBlockRemainder 7 30 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 30 ≤ 30 * 30 := by native_decide

/-- representative_p7_B38 -/
example : radixRepresentativeBudget 7 38 + radixRepresentativeBudgetPrimeEnvelopeGap 7 38 = radixRepresentativeBudgetPrimeEnvelope 7 38 ∧ radixRepresentativeBudget 7 38 ≤ radixRepresentativeBudgetPrimeEnvelope 7 38 ∧ (radixRepresentativeBudget 7 38 = radixRepresentativeBudgetPrimeEnvelope 7 38 ↔ lastRadixBlockQuotient 7 38 = 0 ∨ lastRadixBlockRemainder 7 38 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 38 ≤ 38 * 38 := by native_decide

/-- representative_p7_B46 -/
example : radixRepresentativeBudget 7 46 + radixRepresentativeBudgetPrimeEnvelopeGap 7 46 = radixRepresentativeBudgetPrimeEnvelope 7 46 ∧ radixRepresentativeBudget 7 46 ≤ radixRepresentativeBudgetPrimeEnvelope 7 46 ∧ (radixRepresentativeBudget 7 46 = radixRepresentativeBudgetPrimeEnvelope 7 46 ↔ lastRadixBlockQuotient 7 46 = 0 ∨ lastRadixBlockRemainder 7 46 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 46 ≤ 46 * 46 := by native_decide

/-- representative_p8_B4 -/
example : radixRepresentativeBudget 8 4 + radixRepresentativeBudgetPrimeEnvelopeGap 8 4 = radixRepresentativeBudgetPrimeEnvelope 8 4 ∧ radixRepresentativeBudget 8 4 ≤ radixRepresentativeBudgetPrimeEnvelope 8 4 ∧ (radixRepresentativeBudget 8 4 = radixRepresentativeBudgetPrimeEnvelope 8 4 ↔ lastRadixBlockQuotient 8 4 = 0 ∨ lastRadixBlockRemainder 8 4 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 4 ≤ 4 * 4 := by native_decide

/-- representative_p8_B12 -/
example : radixRepresentativeBudget 8 12 + radixRepresentativeBudgetPrimeEnvelopeGap 8 12 = radixRepresentativeBudgetPrimeEnvelope 8 12 ∧ radixRepresentativeBudget 8 12 ≤ radixRepresentativeBudgetPrimeEnvelope 8 12 ∧ (radixRepresentativeBudget 8 12 = radixRepresentativeBudgetPrimeEnvelope 8 12 ↔ lastRadixBlockQuotient 8 12 = 0 ∨ lastRadixBlockRemainder 8 12 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 12 ≤ 12 * 12 := by native_decide

/-- representative_p8_B20 -/
example : radixRepresentativeBudget 8 20 + radixRepresentativeBudgetPrimeEnvelopeGap 8 20 = radixRepresentativeBudgetPrimeEnvelope 8 20 ∧ radixRepresentativeBudget 8 20 ≤ radixRepresentativeBudgetPrimeEnvelope 8 20 ∧ (radixRepresentativeBudget 8 20 = radixRepresentativeBudgetPrimeEnvelope 8 20 ↔ lastRadixBlockQuotient 8 20 = 0 ∨ lastRadixBlockRemainder 8 20 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 20 ≤ 20 * 20 := by native_decide

/-- representative_p8_B28 -/
example : radixRepresentativeBudget 8 28 + radixRepresentativeBudgetPrimeEnvelopeGap 8 28 = radixRepresentativeBudgetPrimeEnvelope 8 28 ∧ radixRepresentativeBudget 8 28 ≤ radixRepresentativeBudgetPrimeEnvelope 8 28 ∧ (radixRepresentativeBudget 8 28 = radixRepresentativeBudgetPrimeEnvelope 8 28 ↔ lastRadixBlockQuotient 8 28 = 0 ∨ lastRadixBlockRemainder 8 28 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 28 ≤ 28 * 28 := by native_decide

/-- representative_p8_B36 -/
example : radixRepresentativeBudget 8 36 + radixRepresentativeBudgetPrimeEnvelopeGap 8 36 = radixRepresentativeBudgetPrimeEnvelope 8 36 ∧ radixRepresentativeBudget 8 36 ≤ radixRepresentativeBudgetPrimeEnvelope 8 36 ∧ (radixRepresentativeBudget 8 36 = radixRepresentativeBudgetPrimeEnvelope 8 36 ↔ lastRadixBlockQuotient 8 36 = 0 ∨ lastRadixBlockRemainder 8 36 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 36 ≤ 36 * 36 := by native_decide

/-- representative_p8_B44 -/
example : radixRepresentativeBudget 8 44 + radixRepresentativeBudgetPrimeEnvelopeGap 8 44 = radixRepresentativeBudgetPrimeEnvelope 8 44 ∧ radixRepresentativeBudget 8 44 ≤ radixRepresentativeBudgetPrimeEnvelope 8 44 ∧ (radixRepresentativeBudget 8 44 = radixRepresentativeBudgetPrimeEnvelope 8 44 ↔ lastRadixBlockQuotient 8 44 = 0 ∨ lastRadixBlockRemainder 8 44 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 44 ≤ 44 * 44 := by native_decide

/-- representative_p9_B2 -/
example : radixRepresentativeBudget 9 2 + radixRepresentativeBudgetPrimeEnvelopeGap 9 2 = radixRepresentativeBudgetPrimeEnvelope 9 2 ∧ radixRepresentativeBudget 9 2 ≤ radixRepresentativeBudgetPrimeEnvelope 9 2 ∧ (radixRepresentativeBudget 9 2 = radixRepresentativeBudgetPrimeEnvelope 9 2 ↔ lastRadixBlockQuotient 9 2 = 0 ∨ lastRadixBlockRemainder 9 2 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 2 ≤ 2 * 2 := by native_decide

/-- representative_p9_B10 -/
example : radixRepresentativeBudget 9 10 + radixRepresentativeBudgetPrimeEnvelopeGap 9 10 = radixRepresentativeBudgetPrimeEnvelope 9 10 ∧ radixRepresentativeBudget 9 10 ≤ radixRepresentativeBudgetPrimeEnvelope 9 10 ∧ (radixRepresentativeBudget 9 10 = radixRepresentativeBudgetPrimeEnvelope 9 10 ↔ lastRadixBlockQuotient 9 10 = 0 ∨ lastRadixBlockRemainder 9 10 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 10 ≤ 10 * 10 := by native_decide

/-- representative_p9_B18 -/
example : radixRepresentativeBudget 9 18 + radixRepresentativeBudgetPrimeEnvelopeGap 9 18 = radixRepresentativeBudgetPrimeEnvelope 9 18 ∧ radixRepresentativeBudget 9 18 ≤ radixRepresentativeBudgetPrimeEnvelope 9 18 ∧ (radixRepresentativeBudget 9 18 = radixRepresentativeBudgetPrimeEnvelope 9 18 ↔ lastRadixBlockQuotient 9 18 = 0 ∨ lastRadixBlockRemainder 9 18 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 18 ≤ 18 * 18 := by native_decide

/-- representative_p9_B26 -/
example : radixRepresentativeBudget 9 26 + radixRepresentativeBudgetPrimeEnvelopeGap 9 26 = radixRepresentativeBudgetPrimeEnvelope 9 26 ∧ radixRepresentativeBudget 9 26 ≤ radixRepresentativeBudgetPrimeEnvelope 9 26 ∧ (radixRepresentativeBudget 9 26 = radixRepresentativeBudgetPrimeEnvelope 9 26 ↔ lastRadixBlockQuotient 9 26 = 0 ∨ lastRadixBlockRemainder 9 26 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 26 ≤ 26 * 26 := by native_decide

/-- representative_p9_B34 -/
example : radixRepresentativeBudget 9 34 + radixRepresentativeBudgetPrimeEnvelopeGap 9 34 = radixRepresentativeBudgetPrimeEnvelope 9 34 ∧ radixRepresentativeBudget 9 34 ≤ radixRepresentativeBudgetPrimeEnvelope 9 34 ∧ (radixRepresentativeBudget 9 34 = radixRepresentativeBudgetPrimeEnvelope 9 34 ↔ lastRadixBlockQuotient 9 34 = 0 ∨ lastRadixBlockRemainder 9 34 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 34 ≤ 34 * 34 := by native_decide

/-- representative_p9_B42 -/
example : radixRepresentativeBudget 9 42 + radixRepresentativeBudgetPrimeEnvelopeGap 9 42 = radixRepresentativeBudgetPrimeEnvelope 9 42 ∧ radixRepresentativeBudget 9 42 ≤ radixRepresentativeBudgetPrimeEnvelope 9 42 ∧ (radixRepresentativeBudget 9 42 = radixRepresentativeBudgetPrimeEnvelope 9 42 ↔ lastRadixBlockQuotient 9 42 = 0 ∨ lastRadixBlockRemainder 9 42 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 42 ≤ 42 * 42 := by native_decide

/-- representative_p10_B0 -/
example : radixRepresentativeBudget 10 0 + radixRepresentativeBudgetPrimeEnvelopeGap 10 0 = radixRepresentativeBudgetPrimeEnvelope 10 0 ∧ radixRepresentativeBudget 10 0 ≤ radixRepresentativeBudgetPrimeEnvelope 10 0 ∧ (radixRepresentativeBudget 10 0 = radixRepresentativeBudgetPrimeEnvelope 10 0 ↔ lastRadixBlockQuotient 10 0 = 0 ∨ lastRadixBlockRemainder 10 0 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 0 ≤ 0 * 0 := by native_decide

/-- representative_p10_B8 -/
example : radixRepresentativeBudget 10 8 + radixRepresentativeBudgetPrimeEnvelopeGap 10 8 = radixRepresentativeBudgetPrimeEnvelope 10 8 ∧ radixRepresentativeBudget 10 8 ≤ radixRepresentativeBudgetPrimeEnvelope 10 8 ∧ (radixRepresentativeBudget 10 8 = radixRepresentativeBudgetPrimeEnvelope 10 8 ↔ lastRadixBlockQuotient 10 8 = 0 ∨ lastRadixBlockRemainder 10 8 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 8 ≤ 8 * 8 := by native_decide

/-- representative_p10_B16 -/
example : radixRepresentativeBudget 10 16 + radixRepresentativeBudgetPrimeEnvelopeGap 10 16 = radixRepresentativeBudgetPrimeEnvelope 10 16 ∧ radixRepresentativeBudget 10 16 ≤ radixRepresentativeBudgetPrimeEnvelope 10 16 ∧ (radixRepresentativeBudget 10 16 = radixRepresentativeBudgetPrimeEnvelope 10 16 ↔ lastRadixBlockQuotient 10 16 = 0 ∨ lastRadixBlockRemainder 10 16 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 16 ≤ 16 * 16 := by native_decide

/-- representative_p10_B24 -/
example : radixRepresentativeBudget 10 24 + radixRepresentativeBudgetPrimeEnvelopeGap 10 24 = radixRepresentativeBudgetPrimeEnvelope 10 24 ∧ radixRepresentativeBudget 10 24 ≤ radixRepresentativeBudgetPrimeEnvelope 10 24 ∧ (radixRepresentativeBudget 10 24 = radixRepresentativeBudgetPrimeEnvelope 10 24 ↔ lastRadixBlockQuotient 10 24 = 0 ∨ lastRadixBlockRemainder 10 24 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 24 ≤ 24 * 24 := by native_decide

/-- representative_p10_B32 -/
example : radixRepresentativeBudget 10 32 + radixRepresentativeBudgetPrimeEnvelopeGap 10 32 = radixRepresentativeBudgetPrimeEnvelope 10 32 ∧ radixRepresentativeBudget 10 32 ≤ radixRepresentativeBudgetPrimeEnvelope 10 32 ∧ (radixRepresentativeBudget 10 32 = radixRepresentativeBudgetPrimeEnvelope 10 32 ↔ lastRadixBlockQuotient 10 32 = 0 ∨ lastRadixBlockRemainder 10 32 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 32 ≤ 32 * 32 := by native_decide

/-- representative_p10_B40 -/
example : radixRepresentativeBudget 10 40 + radixRepresentativeBudgetPrimeEnvelopeGap 10 40 = radixRepresentativeBudgetPrimeEnvelope 10 40 ∧ radixRepresentativeBudget 10 40 ≤ radixRepresentativeBudgetPrimeEnvelope 10 40 ∧ (radixRepresentativeBudget 10 40 = radixRepresentativeBudgetPrimeEnvelope 10 40 ↔ lastRadixBlockQuotient 10 40 = 0 ∨ lastRadixBlockRemainder 10 40 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 40 ≤ 40 * 40 := by native_decide

/-- representative_p10_B48 -/
example : radixRepresentativeBudget 10 48 + radixRepresentativeBudgetPrimeEnvelopeGap 10 48 = radixRepresentativeBudgetPrimeEnvelope 10 48 ∧ radixRepresentativeBudget 10 48 ≤ radixRepresentativeBudgetPrimeEnvelope 10 48 ∧ (radixRepresentativeBudget 10 48 = radixRepresentativeBudgetPrimeEnvelope 10 48 ↔ lastRadixBlockQuotient 10 48 = 0 ∨ lastRadixBlockRemainder 10 48 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 48 ≤ 48 * 48 := by native_decide

/-- representative_p11_B6 -/
example : radixRepresentativeBudget 11 6 + radixRepresentativeBudgetPrimeEnvelopeGap 11 6 = radixRepresentativeBudgetPrimeEnvelope 11 6 ∧ radixRepresentativeBudget 11 6 ≤ radixRepresentativeBudgetPrimeEnvelope 11 6 ∧ (radixRepresentativeBudget 11 6 = radixRepresentativeBudgetPrimeEnvelope 11 6 ↔ lastRadixBlockQuotient 11 6 = 0 ∨ lastRadixBlockRemainder 11 6 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 6 ≤ 6 * 6 := by native_decide

/-- representative_p11_B14 -/
example : radixRepresentativeBudget 11 14 + radixRepresentativeBudgetPrimeEnvelopeGap 11 14 = radixRepresentativeBudgetPrimeEnvelope 11 14 ∧ radixRepresentativeBudget 11 14 ≤ radixRepresentativeBudgetPrimeEnvelope 11 14 ∧ (radixRepresentativeBudget 11 14 = radixRepresentativeBudgetPrimeEnvelope 11 14 ↔ lastRadixBlockQuotient 11 14 = 0 ∨ lastRadixBlockRemainder 11 14 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 14 ≤ 14 * 14 := by native_decide

/-- representative_p11_B22 -/
example : radixRepresentativeBudget 11 22 + radixRepresentativeBudgetPrimeEnvelopeGap 11 22 = radixRepresentativeBudgetPrimeEnvelope 11 22 ∧ radixRepresentativeBudget 11 22 ≤ radixRepresentativeBudgetPrimeEnvelope 11 22 ∧ (radixRepresentativeBudget 11 22 = radixRepresentativeBudgetPrimeEnvelope 11 22 ↔ lastRadixBlockQuotient 11 22 = 0 ∨ lastRadixBlockRemainder 11 22 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 22 ≤ 22 * 22 := by native_decide

/-- representative_p11_B30 -/
example : radixRepresentativeBudget 11 30 + radixRepresentativeBudgetPrimeEnvelopeGap 11 30 = radixRepresentativeBudgetPrimeEnvelope 11 30 ∧ radixRepresentativeBudget 11 30 ≤ radixRepresentativeBudgetPrimeEnvelope 11 30 ∧ (radixRepresentativeBudget 11 30 = radixRepresentativeBudgetPrimeEnvelope 11 30 ↔ lastRadixBlockQuotient 11 30 = 0 ∨ lastRadixBlockRemainder 11 30 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 30 ≤ 30 * 30 := by native_decide

/-- representative_p11_B38 -/
example : radixRepresentativeBudget 11 38 + radixRepresentativeBudgetPrimeEnvelopeGap 11 38 = radixRepresentativeBudgetPrimeEnvelope 11 38 ∧ radixRepresentativeBudget 11 38 ≤ radixRepresentativeBudgetPrimeEnvelope 11 38 ∧ (radixRepresentativeBudget 11 38 = radixRepresentativeBudgetPrimeEnvelope 11 38 ↔ lastRadixBlockQuotient 11 38 = 0 ∨ lastRadixBlockRemainder 11 38 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 38 ≤ 38 * 38 := by native_decide

/-- representative_p11_B46 -/
example : radixRepresentativeBudget 11 46 + radixRepresentativeBudgetPrimeEnvelopeGap 11 46 = radixRepresentativeBudgetPrimeEnvelope 11 46 ∧ radixRepresentativeBudget 11 46 ≤ radixRepresentativeBudgetPrimeEnvelope 11 46 ∧ (radixRepresentativeBudget 11 46 = radixRepresentativeBudgetPrimeEnvelope 11 46 ↔ lastRadixBlockQuotient 11 46 = 0 ∨ lastRadixBlockRemainder 11 46 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 46 ≤ 46 * 46 := by native_decide

/-- representative_p12_B4 -/
example : radixRepresentativeBudget 12 4 + radixRepresentativeBudgetPrimeEnvelopeGap 12 4 = radixRepresentativeBudgetPrimeEnvelope 12 4 ∧ radixRepresentativeBudget 12 4 ≤ radixRepresentativeBudgetPrimeEnvelope 12 4 ∧ (radixRepresentativeBudget 12 4 = radixRepresentativeBudgetPrimeEnvelope 12 4 ↔ lastRadixBlockQuotient 12 4 = 0 ∨ lastRadixBlockRemainder 12 4 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 4 ≤ 4 * 4 := by native_decide

/-- representative_p12_B12 -/
example : radixRepresentativeBudget 12 12 + radixRepresentativeBudgetPrimeEnvelopeGap 12 12 = radixRepresentativeBudgetPrimeEnvelope 12 12 ∧ radixRepresentativeBudget 12 12 ≤ radixRepresentativeBudgetPrimeEnvelope 12 12 ∧ (radixRepresentativeBudget 12 12 = radixRepresentativeBudgetPrimeEnvelope 12 12 ↔ lastRadixBlockQuotient 12 12 = 0 ∨ lastRadixBlockRemainder 12 12 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 12 ≤ 12 * 12 := by native_decide

/-- representative_p12_B20 -/
example : radixRepresentativeBudget 12 20 + radixRepresentativeBudgetPrimeEnvelopeGap 12 20 = radixRepresentativeBudgetPrimeEnvelope 12 20 ∧ radixRepresentativeBudget 12 20 ≤ radixRepresentativeBudgetPrimeEnvelope 12 20 ∧ (radixRepresentativeBudget 12 20 = radixRepresentativeBudgetPrimeEnvelope 12 20 ↔ lastRadixBlockQuotient 12 20 = 0 ∨ lastRadixBlockRemainder 12 20 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 20 ≤ 20 * 20 := by native_decide

/-- representative_p12_B28 -/
example : radixRepresentativeBudget 12 28 + radixRepresentativeBudgetPrimeEnvelopeGap 12 28 = radixRepresentativeBudgetPrimeEnvelope 12 28 ∧ radixRepresentativeBudget 12 28 ≤ radixRepresentativeBudgetPrimeEnvelope 12 28 ∧ (radixRepresentativeBudget 12 28 = radixRepresentativeBudgetPrimeEnvelope 12 28 ↔ lastRadixBlockQuotient 12 28 = 0 ∨ lastRadixBlockRemainder 12 28 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 28 ≤ 28 * 28 := by native_decide

/-- representative_p12_B36 -/
example : radixRepresentativeBudget 12 36 + radixRepresentativeBudgetPrimeEnvelopeGap 12 36 = radixRepresentativeBudgetPrimeEnvelope 12 36 ∧ radixRepresentativeBudget 12 36 ≤ radixRepresentativeBudgetPrimeEnvelope 12 36 ∧ (radixRepresentativeBudget 12 36 = radixRepresentativeBudgetPrimeEnvelope 12 36 ↔ lastRadixBlockQuotient 12 36 = 0 ∨ lastRadixBlockRemainder 12 36 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 36 ≤ 36 * 36 := by native_decide

/-- representative_p12_B44 -/
example : radixRepresentativeBudget 12 44 + radixRepresentativeBudgetPrimeEnvelopeGap 12 44 = radixRepresentativeBudgetPrimeEnvelope 12 44 ∧ radixRepresentativeBudget 12 44 ≤ radixRepresentativeBudgetPrimeEnvelope 12 44 ∧ (radixRepresentativeBudget 12 44 = radixRepresentativeBudgetPrimeEnvelope 12 44 ↔ lastRadixBlockQuotient 12 44 = 0 ∨ lastRadixBlockRemainder 12 44 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 44 ≤ 44 * 44 := by native_decide

/-- zero_base_B2 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 2 ≤ 2 * 2 := by native_decide

/-- zero_base_B10 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 10 ≤ 10 * 10 := by native_decide

/-- zero_base_B18 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 18 ≤ 18 * 18 := by native_decide

/-- zero_base_B26 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 26 ≤ 26 * 26 := by native_decide

/-- zero_base_B34 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 34 ≤ 34 * 34 := by native_decide

/-- zero_base_B42 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 42 ≤ 42 * 42 := by native_decide

/-- zero_base_B50 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 50 ≤ 50 * 50 := by native_decide

/-- zero_base_B58 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 58 ≤ 58 * 58 := by native_decide

/-- zero_base_B66 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 66 ≤ 66 * 66 := by native_decide

/-- zero_base_B74 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 74 ≤ 74 * 74 := by native_decide

/-- zero_base_B82 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 82 ≤ 82 * 82 := by native_decide

/-- zero_base_B90 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 90 ≤ 90 * 90 := by native_decide

/-- zero_base_B98 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 98 ≤ 98 * 98 := by native_decide

/-- zero_base_B106 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 106 ≤ 106 * 106 := by native_decide

/-- zero_base_B114 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 114 ≤ 114 * 114 := by native_decide

/-- zero_base_B122 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 122 ≤ 122 * 122 := by native_decide

/-- zero_base_B130 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 130 ≤ 130 * 130 := by native_decide

/-- zero_base_B138 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 138 ≤ 138 * 138 := by native_decide

/-- zero_base_B146 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 146 ≤ 146 * 146 := by native_decide

/-- zero_base_B154 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 154 ≤ 154 * 154 := by native_decide

/-- zero_base_B162 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 162 ≤ 162 * 162 := by native_decide

/-- zero_base_B170 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 170 ≤ 170 * 170 := by native_decide

/-- zero_base_B178 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 178 ≤ 178 * 178 := by native_decide

/-- zero_base_B186 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 186 ≤ 186 * 186 := by native_decide

/-- zero_base_B194 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 194 ≤ 194 * 194 := by native_decide

/-- compiler_p2_r1_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 1 2 + maximumLayerCompilerPrimeEnvelopeGap 2 1 2 = maximumLayerCompilerPrimeEnvelopeBound 2 1 2 ∧ maximumLayerCompilerTotalTests 2 1 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 1 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 1 2 ≤ maximumLayerCompilerTestBound 2 1 2 := by native_decide

/-- compiler_p2_r4_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 4 1 + maximumLayerCompilerPrimeEnvelopeGap 2 4 1 = maximumLayerCompilerPrimeEnvelopeBound 2 4 1 ∧ maximumLayerCompilerTotalTests 2 4 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 4 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 4 1 ≤ maximumLayerCompilerTestBound 2 4 1 := by native_decide

/-- compiler_p2_r7_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 7 0 + maximumLayerCompilerPrimeEnvelopeGap 2 7 0 = maximumLayerCompilerPrimeEnvelopeBound 2 7 0 ∧ maximumLayerCompilerTotalTests 2 7 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 7 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 7 0 ≤ maximumLayerCompilerTestBound 2 7 0 := by native_decide

/-- compiler_p2_r9_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 9 2 + maximumLayerCompilerPrimeEnvelopeGap 2 9 2 = maximumLayerCompilerPrimeEnvelopeBound 2 9 2 ∧ maximumLayerCompilerTotalTests 2 9 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 9 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 9 2 ≤ maximumLayerCompilerTestBound 2 9 2 := by native_decide

/-- compiler_p2_r12_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 12 1 + maximumLayerCompilerPrimeEnvelopeGap 2 12 1 = maximumLayerCompilerPrimeEnvelopeBound 2 12 1 ∧ maximumLayerCompilerTotalTests 2 12 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 12 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 12 1 ≤ maximumLayerCompilerTestBound 2 12 1 := by native_decide

/-- compiler_p2_r15_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 15 0 + maximumLayerCompilerPrimeEnvelopeGap 2 15 0 = maximumLayerCompilerPrimeEnvelopeBound 2 15 0 ∧ maximumLayerCompilerTotalTests 2 15 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 15 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 15 0 ≤ maximumLayerCompilerTestBound 2 15 0 := by native_decide

/-- compiler_p2_r17_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 17 2 + maximumLayerCompilerPrimeEnvelopeGap 2 17 2 = maximumLayerCompilerPrimeEnvelopeBound 2 17 2 ∧ maximumLayerCompilerTotalTests 2 17 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 17 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 17 2 ≤ maximumLayerCompilerTestBound 2 17 2 := by native_decide

/-- compiler_p2_r20_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 20 1 + maximumLayerCompilerPrimeEnvelopeGap 2 20 1 = maximumLayerCompilerPrimeEnvelopeBound 2 20 1 ∧ maximumLayerCompilerTotalTests 2 20 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 20 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 20 1 ≤ maximumLayerCompilerTestBound 2 20 1 := by native_decide

/-- compiler_p3_r3_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 3 0 + maximumLayerCompilerPrimeEnvelopeGap 3 3 0 = maximumLayerCompilerPrimeEnvelopeBound 3 3 0 ∧ maximumLayerCompilerTotalTests 3 3 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 3 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 3 0 ≤ maximumLayerCompilerTestBound 3 3 0 := by native_decide

/-- compiler_p3_r5_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 5 2 + maximumLayerCompilerPrimeEnvelopeGap 3 5 2 = maximumLayerCompilerPrimeEnvelopeBound 3 5 2 ∧ maximumLayerCompilerTotalTests 3 5 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 5 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 5 2 ≤ maximumLayerCompilerTestBound 3 5 2 := by native_decide

/-- compiler_p3_r8_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 8 1 + maximumLayerCompilerPrimeEnvelopeGap 3 8 1 = maximumLayerCompilerPrimeEnvelopeBound 3 8 1 ∧ maximumLayerCompilerTotalTests 3 8 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 8 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 8 1 ≤ maximumLayerCompilerTestBound 3 8 1 := by native_decide

/-- compiler_p3_r11_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 11 0 + maximumLayerCompilerPrimeEnvelopeGap 3 11 0 = maximumLayerCompilerPrimeEnvelopeBound 3 11 0 ∧ maximumLayerCompilerTotalTests 3 11 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 11 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 11 0 ≤ maximumLayerCompilerTestBound 3 11 0 := by native_decide

/-- compiler_p3_r13_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 13 2 + maximumLayerCompilerPrimeEnvelopeGap 3 13 2 = maximumLayerCompilerPrimeEnvelopeBound 3 13 2 ∧ maximumLayerCompilerTotalTests 3 13 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 13 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 13 2 ≤ maximumLayerCompilerTestBound 3 13 2 := by native_decide

/-- compiler_p3_r16_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 16 1 + maximumLayerCompilerPrimeEnvelopeGap 3 16 1 = maximumLayerCompilerPrimeEnvelopeBound 3 16 1 ∧ maximumLayerCompilerTotalTests 3 16 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 16 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 16 1 ≤ maximumLayerCompilerTestBound 3 16 1 := by native_decide

/-- compiler_p3_r19_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 19 0 + maximumLayerCompilerPrimeEnvelopeGap 3 19 0 = maximumLayerCompilerPrimeEnvelopeBound 3 19 0 ∧ maximumLayerCompilerTotalTests 3 19 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 19 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 19 0 ≤ maximumLayerCompilerTestBound 3 19 0 := by native_decide

/-- compiler_p5_r1_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 1 2 + maximumLayerCompilerPrimeEnvelopeGap 5 1 2 = maximumLayerCompilerPrimeEnvelopeBound 5 1 2 ∧ maximumLayerCompilerTotalTests 5 1 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 1 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 1 2 ≤ maximumLayerCompilerTestBound 5 1 2 := by native_decide

/-- compiler_p5_r4_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 4 1 + maximumLayerCompilerPrimeEnvelopeGap 5 4 1 = maximumLayerCompilerPrimeEnvelopeBound 5 4 1 ∧ maximumLayerCompilerTotalTests 5 4 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 4 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 4 1 ≤ maximumLayerCompilerTestBound 5 4 1 := by native_decide

/-- compiler_p5_r7_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 7 0 + maximumLayerCompilerPrimeEnvelopeGap 5 7 0 = maximumLayerCompilerPrimeEnvelopeBound 5 7 0 ∧ maximumLayerCompilerTotalTests 5 7 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 7 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 7 0 ≤ maximumLayerCompilerTestBound 5 7 0 := by native_decide

/-- compiler_p5_r9_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 9 2 + maximumLayerCompilerPrimeEnvelopeGap 5 9 2 = maximumLayerCompilerPrimeEnvelopeBound 5 9 2 ∧ maximumLayerCompilerTotalTests 5 9 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 9 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 9 2 ≤ maximumLayerCompilerTestBound 5 9 2 := by native_decide

/-- compiler_p5_r12_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 12 1 + maximumLayerCompilerPrimeEnvelopeGap 5 12 1 = maximumLayerCompilerPrimeEnvelopeBound 5 12 1 ∧ maximumLayerCompilerTotalTests 5 12 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 12 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 12 1 ≤ maximumLayerCompilerTestBound 5 12 1 := by native_decide

/-- compiler_p5_r15_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 15 0 + maximumLayerCompilerPrimeEnvelopeGap 5 15 0 = maximumLayerCompilerPrimeEnvelopeBound 5 15 0 ∧ maximumLayerCompilerTotalTests 5 15 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 15 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 15 0 ≤ maximumLayerCompilerTestBound 5 15 0 := by native_decide

/-- compiler_p5_r17_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 17 2 + maximumLayerCompilerPrimeEnvelopeGap 5 17 2 = maximumLayerCompilerPrimeEnvelopeBound 5 17 2 ∧ maximumLayerCompilerTotalTests 5 17 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 17 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 17 2 ≤ maximumLayerCompilerTestBound 5 17 2 := by native_decide

/-- compiler_p5_r20_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 20 1 + maximumLayerCompilerPrimeEnvelopeGap 5 20 1 = maximumLayerCompilerPrimeEnvelopeBound 5 20 1 ∧ maximumLayerCompilerTotalTests 5 20 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 20 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 20 1 ≤ maximumLayerCompilerTestBound 5 20 1 := by native_decide

/-- compiler_p7_r3_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 3 0 + maximumLayerCompilerPrimeEnvelopeGap 7 3 0 = maximumLayerCompilerPrimeEnvelopeBound 7 3 0 ∧ maximumLayerCompilerTotalTests 7 3 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 3 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 3 0 ≤ maximumLayerCompilerTestBound 7 3 0 := by native_decide

/-- compiler_p7_r5_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 5 2 + maximumLayerCompilerPrimeEnvelopeGap 7 5 2 = maximumLayerCompilerPrimeEnvelopeBound 7 5 2 ∧ maximumLayerCompilerTotalTests 7 5 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 5 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 5 2 ≤ maximumLayerCompilerTestBound 7 5 2 := by native_decide

/-- compiler_p7_r8_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 8 1 + maximumLayerCompilerPrimeEnvelopeGap 7 8 1 = maximumLayerCompilerPrimeEnvelopeBound 7 8 1 ∧ maximumLayerCompilerTotalTests 7 8 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 8 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 8 1 ≤ maximumLayerCompilerTestBound 7 8 1 := by native_decide

/-- compiler_p7_r11_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 11 0 + maximumLayerCompilerPrimeEnvelopeGap 7 11 0 = maximumLayerCompilerPrimeEnvelopeBound 7 11 0 ∧ maximumLayerCompilerTotalTests 7 11 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 11 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 11 0 ≤ maximumLayerCompilerTestBound 7 11 0 := by native_decide

/-- compiler_p7_r13_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 13 2 + maximumLayerCompilerPrimeEnvelopeGap 7 13 2 = maximumLayerCompilerPrimeEnvelopeBound 7 13 2 ∧ maximumLayerCompilerTotalTests 7 13 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 13 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 13 2 ≤ maximumLayerCompilerTestBound 7 13 2 := by native_decide

/-- compiler_p7_r16_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 16 1 + maximumLayerCompilerPrimeEnvelopeGap 7 16 1 = maximumLayerCompilerPrimeEnvelopeBound 7 16 1 ∧ maximumLayerCompilerTotalTests 7 16 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 16 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 16 1 ≤ maximumLayerCompilerTestBound 7 16 1 := by native_decide

/-- compiler_p7_r19_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 19 0 + maximumLayerCompilerPrimeEnvelopeGap 7 19 0 = maximumLayerCompilerPrimeEnvelopeBound 7 19 0 ∧ maximumLayerCompilerTotalTests 7 19 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 19 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 19 0 ≤ maximumLayerCompilerTestBound 7 19 0 := by native_decide

/-- compiler_p11_r1_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 1 2 + maximumLayerCompilerPrimeEnvelopeGap 11 1 2 = maximumLayerCompilerPrimeEnvelopeBound 11 1 2 ∧ maximumLayerCompilerTotalTests 11 1 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 1 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 1 2 ≤ maximumLayerCompilerTestBound 11 1 2 := by native_decide

/-- compiler_p11_r4_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 4 1 + maximumLayerCompilerPrimeEnvelopeGap 11 4 1 = maximumLayerCompilerPrimeEnvelopeBound 11 4 1 ∧ maximumLayerCompilerTotalTests 11 4 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 4 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 4 1 ≤ maximumLayerCompilerTestBound 11 4 1 := by native_decide

/-- compiler_p11_r7_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 7 0 + maximumLayerCompilerPrimeEnvelopeGap 11 7 0 = maximumLayerCompilerPrimeEnvelopeBound 11 7 0 ∧ maximumLayerCompilerTotalTests 11 7 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 7 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 7 0 ≤ maximumLayerCompilerTestBound 11 7 0 := by native_decide

/-- compiler_p11_r9_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 9 2 + maximumLayerCompilerPrimeEnvelopeGap 11 9 2 = maximumLayerCompilerPrimeEnvelopeBound 11 9 2 ∧ maximumLayerCompilerTotalTests 11 9 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 9 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 9 2 ≤ maximumLayerCompilerTestBound 11 9 2 := by native_decide

/-- compiler_p11_r12_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 12 1 + maximumLayerCompilerPrimeEnvelopeGap 11 12 1 = maximumLayerCompilerPrimeEnvelopeBound 11 12 1 ∧ maximumLayerCompilerTotalTests 11 12 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 12 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 12 1 ≤ maximumLayerCompilerTestBound 11 12 1 := by native_decide

/-- compiler_p11_r15_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 15 0 + maximumLayerCompilerPrimeEnvelopeGap 11 15 0 = maximumLayerCompilerPrimeEnvelopeBound 11 15 0 ∧ maximumLayerCompilerTotalTests 11 15 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 15 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 15 0 ≤ maximumLayerCompilerTestBound 11 15 0 := by native_decide

/-- compiler_p11_r17_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 17 2 + maximumLayerCompilerPrimeEnvelopeGap 11 17 2 = maximumLayerCompilerPrimeEnvelopeBound 11 17 2 ∧ maximumLayerCompilerTotalTests 11 17 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 17 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 17 2 ≤ maximumLayerCompilerTestBound 11 17 2 := by native_decide

/-- compiler_p11_r20_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 20 1 + maximumLayerCompilerPrimeEnvelopeGap 11 20 1 = maximumLayerCompilerPrimeEnvelopeBound 11 20 1 ∧ maximumLayerCompilerTotalTests 11 20 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 20 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 20 1 ≤ maximumLayerCompilerTestBound 11 20 1 := by native_decide

/-- compiler_p13_r3_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 3 0 + maximumLayerCompilerPrimeEnvelopeGap 13 3 0 = maximumLayerCompilerPrimeEnvelopeBound 13 3 0 ∧ maximumLayerCompilerTotalTests 13 3 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 3 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 3 0 ≤ maximumLayerCompilerTestBound 13 3 0 := by native_decide

/-- compiler_p13_r5_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 5 2 + maximumLayerCompilerPrimeEnvelopeGap 13 5 2 = maximumLayerCompilerPrimeEnvelopeBound 13 5 2 ∧ maximumLayerCompilerTotalTests 13 5 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 5 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 5 2 ≤ maximumLayerCompilerTestBound 13 5 2 := by native_decide

/-- compiler_p13_r8_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 8 1 + maximumLayerCompilerPrimeEnvelopeGap 13 8 1 = maximumLayerCompilerPrimeEnvelopeBound 13 8 1 ∧ maximumLayerCompilerTotalTests 13 8 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 8 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 8 1 ≤ maximumLayerCompilerTestBound 13 8 1 := by native_decide

/-- compiler_p13_r11_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 11 0 + maximumLayerCompilerPrimeEnvelopeGap 13 11 0 = maximumLayerCompilerPrimeEnvelopeBound 13 11 0 ∧ maximumLayerCompilerTotalTests 13 11 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 11 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 11 0 ≤ maximumLayerCompilerTestBound 13 11 0 := by native_decide

/-- compiler_p13_r13_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 13 2 + maximumLayerCompilerPrimeEnvelopeGap 13 13 2 = maximumLayerCompilerPrimeEnvelopeBound 13 13 2 ∧ maximumLayerCompilerTotalTests 13 13 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 13 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 13 2 ≤ maximumLayerCompilerTestBound 13 13 2 := by native_decide

/-- compiler_p13_r16_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 16 1 + maximumLayerCompilerPrimeEnvelopeGap 13 16 1 = maximumLayerCompilerPrimeEnvelopeBound 13 16 1 ∧ maximumLayerCompilerTotalTests 13 16 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 16 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 16 1 ≤ maximumLayerCompilerTestBound 13 16 1 := by native_decide

/-- compiler_p13_r19_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 19 0 + maximumLayerCompilerPrimeEnvelopeGap 13 19 0 = maximumLayerCompilerPrimeEnvelopeBound 13 19 0 ∧ maximumLayerCompilerTotalTests 13 19 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 19 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 19 0 ≤ maximumLayerCompilerTestBound 13 19 0 := by native_decide

end KomorebiPadic
