import KomorebiPadic

namespace KomorebiPadic

/-- representative_p1_B4 -/
example : radixRepresentativeBudget 1 4 + radixRepresentativeBudgetPrimeEnvelopeGap 1 4 = radixRepresentativeBudgetPrimeEnvelope 1 4 ∧ radixRepresentativeBudget 1 4 ≤ radixRepresentativeBudgetPrimeEnvelope 1 4 ∧ (radixRepresentativeBudget 1 4 = radixRepresentativeBudgetPrimeEnvelope 1 4 ↔ lastRadixBlockQuotient 1 4 = 0 ∨ lastRadixBlockRemainder 1 4 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 4 ≤ 4 * 4 := by native_decide

/-- representative_p1_B12 -/
example : radixRepresentativeBudget 1 12 + radixRepresentativeBudgetPrimeEnvelopeGap 1 12 = radixRepresentativeBudgetPrimeEnvelope 1 12 ∧ radixRepresentativeBudget 1 12 ≤ radixRepresentativeBudgetPrimeEnvelope 1 12 ∧ (radixRepresentativeBudget 1 12 = radixRepresentativeBudgetPrimeEnvelope 1 12 ↔ lastRadixBlockQuotient 1 12 = 0 ∨ lastRadixBlockRemainder 1 12 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 12 ≤ 12 * 12 := by native_decide

/-- representative_p1_B20 -/
example : radixRepresentativeBudget 1 20 + radixRepresentativeBudgetPrimeEnvelopeGap 1 20 = radixRepresentativeBudgetPrimeEnvelope 1 20 ∧ radixRepresentativeBudget 1 20 ≤ radixRepresentativeBudgetPrimeEnvelope 1 20 ∧ (radixRepresentativeBudget 1 20 = radixRepresentativeBudgetPrimeEnvelope 1 20 ↔ lastRadixBlockQuotient 1 20 = 0 ∨ lastRadixBlockRemainder 1 20 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 20 ≤ 20 * 20 := by native_decide

/-- representative_p1_B28 -/
example : radixRepresentativeBudget 1 28 + radixRepresentativeBudgetPrimeEnvelopeGap 1 28 = radixRepresentativeBudgetPrimeEnvelope 1 28 ∧ radixRepresentativeBudget 1 28 ≤ radixRepresentativeBudgetPrimeEnvelope 1 28 ∧ (radixRepresentativeBudget 1 28 = radixRepresentativeBudgetPrimeEnvelope 1 28 ↔ lastRadixBlockQuotient 1 28 = 0 ∨ lastRadixBlockRemainder 1 28 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 28 ≤ 28 * 28 := by native_decide

/-- representative_p1_B36 -/
example : radixRepresentativeBudget 1 36 + radixRepresentativeBudgetPrimeEnvelopeGap 1 36 = radixRepresentativeBudgetPrimeEnvelope 1 36 ∧ radixRepresentativeBudget 1 36 ≤ radixRepresentativeBudgetPrimeEnvelope 1 36 ∧ (radixRepresentativeBudget 1 36 = radixRepresentativeBudgetPrimeEnvelope 1 36 ↔ lastRadixBlockQuotient 1 36 = 0 ∨ lastRadixBlockRemainder 1 36 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 36 ≤ 36 * 36 := by native_decide

/-- representative_p1_B44 -/
example : radixRepresentativeBudget 1 44 + radixRepresentativeBudgetPrimeEnvelopeGap 1 44 = radixRepresentativeBudgetPrimeEnvelope 1 44 ∧ radixRepresentativeBudget 1 44 ≤ radixRepresentativeBudgetPrimeEnvelope 1 44 ∧ (radixRepresentativeBudget 1 44 = radixRepresentativeBudgetPrimeEnvelope 1 44 ↔ lastRadixBlockQuotient 1 44 = 0 ∨ lastRadixBlockRemainder 1 44 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 44 ≤ 44 * 44 := by native_decide

/-- representative_p2_B2 -/
example : radixRepresentativeBudget 2 2 + radixRepresentativeBudgetPrimeEnvelopeGap 2 2 = radixRepresentativeBudgetPrimeEnvelope 2 2 ∧ radixRepresentativeBudget 2 2 ≤ radixRepresentativeBudgetPrimeEnvelope 2 2 ∧ (radixRepresentativeBudget 2 2 = radixRepresentativeBudgetPrimeEnvelope 2 2 ↔ lastRadixBlockQuotient 2 2 = 0 ∨ lastRadixBlockRemainder 2 2 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 2 ≤ 2 * 2 := by native_decide

/-- representative_p2_B10 -/
example : radixRepresentativeBudget 2 10 + radixRepresentativeBudgetPrimeEnvelopeGap 2 10 = radixRepresentativeBudgetPrimeEnvelope 2 10 ∧ radixRepresentativeBudget 2 10 ≤ radixRepresentativeBudgetPrimeEnvelope 2 10 ∧ (radixRepresentativeBudget 2 10 = radixRepresentativeBudgetPrimeEnvelope 2 10 ↔ lastRadixBlockQuotient 2 10 = 0 ∨ lastRadixBlockRemainder 2 10 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 10 ≤ 10 * 10 := by native_decide

/-- representative_p2_B18 -/
example : radixRepresentativeBudget 2 18 + radixRepresentativeBudgetPrimeEnvelopeGap 2 18 = radixRepresentativeBudgetPrimeEnvelope 2 18 ∧ radixRepresentativeBudget 2 18 ≤ radixRepresentativeBudgetPrimeEnvelope 2 18 ∧ (radixRepresentativeBudget 2 18 = radixRepresentativeBudgetPrimeEnvelope 2 18 ↔ lastRadixBlockQuotient 2 18 = 0 ∨ lastRadixBlockRemainder 2 18 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 18 ≤ 18 * 18 := by native_decide

/-- representative_p2_B26 -/
example : radixRepresentativeBudget 2 26 + radixRepresentativeBudgetPrimeEnvelopeGap 2 26 = radixRepresentativeBudgetPrimeEnvelope 2 26 ∧ radixRepresentativeBudget 2 26 ≤ radixRepresentativeBudgetPrimeEnvelope 2 26 ∧ (radixRepresentativeBudget 2 26 = radixRepresentativeBudgetPrimeEnvelope 2 26 ↔ lastRadixBlockQuotient 2 26 = 0 ∨ lastRadixBlockRemainder 2 26 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 26 ≤ 26 * 26 := by native_decide

/-- representative_p2_B34 -/
example : radixRepresentativeBudget 2 34 + radixRepresentativeBudgetPrimeEnvelopeGap 2 34 = radixRepresentativeBudgetPrimeEnvelope 2 34 ∧ radixRepresentativeBudget 2 34 ≤ radixRepresentativeBudgetPrimeEnvelope 2 34 ∧ (radixRepresentativeBudget 2 34 = radixRepresentativeBudgetPrimeEnvelope 2 34 ↔ lastRadixBlockQuotient 2 34 = 0 ∨ lastRadixBlockRemainder 2 34 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 34 ≤ 34 * 34 := by native_decide

/-- representative_p2_B42 -/
example : radixRepresentativeBudget 2 42 + radixRepresentativeBudgetPrimeEnvelopeGap 2 42 = radixRepresentativeBudgetPrimeEnvelope 2 42 ∧ radixRepresentativeBudget 2 42 ≤ radixRepresentativeBudgetPrimeEnvelope 2 42 ∧ (radixRepresentativeBudget 2 42 = radixRepresentativeBudgetPrimeEnvelope 2 42 ↔ lastRadixBlockQuotient 2 42 = 0 ∨ lastRadixBlockRemainder 2 42 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 42 ≤ 42 * 42 := by native_decide

/-- representative_p3_B0 -/
example : radixRepresentativeBudget 3 0 + radixRepresentativeBudgetPrimeEnvelopeGap 3 0 = radixRepresentativeBudgetPrimeEnvelope 3 0 ∧ radixRepresentativeBudget 3 0 ≤ radixRepresentativeBudgetPrimeEnvelope 3 0 ∧ (radixRepresentativeBudget 3 0 = radixRepresentativeBudgetPrimeEnvelope 3 0 ↔ lastRadixBlockQuotient 3 0 = 0 ∨ lastRadixBlockRemainder 3 0 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 0 ≤ 0 * 0 := by native_decide

/-- representative_p3_B8 -/
example : radixRepresentativeBudget 3 8 + radixRepresentativeBudgetPrimeEnvelopeGap 3 8 = radixRepresentativeBudgetPrimeEnvelope 3 8 ∧ radixRepresentativeBudget 3 8 ≤ radixRepresentativeBudgetPrimeEnvelope 3 8 ∧ (radixRepresentativeBudget 3 8 = radixRepresentativeBudgetPrimeEnvelope 3 8 ↔ lastRadixBlockQuotient 3 8 = 0 ∨ lastRadixBlockRemainder 3 8 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 8 ≤ 8 * 8 := by native_decide

/-- representative_p3_B16 -/
example : radixRepresentativeBudget 3 16 + radixRepresentativeBudgetPrimeEnvelopeGap 3 16 = radixRepresentativeBudgetPrimeEnvelope 3 16 ∧ radixRepresentativeBudget 3 16 ≤ radixRepresentativeBudgetPrimeEnvelope 3 16 ∧ (radixRepresentativeBudget 3 16 = radixRepresentativeBudgetPrimeEnvelope 3 16 ↔ lastRadixBlockQuotient 3 16 = 0 ∨ lastRadixBlockRemainder 3 16 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 16 ≤ 16 * 16 := by native_decide

/-- representative_p3_B24 -/
example : radixRepresentativeBudget 3 24 + radixRepresentativeBudgetPrimeEnvelopeGap 3 24 = radixRepresentativeBudgetPrimeEnvelope 3 24 ∧ radixRepresentativeBudget 3 24 ≤ radixRepresentativeBudgetPrimeEnvelope 3 24 ∧ (radixRepresentativeBudget 3 24 = radixRepresentativeBudgetPrimeEnvelope 3 24 ↔ lastRadixBlockQuotient 3 24 = 0 ∨ lastRadixBlockRemainder 3 24 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 24 ≤ 24 * 24 := by native_decide

/-- representative_p3_B32 -/
example : radixRepresentativeBudget 3 32 + radixRepresentativeBudgetPrimeEnvelopeGap 3 32 = radixRepresentativeBudgetPrimeEnvelope 3 32 ∧ radixRepresentativeBudget 3 32 ≤ radixRepresentativeBudgetPrimeEnvelope 3 32 ∧ (radixRepresentativeBudget 3 32 = radixRepresentativeBudgetPrimeEnvelope 3 32 ↔ lastRadixBlockQuotient 3 32 = 0 ∨ lastRadixBlockRemainder 3 32 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 32 ≤ 32 * 32 := by native_decide

/-- representative_p3_B40 -/
example : radixRepresentativeBudget 3 40 + radixRepresentativeBudgetPrimeEnvelopeGap 3 40 = radixRepresentativeBudgetPrimeEnvelope 3 40 ∧ radixRepresentativeBudget 3 40 ≤ radixRepresentativeBudgetPrimeEnvelope 3 40 ∧ (radixRepresentativeBudget 3 40 = radixRepresentativeBudgetPrimeEnvelope 3 40 ↔ lastRadixBlockQuotient 3 40 = 0 ∨ lastRadixBlockRemainder 3 40 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 40 ≤ 40 * 40 := by native_decide

/-- representative_p3_B48 -/
example : radixRepresentativeBudget 3 48 + radixRepresentativeBudgetPrimeEnvelopeGap 3 48 = radixRepresentativeBudgetPrimeEnvelope 3 48 ∧ radixRepresentativeBudget 3 48 ≤ radixRepresentativeBudgetPrimeEnvelope 3 48 ∧ (radixRepresentativeBudget 3 48 = radixRepresentativeBudgetPrimeEnvelope 3 48 ↔ lastRadixBlockQuotient 3 48 = 0 ∨ lastRadixBlockRemainder 3 48 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 48 ≤ 48 * 48 := by native_decide

/-- representative_p4_B6 -/
example : radixRepresentativeBudget 4 6 + radixRepresentativeBudgetPrimeEnvelopeGap 4 6 = radixRepresentativeBudgetPrimeEnvelope 4 6 ∧ radixRepresentativeBudget 4 6 ≤ radixRepresentativeBudgetPrimeEnvelope 4 6 ∧ (radixRepresentativeBudget 4 6 = radixRepresentativeBudgetPrimeEnvelope 4 6 ↔ lastRadixBlockQuotient 4 6 = 0 ∨ lastRadixBlockRemainder 4 6 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 6 ≤ 6 * 6 := by native_decide

/-- representative_p4_B14 -/
example : radixRepresentativeBudget 4 14 + radixRepresentativeBudgetPrimeEnvelopeGap 4 14 = radixRepresentativeBudgetPrimeEnvelope 4 14 ∧ radixRepresentativeBudget 4 14 ≤ radixRepresentativeBudgetPrimeEnvelope 4 14 ∧ (radixRepresentativeBudget 4 14 = radixRepresentativeBudgetPrimeEnvelope 4 14 ↔ lastRadixBlockQuotient 4 14 = 0 ∨ lastRadixBlockRemainder 4 14 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 14 ≤ 14 * 14 := by native_decide

/-- representative_p4_B22 -/
example : radixRepresentativeBudget 4 22 + radixRepresentativeBudgetPrimeEnvelopeGap 4 22 = radixRepresentativeBudgetPrimeEnvelope 4 22 ∧ radixRepresentativeBudget 4 22 ≤ radixRepresentativeBudgetPrimeEnvelope 4 22 ∧ (radixRepresentativeBudget 4 22 = radixRepresentativeBudgetPrimeEnvelope 4 22 ↔ lastRadixBlockQuotient 4 22 = 0 ∨ lastRadixBlockRemainder 4 22 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 22 ≤ 22 * 22 := by native_decide

/-- representative_p4_B30 -/
example : radixRepresentativeBudget 4 30 + radixRepresentativeBudgetPrimeEnvelopeGap 4 30 = radixRepresentativeBudgetPrimeEnvelope 4 30 ∧ radixRepresentativeBudget 4 30 ≤ radixRepresentativeBudgetPrimeEnvelope 4 30 ∧ (radixRepresentativeBudget 4 30 = radixRepresentativeBudgetPrimeEnvelope 4 30 ↔ lastRadixBlockQuotient 4 30 = 0 ∨ lastRadixBlockRemainder 4 30 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 30 ≤ 30 * 30 := by native_decide

/-- representative_p4_B38 -/
example : radixRepresentativeBudget 4 38 + radixRepresentativeBudgetPrimeEnvelopeGap 4 38 = radixRepresentativeBudgetPrimeEnvelope 4 38 ∧ radixRepresentativeBudget 4 38 ≤ radixRepresentativeBudgetPrimeEnvelope 4 38 ∧ (radixRepresentativeBudget 4 38 = radixRepresentativeBudgetPrimeEnvelope 4 38 ↔ lastRadixBlockQuotient 4 38 = 0 ∨ lastRadixBlockRemainder 4 38 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 38 ≤ 38 * 38 := by native_decide

/-- representative_p4_B46 -/
example : radixRepresentativeBudget 4 46 + radixRepresentativeBudgetPrimeEnvelopeGap 4 46 = radixRepresentativeBudgetPrimeEnvelope 4 46 ∧ radixRepresentativeBudget 4 46 ≤ radixRepresentativeBudgetPrimeEnvelope 4 46 ∧ (radixRepresentativeBudget 4 46 = radixRepresentativeBudgetPrimeEnvelope 4 46 ↔ lastRadixBlockQuotient 4 46 = 0 ∨ lastRadixBlockRemainder 4 46 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 46 ≤ 46 * 46 := by native_decide

/-- representative_p5_B4 -/
example : radixRepresentativeBudget 5 4 + radixRepresentativeBudgetPrimeEnvelopeGap 5 4 = radixRepresentativeBudgetPrimeEnvelope 5 4 ∧ radixRepresentativeBudget 5 4 ≤ radixRepresentativeBudgetPrimeEnvelope 5 4 ∧ (radixRepresentativeBudget 5 4 = radixRepresentativeBudgetPrimeEnvelope 5 4 ↔ lastRadixBlockQuotient 5 4 = 0 ∨ lastRadixBlockRemainder 5 4 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 4 ≤ 4 * 4 := by native_decide

/-- representative_p5_B12 -/
example : radixRepresentativeBudget 5 12 + radixRepresentativeBudgetPrimeEnvelopeGap 5 12 = radixRepresentativeBudgetPrimeEnvelope 5 12 ∧ radixRepresentativeBudget 5 12 ≤ radixRepresentativeBudgetPrimeEnvelope 5 12 ∧ (radixRepresentativeBudget 5 12 = radixRepresentativeBudgetPrimeEnvelope 5 12 ↔ lastRadixBlockQuotient 5 12 = 0 ∨ lastRadixBlockRemainder 5 12 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 12 ≤ 12 * 12 := by native_decide

/-- representative_p5_B20 -/
example : radixRepresentativeBudget 5 20 + radixRepresentativeBudgetPrimeEnvelopeGap 5 20 = radixRepresentativeBudgetPrimeEnvelope 5 20 ∧ radixRepresentativeBudget 5 20 ≤ radixRepresentativeBudgetPrimeEnvelope 5 20 ∧ (radixRepresentativeBudget 5 20 = radixRepresentativeBudgetPrimeEnvelope 5 20 ↔ lastRadixBlockQuotient 5 20 = 0 ∨ lastRadixBlockRemainder 5 20 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 20 ≤ 20 * 20 := by native_decide

/-- representative_p5_B28 -/
example : radixRepresentativeBudget 5 28 + radixRepresentativeBudgetPrimeEnvelopeGap 5 28 = radixRepresentativeBudgetPrimeEnvelope 5 28 ∧ radixRepresentativeBudget 5 28 ≤ radixRepresentativeBudgetPrimeEnvelope 5 28 ∧ (radixRepresentativeBudget 5 28 = radixRepresentativeBudgetPrimeEnvelope 5 28 ↔ lastRadixBlockQuotient 5 28 = 0 ∨ lastRadixBlockRemainder 5 28 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 28 ≤ 28 * 28 := by native_decide

/-- representative_p5_B36 -/
example : radixRepresentativeBudget 5 36 + radixRepresentativeBudgetPrimeEnvelopeGap 5 36 = radixRepresentativeBudgetPrimeEnvelope 5 36 ∧ radixRepresentativeBudget 5 36 ≤ radixRepresentativeBudgetPrimeEnvelope 5 36 ∧ (radixRepresentativeBudget 5 36 = radixRepresentativeBudgetPrimeEnvelope 5 36 ↔ lastRadixBlockQuotient 5 36 = 0 ∨ lastRadixBlockRemainder 5 36 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 36 ≤ 36 * 36 := by native_decide

/-- representative_p5_B44 -/
example : radixRepresentativeBudget 5 44 + radixRepresentativeBudgetPrimeEnvelopeGap 5 44 = radixRepresentativeBudgetPrimeEnvelope 5 44 ∧ radixRepresentativeBudget 5 44 ≤ radixRepresentativeBudgetPrimeEnvelope 5 44 ∧ (radixRepresentativeBudget 5 44 = radixRepresentativeBudgetPrimeEnvelope 5 44 ↔ lastRadixBlockQuotient 5 44 = 0 ∨ lastRadixBlockRemainder 5 44 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 44 ≤ 44 * 44 := by native_decide

/-- representative_p6_B2 -/
example : radixRepresentativeBudget 6 2 + radixRepresentativeBudgetPrimeEnvelopeGap 6 2 = radixRepresentativeBudgetPrimeEnvelope 6 2 ∧ radixRepresentativeBudget 6 2 ≤ radixRepresentativeBudgetPrimeEnvelope 6 2 ∧ (radixRepresentativeBudget 6 2 = radixRepresentativeBudgetPrimeEnvelope 6 2 ↔ lastRadixBlockQuotient 6 2 = 0 ∨ lastRadixBlockRemainder 6 2 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 2 ≤ 2 * 2 := by native_decide

/-- representative_p6_B10 -/
example : radixRepresentativeBudget 6 10 + radixRepresentativeBudgetPrimeEnvelopeGap 6 10 = radixRepresentativeBudgetPrimeEnvelope 6 10 ∧ radixRepresentativeBudget 6 10 ≤ radixRepresentativeBudgetPrimeEnvelope 6 10 ∧ (radixRepresentativeBudget 6 10 = radixRepresentativeBudgetPrimeEnvelope 6 10 ↔ lastRadixBlockQuotient 6 10 = 0 ∨ lastRadixBlockRemainder 6 10 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 10 ≤ 10 * 10 := by native_decide

/-- representative_p6_B18 -/
example : radixRepresentativeBudget 6 18 + radixRepresentativeBudgetPrimeEnvelopeGap 6 18 = radixRepresentativeBudgetPrimeEnvelope 6 18 ∧ radixRepresentativeBudget 6 18 ≤ radixRepresentativeBudgetPrimeEnvelope 6 18 ∧ (radixRepresentativeBudget 6 18 = radixRepresentativeBudgetPrimeEnvelope 6 18 ↔ lastRadixBlockQuotient 6 18 = 0 ∨ lastRadixBlockRemainder 6 18 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 18 ≤ 18 * 18 := by native_decide

/-- representative_p6_B26 -/
example : radixRepresentativeBudget 6 26 + radixRepresentativeBudgetPrimeEnvelopeGap 6 26 = radixRepresentativeBudgetPrimeEnvelope 6 26 ∧ radixRepresentativeBudget 6 26 ≤ radixRepresentativeBudgetPrimeEnvelope 6 26 ∧ (radixRepresentativeBudget 6 26 = radixRepresentativeBudgetPrimeEnvelope 6 26 ↔ lastRadixBlockQuotient 6 26 = 0 ∨ lastRadixBlockRemainder 6 26 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 26 ≤ 26 * 26 := by native_decide

/-- representative_p6_B34 -/
example : radixRepresentativeBudget 6 34 + radixRepresentativeBudgetPrimeEnvelopeGap 6 34 = radixRepresentativeBudgetPrimeEnvelope 6 34 ∧ radixRepresentativeBudget 6 34 ≤ radixRepresentativeBudgetPrimeEnvelope 6 34 ∧ (radixRepresentativeBudget 6 34 = radixRepresentativeBudgetPrimeEnvelope 6 34 ↔ lastRadixBlockQuotient 6 34 = 0 ∨ lastRadixBlockRemainder 6 34 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 34 ≤ 34 * 34 := by native_decide

/-- representative_p6_B42 -/
example : radixRepresentativeBudget 6 42 + radixRepresentativeBudgetPrimeEnvelopeGap 6 42 = radixRepresentativeBudgetPrimeEnvelope 6 42 ∧ radixRepresentativeBudget 6 42 ≤ radixRepresentativeBudgetPrimeEnvelope 6 42 ∧ (radixRepresentativeBudget 6 42 = radixRepresentativeBudgetPrimeEnvelope 6 42 ↔ lastRadixBlockQuotient 6 42 = 0 ∨ lastRadixBlockRemainder 6 42 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 42 ≤ 42 * 42 := by native_decide

/-- representative_p7_B0 -/
example : radixRepresentativeBudget 7 0 + radixRepresentativeBudgetPrimeEnvelopeGap 7 0 = radixRepresentativeBudgetPrimeEnvelope 7 0 ∧ radixRepresentativeBudget 7 0 ≤ radixRepresentativeBudgetPrimeEnvelope 7 0 ∧ (radixRepresentativeBudget 7 0 = radixRepresentativeBudgetPrimeEnvelope 7 0 ↔ lastRadixBlockQuotient 7 0 = 0 ∨ lastRadixBlockRemainder 7 0 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 0 ≤ 0 * 0 := by native_decide

/-- representative_p7_B8 -/
example : radixRepresentativeBudget 7 8 + radixRepresentativeBudgetPrimeEnvelopeGap 7 8 = radixRepresentativeBudgetPrimeEnvelope 7 8 ∧ radixRepresentativeBudget 7 8 ≤ radixRepresentativeBudgetPrimeEnvelope 7 8 ∧ (radixRepresentativeBudget 7 8 = radixRepresentativeBudgetPrimeEnvelope 7 8 ↔ lastRadixBlockQuotient 7 8 = 0 ∨ lastRadixBlockRemainder 7 8 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 8 ≤ 8 * 8 := by native_decide

/-- representative_p7_B16 -/
example : radixRepresentativeBudget 7 16 + radixRepresentativeBudgetPrimeEnvelopeGap 7 16 = radixRepresentativeBudgetPrimeEnvelope 7 16 ∧ radixRepresentativeBudget 7 16 ≤ radixRepresentativeBudgetPrimeEnvelope 7 16 ∧ (radixRepresentativeBudget 7 16 = radixRepresentativeBudgetPrimeEnvelope 7 16 ↔ lastRadixBlockQuotient 7 16 = 0 ∨ lastRadixBlockRemainder 7 16 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 16 ≤ 16 * 16 := by native_decide

/-- representative_p7_B24 -/
example : radixRepresentativeBudget 7 24 + radixRepresentativeBudgetPrimeEnvelopeGap 7 24 = radixRepresentativeBudgetPrimeEnvelope 7 24 ∧ radixRepresentativeBudget 7 24 ≤ radixRepresentativeBudgetPrimeEnvelope 7 24 ∧ (radixRepresentativeBudget 7 24 = radixRepresentativeBudgetPrimeEnvelope 7 24 ↔ lastRadixBlockQuotient 7 24 = 0 ∨ lastRadixBlockRemainder 7 24 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 24 ≤ 24 * 24 := by native_decide

/-- representative_p7_B32 -/
example : radixRepresentativeBudget 7 32 + radixRepresentativeBudgetPrimeEnvelopeGap 7 32 = radixRepresentativeBudgetPrimeEnvelope 7 32 ∧ radixRepresentativeBudget 7 32 ≤ radixRepresentativeBudgetPrimeEnvelope 7 32 ∧ (radixRepresentativeBudget 7 32 = radixRepresentativeBudgetPrimeEnvelope 7 32 ↔ lastRadixBlockQuotient 7 32 = 0 ∨ lastRadixBlockRemainder 7 32 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 32 ≤ 32 * 32 := by native_decide

/-- representative_p7_B40 -/
example : radixRepresentativeBudget 7 40 + radixRepresentativeBudgetPrimeEnvelopeGap 7 40 = radixRepresentativeBudgetPrimeEnvelope 7 40 ∧ radixRepresentativeBudget 7 40 ≤ radixRepresentativeBudgetPrimeEnvelope 7 40 ∧ (radixRepresentativeBudget 7 40 = radixRepresentativeBudgetPrimeEnvelope 7 40 ↔ lastRadixBlockQuotient 7 40 = 0 ∨ lastRadixBlockRemainder 7 40 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 40 ≤ 40 * 40 := by native_decide

/-- representative_p7_B48 -/
example : radixRepresentativeBudget 7 48 + radixRepresentativeBudgetPrimeEnvelopeGap 7 48 = radixRepresentativeBudgetPrimeEnvelope 7 48 ∧ radixRepresentativeBudget 7 48 ≤ radixRepresentativeBudgetPrimeEnvelope 7 48 ∧ (radixRepresentativeBudget 7 48 = radixRepresentativeBudgetPrimeEnvelope 7 48 ↔ lastRadixBlockQuotient 7 48 = 0 ∨ lastRadixBlockRemainder 7 48 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 48 ≤ 48 * 48 := by native_decide

/-- representative_p8_B6 -/
example : radixRepresentativeBudget 8 6 + radixRepresentativeBudgetPrimeEnvelopeGap 8 6 = radixRepresentativeBudgetPrimeEnvelope 8 6 ∧ radixRepresentativeBudget 8 6 ≤ radixRepresentativeBudgetPrimeEnvelope 8 6 ∧ (radixRepresentativeBudget 8 6 = radixRepresentativeBudgetPrimeEnvelope 8 6 ↔ lastRadixBlockQuotient 8 6 = 0 ∨ lastRadixBlockRemainder 8 6 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 6 ≤ 6 * 6 := by native_decide

/-- representative_p8_B14 -/
example : radixRepresentativeBudget 8 14 + radixRepresentativeBudgetPrimeEnvelopeGap 8 14 = radixRepresentativeBudgetPrimeEnvelope 8 14 ∧ radixRepresentativeBudget 8 14 ≤ radixRepresentativeBudgetPrimeEnvelope 8 14 ∧ (radixRepresentativeBudget 8 14 = radixRepresentativeBudgetPrimeEnvelope 8 14 ↔ lastRadixBlockQuotient 8 14 = 0 ∨ lastRadixBlockRemainder 8 14 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 14 ≤ 14 * 14 := by native_decide

/-- representative_p8_B22 -/
example : radixRepresentativeBudget 8 22 + radixRepresentativeBudgetPrimeEnvelopeGap 8 22 = radixRepresentativeBudgetPrimeEnvelope 8 22 ∧ radixRepresentativeBudget 8 22 ≤ radixRepresentativeBudgetPrimeEnvelope 8 22 ∧ (radixRepresentativeBudget 8 22 = radixRepresentativeBudgetPrimeEnvelope 8 22 ↔ lastRadixBlockQuotient 8 22 = 0 ∨ lastRadixBlockRemainder 8 22 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 22 ≤ 22 * 22 := by native_decide

/-- representative_p8_B30 -/
example : radixRepresentativeBudget 8 30 + radixRepresentativeBudgetPrimeEnvelopeGap 8 30 = radixRepresentativeBudgetPrimeEnvelope 8 30 ∧ radixRepresentativeBudget 8 30 ≤ radixRepresentativeBudgetPrimeEnvelope 8 30 ∧ (radixRepresentativeBudget 8 30 = radixRepresentativeBudgetPrimeEnvelope 8 30 ↔ lastRadixBlockQuotient 8 30 = 0 ∨ lastRadixBlockRemainder 8 30 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 30 ≤ 30 * 30 := by native_decide

/-- representative_p8_B38 -/
example : radixRepresentativeBudget 8 38 + radixRepresentativeBudgetPrimeEnvelopeGap 8 38 = radixRepresentativeBudgetPrimeEnvelope 8 38 ∧ radixRepresentativeBudget 8 38 ≤ radixRepresentativeBudgetPrimeEnvelope 8 38 ∧ (radixRepresentativeBudget 8 38 = radixRepresentativeBudgetPrimeEnvelope 8 38 ↔ lastRadixBlockQuotient 8 38 = 0 ∨ lastRadixBlockRemainder 8 38 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 38 ≤ 38 * 38 := by native_decide

/-- representative_p8_B46 -/
example : radixRepresentativeBudget 8 46 + radixRepresentativeBudgetPrimeEnvelopeGap 8 46 = radixRepresentativeBudgetPrimeEnvelope 8 46 ∧ radixRepresentativeBudget 8 46 ≤ radixRepresentativeBudgetPrimeEnvelope 8 46 ∧ (radixRepresentativeBudget 8 46 = radixRepresentativeBudgetPrimeEnvelope 8 46 ↔ lastRadixBlockQuotient 8 46 = 0 ∨ lastRadixBlockRemainder 8 46 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 46 ≤ 46 * 46 := by native_decide

/-- representative_p9_B4 -/
example : radixRepresentativeBudget 9 4 + radixRepresentativeBudgetPrimeEnvelopeGap 9 4 = radixRepresentativeBudgetPrimeEnvelope 9 4 ∧ radixRepresentativeBudget 9 4 ≤ radixRepresentativeBudgetPrimeEnvelope 9 4 ∧ (radixRepresentativeBudget 9 4 = radixRepresentativeBudgetPrimeEnvelope 9 4 ↔ lastRadixBlockQuotient 9 4 = 0 ∨ lastRadixBlockRemainder 9 4 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 4 ≤ 4 * 4 := by native_decide

/-- representative_p9_B12 -/
example : radixRepresentativeBudget 9 12 + radixRepresentativeBudgetPrimeEnvelopeGap 9 12 = radixRepresentativeBudgetPrimeEnvelope 9 12 ∧ radixRepresentativeBudget 9 12 ≤ radixRepresentativeBudgetPrimeEnvelope 9 12 ∧ (radixRepresentativeBudget 9 12 = radixRepresentativeBudgetPrimeEnvelope 9 12 ↔ lastRadixBlockQuotient 9 12 = 0 ∨ lastRadixBlockRemainder 9 12 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 12 ≤ 12 * 12 := by native_decide

/-- representative_p9_B20 -/
example : radixRepresentativeBudget 9 20 + radixRepresentativeBudgetPrimeEnvelopeGap 9 20 = radixRepresentativeBudgetPrimeEnvelope 9 20 ∧ radixRepresentativeBudget 9 20 ≤ radixRepresentativeBudgetPrimeEnvelope 9 20 ∧ (radixRepresentativeBudget 9 20 = radixRepresentativeBudgetPrimeEnvelope 9 20 ↔ lastRadixBlockQuotient 9 20 = 0 ∨ lastRadixBlockRemainder 9 20 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 20 ≤ 20 * 20 := by native_decide

/-- representative_p9_B28 -/
example : radixRepresentativeBudget 9 28 + radixRepresentativeBudgetPrimeEnvelopeGap 9 28 = radixRepresentativeBudgetPrimeEnvelope 9 28 ∧ radixRepresentativeBudget 9 28 ≤ radixRepresentativeBudgetPrimeEnvelope 9 28 ∧ (radixRepresentativeBudget 9 28 = radixRepresentativeBudgetPrimeEnvelope 9 28 ↔ lastRadixBlockQuotient 9 28 = 0 ∨ lastRadixBlockRemainder 9 28 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 28 ≤ 28 * 28 := by native_decide

/-- representative_p9_B36 -/
example : radixRepresentativeBudget 9 36 + radixRepresentativeBudgetPrimeEnvelopeGap 9 36 = radixRepresentativeBudgetPrimeEnvelope 9 36 ∧ radixRepresentativeBudget 9 36 ≤ radixRepresentativeBudgetPrimeEnvelope 9 36 ∧ (radixRepresentativeBudget 9 36 = radixRepresentativeBudgetPrimeEnvelope 9 36 ↔ lastRadixBlockQuotient 9 36 = 0 ∨ lastRadixBlockRemainder 9 36 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 36 ≤ 36 * 36 := by native_decide

/-- representative_p9_B44 -/
example : radixRepresentativeBudget 9 44 + radixRepresentativeBudgetPrimeEnvelopeGap 9 44 = radixRepresentativeBudgetPrimeEnvelope 9 44 ∧ radixRepresentativeBudget 9 44 ≤ radixRepresentativeBudgetPrimeEnvelope 9 44 ∧ (radixRepresentativeBudget 9 44 = radixRepresentativeBudgetPrimeEnvelope 9 44 ↔ lastRadixBlockQuotient 9 44 = 0 ∨ lastRadixBlockRemainder 9 44 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 44 ≤ 44 * 44 := by native_decide

/-- representative_p10_B2 -/
example : radixRepresentativeBudget 10 2 + radixRepresentativeBudgetPrimeEnvelopeGap 10 2 = radixRepresentativeBudgetPrimeEnvelope 10 2 ∧ radixRepresentativeBudget 10 2 ≤ radixRepresentativeBudgetPrimeEnvelope 10 2 ∧ (radixRepresentativeBudget 10 2 = radixRepresentativeBudgetPrimeEnvelope 10 2 ↔ lastRadixBlockQuotient 10 2 = 0 ∨ lastRadixBlockRemainder 10 2 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 2 ≤ 2 * 2 := by native_decide

/-- representative_p10_B10 -/
example : radixRepresentativeBudget 10 10 + radixRepresentativeBudgetPrimeEnvelopeGap 10 10 = radixRepresentativeBudgetPrimeEnvelope 10 10 ∧ radixRepresentativeBudget 10 10 ≤ radixRepresentativeBudgetPrimeEnvelope 10 10 ∧ (radixRepresentativeBudget 10 10 = radixRepresentativeBudgetPrimeEnvelope 10 10 ↔ lastRadixBlockQuotient 10 10 = 0 ∨ lastRadixBlockRemainder 10 10 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 10 ≤ 10 * 10 := by native_decide

/-- representative_p10_B18 -/
example : radixRepresentativeBudget 10 18 + radixRepresentativeBudgetPrimeEnvelopeGap 10 18 = radixRepresentativeBudgetPrimeEnvelope 10 18 ∧ radixRepresentativeBudget 10 18 ≤ radixRepresentativeBudgetPrimeEnvelope 10 18 ∧ (radixRepresentativeBudget 10 18 = radixRepresentativeBudgetPrimeEnvelope 10 18 ↔ lastRadixBlockQuotient 10 18 = 0 ∨ lastRadixBlockRemainder 10 18 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 18 ≤ 18 * 18 := by native_decide

/-- representative_p10_B26 -/
example : radixRepresentativeBudget 10 26 + radixRepresentativeBudgetPrimeEnvelopeGap 10 26 = radixRepresentativeBudgetPrimeEnvelope 10 26 ∧ radixRepresentativeBudget 10 26 ≤ radixRepresentativeBudgetPrimeEnvelope 10 26 ∧ (radixRepresentativeBudget 10 26 = radixRepresentativeBudgetPrimeEnvelope 10 26 ↔ lastRadixBlockQuotient 10 26 = 0 ∨ lastRadixBlockRemainder 10 26 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 26 ≤ 26 * 26 := by native_decide

/-- representative_p10_B34 -/
example : radixRepresentativeBudget 10 34 + radixRepresentativeBudgetPrimeEnvelopeGap 10 34 = radixRepresentativeBudgetPrimeEnvelope 10 34 ∧ radixRepresentativeBudget 10 34 ≤ radixRepresentativeBudgetPrimeEnvelope 10 34 ∧ (radixRepresentativeBudget 10 34 = radixRepresentativeBudgetPrimeEnvelope 10 34 ↔ lastRadixBlockQuotient 10 34 = 0 ∨ lastRadixBlockRemainder 10 34 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 34 ≤ 34 * 34 := by native_decide

/-- representative_p10_B42 -/
example : radixRepresentativeBudget 10 42 + radixRepresentativeBudgetPrimeEnvelopeGap 10 42 = radixRepresentativeBudgetPrimeEnvelope 10 42 ∧ radixRepresentativeBudget 10 42 ≤ radixRepresentativeBudgetPrimeEnvelope 10 42 ∧ (radixRepresentativeBudget 10 42 = radixRepresentativeBudgetPrimeEnvelope 10 42 ↔ lastRadixBlockQuotient 10 42 = 0 ∨ lastRadixBlockRemainder 10 42 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 42 ≤ 42 * 42 := by native_decide

/-- representative_p11_B0 -/
example : radixRepresentativeBudget 11 0 + radixRepresentativeBudgetPrimeEnvelopeGap 11 0 = radixRepresentativeBudgetPrimeEnvelope 11 0 ∧ radixRepresentativeBudget 11 0 ≤ radixRepresentativeBudgetPrimeEnvelope 11 0 ∧ (radixRepresentativeBudget 11 0 = radixRepresentativeBudgetPrimeEnvelope 11 0 ↔ lastRadixBlockQuotient 11 0 = 0 ∨ lastRadixBlockRemainder 11 0 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 0 ≤ 0 * 0 := by native_decide

/-- representative_p11_B8 -/
example : radixRepresentativeBudget 11 8 + radixRepresentativeBudgetPrimeEnvelopeGap 11 8 = radixRepresentativeBudgetPrimeEnvelope 11 8 ∧ radixRepresentativeBudget 11 8 ≤ radixRepresentativeBudgetPrimeEnvelope 11 8 ∧ (radixRepresentativeBudget 11 8 = radixRepresentativeBudgetPrimeEnvelope 11 8 ↔ lastRadixBlockQuotient 11 8 = 0 ∨ lastRadixBlockRemainder 11 8 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 8 ≤ 8 * 8 := by native_decide

/-- representative_p11_B16 -/
example : radixRepresentativeBudget 11 16 + radixRepresentativeBudgetPrimeEnvelopeGap 11 16 = radixRepresentativeBudgetPrimeEnvelope 11 16 ∧ radixRepresentativeBudget 11 16 ≤ radixRepresentativeBudgetPrimeEnvelope 11 16 ∧ (radixRepresentativeBudget 11 16 = radixRepresentativeBudgetPrimeEnvelope 11 16 ↔ lastRadixBlockQuotient 11 16 = 0 ∨ lastRadixBlockRemainder 11 16 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 16 ≤ 16 * 16 := by native_decide

/-- representative_p11_B24 -/
example : radixRepresentativeBudget 11 24 + radixRepresentativeBudgetPrimeEnvelopeGap 11 24 = radixRepresentativeBudgetPrimeEnvelope 11 24 ∧ radixRepresentativeBudget 11 24 ≤ radixRepresentativeBudgetPrimeEnvelope 11 24 ∧ (radixRepresentativeBudget 11 24 = radixRepresentativeBudgetPrimeEnvelope 11 24 ↔ lastRadixBlockQuotient 11 24 = 0 ∨ lastRadixBlockRemainder 11 24 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 24 ≤ 24 * 24 := by native_decide

/-- representative_p11_B32 -/
example : radixRepresentativeBudget 11 32 + radixRepresentativeBudgetPrimeEnvelopeGap 11 32 = radixRepresentativeBudgetPrimeEnvelope 11 32 ∧ radixRepresentativeBudget 11 32 ≤ radixRepresentativeBudgetPrimeEnvelope 11 32 ∧ (radixRepresentativeBudget 11 32 = radixRepresentativeBudgetPrimeEnvelope 11 32 ↔ lastRadixBlockQuotient 11 32 = 0 ∨ lastRadixBlockRemainder 11 32 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 32 ≤ 32 * 32 := by native_decide

/-- representative_p11_B40 -/
example : radixRepresentativeBudget 11 40 + radixRepresentativeBudgetPrimeEnvelopeGap 11 40 = radixRepresentativeBudgetPrimeEnvelope 11 40 ∧ radixRepresentativeBudget 11 40 ≤ radixRepresentativeBudgetPrimeEnvelope 11 40 ∧ (radixRepresentativeBudget 11 40 = radixRepresentativeBudgetPrimeEnvelope 11 40 ↔ lastRadixBlockQuotient 11 40 = 0 ∨ lastRadixBlockRemainder 11 40 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 40 ≤ 40 * 40 := by native_decide

/-- representative_p11_B48 -/
example : radixRepresentativeBudget 11 48 + radixRepresentativeBudgetPrimeEnvelopeGap 11 48 = radixRepresentativeBudgetPrimeEnvelope 11 48 ∧ radixRepresentativeBudget 11 48 ≤ radixRepresentativeBudgetPrimeEnvelope 11 48 ∧ (radixRepresentativeBudget 11 48 = radixRepresentativeBudgetPrimeEnvelope 11 48 ↔ lastRadixBlockQuotient 11 48 = 0 ∨ lastRadixBlockRemainder 11 48 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 48 ≤ 48 * 48 := by native_decide

/-- representative_p12_B6 -/
example : radixRepresentativeBudget 12 6 + radixRepresentativeBudgetPrimeEnvelopeGap 12 6 = radixRepresentativeBudgetPrimeEnvelope 12 6 ∧ radixRepresentativeBudget 12 6 ≤ radixRepresentativeBudgetPrimeEnvelope 12 6 ∧ (radixRepresentativeBudget 12 6 = radixRepresentativeBudgetPrimeEnvelope 12 6 ↔ lastRadixBlockQuotient 12 6 = 0 ∨ lastRadixBlockRemainder 12 6 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 6 ≤ 6 * 6 := by native_decide

/-- representative_p12_B14 -/
example : radixRepresentativeBudget 12 14 + radixRepresentativeBudgetPrimeEnvelopeGap 12 14 = radixRepresentativeBudgetPrimeEnvelope 12 14 ∧ radixRepresentativeBudget 12 14 ≤ radixRepresentativeBudgetPrimeEnvelope 12 14 ∧ (radixRepresentativeBudget 12 14 = radixRepresentativeBudgetPrimeEnvelope 12 14 ↔ lastRadixBlockQuotient 12 14 = 0 ∨ lastRadixBlockRemainder 12 14 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 14 ≤ 14 * 14 := by native_decide

/-- representative_p12_B22 -/
example : radixRepresentativeBudget 12 22 + radixRepresentativeBudgetPrimeEnvelopeGap 12 22 = radixRepresentativeBudgetPrimeEnvelope 12 22 ∧ radixRepresentativeBudget 12 22 ≤ radixRepresentativeBudgetPrimeEnvelope 12 22 ∧ (radixRepresentativeBudget 12 22 = radixRepresentativeBudgetPrimeEnvelope 12 22 ↔ lastRadixBlockQuotient 12 22 = 0 ∨ lastRadixBlockRemainder 12 22 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 22 ≤ 22 * 22 := by native_decide

/-- representative_p12_B30 -/
example : radixRepresentativeBudget 12 30 + radixRepresentativeBudgetPrimeEnvelopeGap 12 30 = radixRepresentativeBudgetPrimeEnvelope 12 30 ∧ radixRepresentativeBudget 12 30 ≤ radixRepresentativeBudgetPrimeEnvelope 12 30 ∧ (radixRepresentativeBudget 12 30 = radixRepresentativeBudgetPrimeEnvelope 12 30 ↔ lastRadixBlockQuotient 12 30 = 0 ∨ lastRadixBlockRemainder 12 30 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 30 ≤ 30 * 30 := by native_decide

/-- representative_p12_B38 -/
example : radixRepresentativeBudget 12 38 + radixRepresentativeBudgetPrimeEnvelopeGap 12 38 = radixRepresentativeBudgetPrimeEnvelope 12 38 ∧ radixRepresentativeBudget 12 38 ≤ radixRepresentativeBudgetPrimeEnvelope 12 38 ∧ (radixRepresentativeBudget 12 38 = radixRepresentativeBudgetPrimeEnvelope 12 38 ↔ lastRadixBlockQuotient 12 38 = 0 ∨ lastRadixBlockRemainder 12 38 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 38 ≤ 38 * 38 := by native_decide

/-- representative_p12_B46 -/
example : radixRepresentativeBudget 12 46 + radixRepresentativeBudgetPrimeEnvelopeGap 12 46 = radixRepresentativeBudgetPrimeEnvelope 12 46 ∧ radixRepresentativeBudget 12 46 ≤ radixRepresentativeBudgetPrimeEnvelope 12 46 ∧ (radixRepresentativeBudget 12 46 = radixRepresentativeBudgetPrimeEnvelope 12 46 ↔ lastRadixBlockQuotient 12 46 = 0 ∨ lastRadixBlockRemainder 12 46 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 46 ≤ 46 * 46 := by native_decide

/-- zero_base_B4 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 4 ≤ 4 * 4 := by native_decide

/-- zero_base_B12 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 12 ≤ 12 * 12 := by native_decide

/-- zero_base_B20 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 20 ≤ 20 * 20 := by native_decide

/-- zero_base_B28 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 28 ≤ 28 * 28 := by native_decide

/-- zero_base_B36 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 36 ≤ 36 * 36 := by native_decide

/-- zero_base_B44 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 44 ≤ 44 * 44 := by native_decide

/-- zero_base_B52 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 52 ≤ 52 * 52 := by native_decide

/-- zero_base_B60 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 60 ≤ 60 * 60 := by native_decide

/-- zero_base_B68 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 68 ≤ 68 * 68 := by native_decide

/-- zero_base_B76 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 76 ≤ 76 * 76 := by native_decide

/-- zero_base_B84 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 84 ≤ 84 * 84 := by native_decide

/-- zero_base_B92 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 92 ≤ 92 * 92 := by native_decide

/-- zero_base_B100 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 100 ≤ 100 * 100 := by native_decide

/-- zero_base_B108 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 108 ≤ 108 * 108 := by native_decide

/-- zero_base_B116 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 116 ≤ 116 * 116 := by native_decide

/-- zero_base_B124 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 124 ≤ 124 * 124 := by native_decide

/-- zero_base_B132 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 132 ≤ 132 * 132 := by native_decide

/-- zero_base_B140 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 140 ≤ 140 * 140 := by native_decide

/-- zero_base_B148 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 148 ≤ 148 * 148 := by native_decide

/-- zero_base_B156 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 156 ≤ 156 * 156 := by native_decide

/-- zero_base_B164 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 164 ≤ 164 * 164 := by native_decide

/-- zero_base_B172 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 172 ≤ 172 * 172 := by native_decide

/-- zero_base_B180 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 180 ≤ 180 * 180 := by native_decide

/-- zero_base_B188 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 188 ≤ 188 * 188 := by native_decide

/-- zero_base_B196 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 196 ≤ 196 * 196 := by native_decide

/-- compiler_p2_r2_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 2 1 + maximumLayerCompilerPrimeEnvelopeGap 2 2 1 = maximumLayerCompilerPrimeEnvelopeBound 2 2 1 ∧ maximumLayerCompilerTotalTests 2 2 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 2 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 2 1 ≤ maximumLayerCompilerTestBound 2 2 1 := by native_decide

/-- compiler_p2_r5_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 5 0 + maximumLayerCompilerPrimeEnvelopeGap 2 5 0 = maximumLayerCompilerPrimeEnvelopeBound 2 5 0 ∧ maximumLayerCompilerTotalTests 2 5 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 5 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 5 0 ≤ maximumLayerCompilerTestBound 2 5 0 := by native_decide

/-- compiler_p2_r7_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 7 2 + maximumLayerCompilerPrimeEnvelopeGap 2 7 2 = maximumLayerCompilerPrimeEnvelopeBound 2 7 2 ∧ maximumLayerCompilerTotalTests 2 7 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 7 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 7 2 ≤ maximumLayerCompilerTestBound 2 7 2 := by native_decide

/-- compiler_p2_r10_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 10 1 + maximumLayerCompilerPrimeEnvelopeGap 2 10 1 = maximumLayerCompilerPrimeEnvelopeBound 2 10 1 ∧ maximumLayerCompilerTotalTests 2 10 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 10 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 10 1 ≤ maximumLayerCompilerTestBound 2 10 1 := by native_decide

/-- compiler_p2_r13_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 13 0 + maximumLayerCompilerPrimeEnvelopeGap 2 13 0 = maximumLayerCompilerPrimeEnvelopeBound 2 13 0 ∧ maximumLayerCompilerTotalTests 2 13 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 13 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 13 0 ≤ maximumLayerCompilerTestBound 2 13 0 := by native_decide

/-- compiler_p2_r15_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 15 2 + maximumLayerCompilerPrimeEnvelopeGap 2 15 2 = maximumLayerCompilerPrimeEnvelopeBound 2 15 2 ∧ maximumLayerCompilerTotalTests 2 15 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 15 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 15 2 ≤ maximumLayerCompilerTestBound 2 15 2 := by native_decide

/-- compiler_p2_r18_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 18 1 + maximumLayerCompilerPrimeEnvelopeGap 2 18 1 = maximumLayerCompilerPrimeEnvelopeBound 2 18 1 ∧ maximumLayerCompilerTotalTests 2 18 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 18 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 18 1 ≤ maximumLayerCompilerTestBound 2 18 1 := by native_decide

/-- compiler_p3_r1_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 1 0 + maximumLayerCompilerPrimeEnvelopeGap 3 1 0 = maximumLayerCompilerPrimeEnvelopeBound 3 1 0 ∧ maximumLayerCompilerTotalTests 3 1 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 1 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 1 0 ≤ maximumLayerCompilerTestBound 3 1 0 := by native_decide

/-- compiler_p3_r3_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 3 2 + maximumLayerCompilerPrimeEnvelopeGap 3 3 2 = maximumLayerCompilerPrimeEnvelopeBound 3 3 2 ∧ maximumLayerCompilerTotalTests 3 3 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 3 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 3 2 ≤ maximumLayerCompilerTestBound 3 3 2 := by native_decide

/-- compiler_p3_r6_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 6 1 + maximumLayerCompilerPrimeEnvelopeGap 3 6 1 = maximumLayerCompilerPrimeEnvelopeBound 3 6 1 ∧ maximumLayerCompilerTotalTests 3 6 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 6 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 6 1 ≤ maximumLayerCompilerTestBound 3 6 1 := by native_decide

/-- compiler_p3_r9_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 9 0 + maximumLayerCompilerPrimeEnvelopeGap 3 9 0 = maximumLayerCompilerPrimeEnvelopeBound 3 9 0 ∧ maximumLayerCompilerTotalTests 3 9 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 9 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 9 0 ≤ maximumLayerCompilerTestBound 3 9 0 := by native_decide

/-- compiler_p3_r11_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 11 2 + maximumLayerCompilerPrimeEnvelopeGap 3 11 2 = maximumLayerCompilerPrimeEnvelopeBound 3 11 2 ∧ maximumLayerCompilerTotalTests 3 11 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 11 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 11 2 ≤ maximumLayerCompilerTestBound 3 11 2 := by native_decide

/-- compiler_p3_r14_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 14 1 + maximumLayerCompilerPrimeEnvelopeGap 3 14 1 = maximumLayerCompilerPrimeEnvelopeBound 3 14 1 ∧ maximumLayerCompilerTotalTests 3 14 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 14 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 14 1 ≤ maximumLayerCompilerTestBound 3 14 1 := by native_decide

/-- compiler_p3_r17_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 17 0 + maximumLayerCompilerPrimeEnvelopeGap 3 17 0 = maximumLayerCompilerPrimeEnvelopeBound 3 17 0 ∧ maximumLayerCompilerTotalTests 3 17 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 17 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 17 0 ≤ maximumLayerCompilerTestBound 3 17 0 := by native_decide

/-- compiler_p3_r19_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 19 2 + maximumLayerCompilerPrimeEnvelopeGap 3 19 2 = maximumLayerCompilerPrimeEnvelopeBound 3 19 2 ∧ maximumLayerCompilerTotalTests 3 19 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 19 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 19 2 ≤ maximumLayerCompilerTestBound 3 19 2 := by native_decide

/-- compiler_p5_r2_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 2 1 + maximumLayerCompilerPrimeEnvelopeGap 5 2 1 = maximumLayerCompilerPrimeEnvelopeBound 5 2 1 ∧ maximumLayerCompilerTotalTests 5 2 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 2 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 2 1 ≤ maximumLayerCompilerTestBound 5 2 1 := by native_decide

/-- compiler_p5_r5_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 5 0 + maximumLayerCompilerPrimeEnvelopeGap 5 5 0 = maximumLayerCompilerPrimeEnvelopeBound 5 5 0 ∧ maximumLayerCompilerTotalTests 5 5 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 5 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 5 0 ≤ maximumLayerCompilerTestBound 5 5 0 := by native_decide

/-- compiler_p5_r7_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 7 2 + maximumLayerCompilerPrimeEnvelopeGap 5 7 2 = maximumLayerCompilerPrimeEnvelopeBound 5 7 2 ∧ maximumLayerCompilerTotalTests 5 7 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 7 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 7 2 ≤ maximumLayerCompilerTestBound 5 7 2 := by native_decide

/-- compiler_p5_r10_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 10 1 + maximumLayerCompilerPrimeEnvelopeGap 5 10 1 = maximumLayerCompilerPrimeEnvelopeBound 5 10 1 ∧ maximumLayerCompilerTotalTests 5 10 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 10 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 10 1 ≤ maximumLayerCompilerTestBound 5 10 1 := by native_decide

/-- compiler_p5_r13_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 13 0 + maximumLayerCompilerPrimeEnvelopeGap 5 13 0 = maximumLayerCompilerPrimeEnvelopeBound 5 13 0 ∧ maximumLayerCompilerTotalTests 5 13 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 13 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 13 0 ≤ maximumLayerCompilerTestBound 5 13 0 := by native_decide

/-- compiler_p5_r15_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 15 2 + maximumLayerCompilerPrimeEnvelopeGap 5 15 2 = maximumLayerCompilerPrimeEnvelopeBound 5 15 2 ∧ maximumLayerCompilerTotalTests 5 15 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 15 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 15 2 ≤ maximumLayerCompilerTestBound 5 15 2 := by native_decide

/-- compiler_p5_r18_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 18 1 + maximumLayerCompilerPrimeEnvelopeGap 5 18 1 = maximumLayerCompilerPrimeEnvelopeBound 5 18 1 ∧ maximumLayerCompilerTotalTests 5 18 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 18 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 18 1 ≤ maximumLayerCompilerTestBound 5 18 1 := by native_decide

/-- compiler_p7_r1_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 1 0 + maximumLayerCompilerPrimeEnvelopeGap 7 1 0 = maximumLayerCompilerPrimeEnvelopeBound 7 1 0 ∧ maximumLayerCompilerTotalTests 7 1 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 1 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 1 0 ≤ maximumLayerCompilerTestBound 7 1 0 := by native_decide

/-- compiler_p7_r3_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 3 2 + maximumLayerCompilerPrimeEnvelopeGap 7 3 2 = maximumLayerCompilerPrimeEnvelopeBound 7 3 2 ∧ maximumLayerCompilerTotalTests 7 3 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 3 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 3 2 ≤ maximumLayerCompilerTestBound 7 3 2 := by native_decide

/-- compiler_p7_r6_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 6 1 + maximumLayerCompilerPrimeEnvelopeGap 7 6 1 = maximumLayerCompilerPrimeEnvelopeBound 7 6 1 ∧ maximumLayerCompilerTotalTests 7 6 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 6 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 6 1 ≤ maximumLayerCompilerTestBound 7 6 1 := by native_decide

/-- compiler_p7_r9_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 9 0 + maximumLayerCompilerPrimeEnvelopeGap 7 9 0 = maximumLayerCompilerPrimeEnvelopeBound 7 9 0 ∧ maximumLayerCompilerTotalTests 7 9 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 9 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 9 0 ≤ maximumLayerCompilerTestBound 7 9 0 := by native_decide

/-- compiler_p7_r11_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 11 2 + maximumLayerCompilerPrimeEnvelopeGap 7 11 2 = maximumLayerCompilerPrimeEnvelopeBound 7 11 2 ∧ maximumLayerCompilerTotalTests 7 11 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 11 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 11 2 ≤ maximumLayerCompilerTestBound 7 11 2 := by native_decide

/-- compiler_p7_r14_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 14 1 + maximumLayerCompilerPrimeEnvelopeGap 7 14 1 = maximumLayerCompilerPrimeEnvelopeBound 7 14 1 ∧ maximumLayerCompilerTotalTests 7 14 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 14 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 14 1 ≤ maximumLayerCompilerTestBound 7 14 1 := by native_decide

/-- compiler_p7_r17_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 17 0 + maximumLayerCompilerPrimeEnvelopeGap 7 17 0 = maximumLayerCompilerPrimeEnvelopeBound 7 17 0 ∧ maximumLayerCompilerTotalTests 7 17 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 17 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 17 0 ≤ maximumLayerCompilerTestBound 7 17 0 := by native_decide

/-- compiler_p7_r19_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 19 2 + maximumLayerCompilerPrimeEnvelopeGap 7 19 2 = maximumLayerCompilerPrimeEnvelopeBound 7 19 2 ∧ maximumLayerCompilerTotalTests 7 19 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 19 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 19 2 ≤ maximumLayerCompilerTestBound 7 19 2 := by native_decide

/-- compiler_p11_r2_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 2 1 + maximumLayerCompilerPrimeEnvelopeGap 11 2 1 = maximumLayerCompilerPrimeEnvelopeBound 11 2 1 ∧ maximumLayerCompilerTotalTests 11 2 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 2 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 2 1 ≤ maximumLayerCompilerTestBound 11 2 1 := by native_decide

/-- compiler_p11_r5_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 5 0 + maximumLayerCompilerPrimeEnvelopeGap 11 5 0 = maximumLayerCompilerPrimeEnvelopeBound 11 5 0 ∧ maximumLayerCompilerTotalTests 11 5 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 5 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 5 0 ≤ maximumLayerCompilerTestBound 11 5 0 := by native_decide

/-- compiler_p11_r7_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 7 2 + maximumLayerCompilerPrimeEnvelopeGap 11 7 2 = maximumLayerCompilerPrimeEnvelopeBound 11 7 2 ∧ maximumLayerCompilerTotalTests 11 7 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 7 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 7 2 ≤ maximumLayerCompilerTestBound 11 7 2 := by native_decide

/-- compiler_p11_r10_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 10 1 + maximumLayerCompilerPrimeEnvelopeGap 11 10 1 = maximumLayerCompilerPrimeEnvelopeBound 11 10 1 ∧ maximumLayerCompilerTotalTests 11 10 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 10 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 10 1 ≤ maximumLayerCompilerTestBound 11 10 1 := by native_decide

/-- compiler_p11_r13_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 13 0 + maximumLayerCompilerPrimeEnvelopeGap 11 13 0 = maximumLayerCompilerPrimeEnvelopeBound 11 13 0 ∧ maximumLayerCompilerTotalTests 11 13 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 13 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 13 0 ≤ maximumLayerCompilerTestBound 11 13 0 := by native_decide

/-- compiler_p11_r15_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 15 2 + maximumLayerCompilerPrimeEnvelopeGap 11 15 2 = maximumLayerCompilerPrimeEnvelopeBound 11 15 2 ∧ maximumLayerCompilerTotalTests 11 15 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 15 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 15 2 ≤ maximumLayerCompilerTestBound 11 15 2 := by native_decide

/-- compiler_p11_r18_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 18 1 + maximumLayerCompilerPrimeEnvelopeGap 11 18 1 = maximumLayerCompilerPrimeEnvelopeBound 11 18 1 ∧ maximumLayerCompilerTotalTests 11 18 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 18 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 18 1 ≤ maximumLayerCompilerTestBound 11 18 1 := by native_decide

/-- compiler_p13_r1_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 1 0 + maximumLayerCompilerPrimeEnvelopeGap 13 1 0 = maximumLayerCompilerPrimeEnvelopeBound 13 1 0 ∧ maximumLayerCompilerTotalTests 13 1 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 1 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 1 0 ≤ maximumLayerCompilerTestBound 13 1 0 := by native_decide

/-- compiler_p13_r3_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 3 2 + maximumLayerCompilerPrimeEnvelopeGap 13 3 2 = maximumLayerCompilerPrimeEnvelopeBound 13 3 2 ∧ maximumLayerCompilerTotalTests 13 3 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 3 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 3 2 ≤ maximumLayerCompilerTestBound 13 3 2 := by native_decide

/-- compiler_p13_r6_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 6 1 + maximumLayerCompilerPrimeEnvelopeGap 13 6 1 = maximumLayerCompilerPrimeEnvelopeBound 13 6 1 ∧ maximumLayerCompilerTotalTests 13 6 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 6 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 6 1 ≤ maximumLayerCompilerTestBound 13 6 1 := by native_decide

/-- compiler_p13_r9_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 9 0 + maximumLayerCompilerPrimeEnvelopeGap 13 9 0 = maximumLayerCompilerPrimeEnvelopeBound 13 9 0 ∧ maximumLayerCompilerTotalTests 13 9 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 9 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 9 0 ≤ maximumLayerCompilerTestBound 13 9 0 := by native_decide

/-- compiler_p13_r11_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 11 2 + maximumLayerCompilerPrimeEnvelopeGap 13 11 2 = maximumLayerCompilerPrimeEnvelopeBound 13 11 2 ∧ maximumLayerCompilerTotalTests 13 11 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 11 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 11 2 ≤ maximumLayerCompilerTestBound 13 11 2 := by native_decide

/-- compiler_p13_r14_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 14 1 + maximumLayerCompilerPrimeEnvelopeGap 13 14 1 = maximumLayerCompilerPrimeEnvelopeBound 13 14 1 ∧ maximumLayerCompilerTotalTests 13 14 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 14 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 14 1 ≤ maximumLayerCompilerTestBound 13 14 1 := by native_decide

/-- compiler_p13_r17_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 17 0 + maximumLayerCompilerPrimeEnvelopeGap 13 17 0 = maximumLayerCompilerPrimeEnvelopeBound 13 17 0 ∧ maximumLayerCompilerTotalTests 13 17 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 17 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 17 0 ≤ maximumLayerCompilerTestBound 13 17 0 := by native_decide

/-- compiler_p13_r19_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 19 2 + maximumLayerCompilerPrimeEnvelopeGap 13 19 2 = maximumLayerCompilerPrimeEnvelopeBound 13 19 2 ∧ maximumLayerCompilerTotalTests 13 19 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 19 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 19 2 ≤ maximumLayerCompilerTestBound 13 19 2 := by native_decide

end KomorebiPadic
