import KomorebiPadic

namespace KomorebiPadic

/-- representative_p1_B6 -/
example : radixRepresentativeBudget 1 6 + radixRepresentativeBudgetPrimeEnvelopeGap 1 6 = radixRepresentativeBudgetPrimeEnvelope 1 6 ∧ radixRepresentativeBudget 1 6 ≤ radixRepresentativeBudgetPrimeEnvelope 1 6 ∧ (radixRepresentativeBudget 1 6 = radixRepresentativeBudgetPrimeEnvelope 1 6 ↔ lastRadixBlockQuotient 1 6 = 0 ∨ lastRadixBlockRemainder 1 6 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 6 ≤ 6 * 6 := by native_decide

/-- representative_p1_B14 -/
example : radixRepresentativeBudget 1 14 + radixRepresentativeBudgetPrimeEnvelopeGap 1 14 = radixRepresentativeBudgetPrimeEnvelope 1 14 ∧ radixRepresentativeBudget 1 14 ≤ radixRepresentativeBudgetPrimeEnvelope 1 14 ∧ (radixRepresentativeBudget 1 14 = radixRepresentativeBudgetPrimeEnvelope 1 14 ↔ lastRadixBlockQuotient 1 14 = 0 ∨ lastRadixBlockRemainder 1 14 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 14 ≤ 14 * 14 := by native_decide

/-- representative_p1_B22 -/
example : radixRepresentativeBudget 1 22 + radixRepresentativeBudgetPrimeEnvelopeGap 1 22 = radixRepresentativeBudgetPrimeEnvelope 1 22 ∧ radixRepresentativeBudget 1 22 ≤ radixRepresentativeBudgetPrimeEnvelope 1 22 ∧ (radixRepresentativeBudget 1 22 = radixRepresentativeBudgetPrimeEnvelope 1 22 ↔ lastRadixBlockQuotient 1 22 = 0 ∨ lastRadixBlockRemainder 1 22 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 22 ≤ 22 * 22 := by native_decide

/-- representative_p1_B30 -/
example : radixRepresentativeBudget 1 30 + radixRepresentativeBudgetPrimeEnvelopeGap 1 30 = radixRepresentativeBudgetPrimeEnvelope 1 30 ∧ radixRepresentativeBudget 1 30 ≤ radixRepresentativeBudgetPrimeEnvelope 1 30 ∧ (radixRepresentativeBudget 1 30 = radixRepresentativeBudgetPrimeEnvelope 1 30 ↔ lastRadixBlockQuotient 1 30 = 0 ∨ lastRadixBlockRemainder 1 30 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 30 ≤ 30 * 30 := by native_decide

/-- representative_p1_B38 -/
example : radixRepresentativeBudget 1 38 + radixRepresentativeBudgetPrimeEnvelopeGap 1 38 = radixRepresentativeBudgetPrimeEnvelope 1 38 ∧ radixRepresentativeBudget 1 38 ≤ radixRepresentativeBudgetPrimeEnvelope 1 38 ∧ (radixRepresentativeBudget 1 38 = radixRepresentativeBudgetPrimeEnvelope 1 38 ↔ lastRadixBlockQuotient 1 38 = 0 ∨ lastRadixBlockRemainder 1 38 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 38 ≤ 38 * 38 := by native_decide

/-- representative_p1_B46 -/
example : radixRepresentativeBudget 1 46 + radixRepresentativeBudgetPrimeEnvelopeGap 1 46 = radixRepresentativeBudgetPrimeEnvelope 1 46 ∧ radixRepresentativeBudget 1 46 ≤ radixRepresentativeBudgetPrimeEnvelope 1 46 ∧ (radixRepresentativeBudget 1 46 = radixRepresentativeBudgetPrimeEnvelope 1 46 ↔ lastRadixBlockQuotient 1 46 = 0 ∨ lastRadixBlockRemainder 1 46 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 46 ≤ 46 * 46 := by native_decide

/-- representative_p2_B4 -/
example : radixRepresentativeBudget 2 4 + radixRepresentativeBudgetPrimeEnvelopeGap 2 4 = radixRepresentativeBudgetPrimeEnvelope 2 4 ∧ radixRepresentativeBudget 2 4 ≤ radixRepresentativeBudgetPrimeEnvelope 2 4 ∧ (radixRepresentativeBudget 2 4 = radixRepresentativeBudgetPrimeEnvelope 2 4 ↔ lastRadixBlockQuotient 2 4 = 0 ∨ lastRadixBlockRemainder 2 4 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 4 ≤ 4 * 4 := by native_decide

/-- representative_p2_B12 -/
example : radixRepresentativeBudget 2 12 + radixRepresentativeBudgetPrimeEnvelopeGap 2 12 = radixRepresentativeBudgetPrimeEnvelope 2 12 ∧ radixRepresentativeBudget 2 12 ≤ radixRepresentativeBudgetPrimeEnvelope 2 12 ∧ (radixRepresentativeBudget 2 12 = radixRepresentativeBudgetPrimeEnvelope 2 12 ↔ lastRadixBlockQuotient 2 12 = 0 ∨ lastRadixBlockRemainder 2 12 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 12 ≤ 12 * 12 := by native_decide

/-- representative_p2_B20 -/
example : radixRepresentativeBudget 2 20 + radixRepresentativeBudgetPrimeEnvelopeGap 2 20 = radixRepresentativeBudgetPrimeEnvelope 2 20 ∧ radixRepresentativeBudget 2 20 ≤ radixRepresentativeBudgetPrimeEnvelope 2 20 ∧ (radixRepresentativeBudget 2 20 = radixRepresentativeBudgetPrimeEnvelope 2 20 ↔ lastRadixBlockQuotient 2 20 = 0 ∨ lastRadixBlockRemainder 2 20 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 20 ≤ 20 * 20 := by native_decide

/-- representative_p2_B28 -/
example : radixRepresentativeBudget 2 28 + radixRepresentativeBudgetPrimeEnvelopeGap 2 28 = radixRepresentativeBudgetPrimeEnvelope 2 28 ∧ radixRepresentativeBudget 2 28 ≤ radixRepresentativeBudgetPrimeEnvelope 2 28 ∧ (radixRepresentativeBudget 2 28 = radixRepresentativeBudgetPrimeEnvelope 2 28 ↔ lastRadixBlockQuotient 2 28 = 0 ∨ lastRadixBlockRemainder 2 28 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 28 ≤ 28 * 28 := by native_decide

/-- representative_p2_B36 -/
example : radixRepresentativeBudget 2 36 + radixRepresentativeBudgetPrimeEnvelopeGap 2 36 = radixRepresentativeBudgetPrimeEnvelope 2 36 ∧ radixRepresentativeBudget 2 36 ≤ radixRepresentativeBudgetPrimeEnvelope 2 36 ∧ (radixRepresentativeBudget 2 36 = radixRepresentativeBudgetPrimeEnvelope 2 36 ↔ lastRadixBlockQuotient 2 36 = 0 ∨ lastRadixBlockRemainder 2 36 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 36 ≤ 36 * 36 := by native_decide

/-- representative_p2_B44 -/
example : radixRepresentativeBudget 2 44 + radixRepresentativeBudgetPrimeEnvelopeGap 2 44 = radixRepresentativeBudgetPrimeEnvelope 2 44 ∧ radixRepresentativeBudget 2 44 ≤ radixRepresentativeBudgetPrimeEnvelope 2 44 ∧ (radixRepresentativeBudget 2 44 = radixRepresentativeBudgetPrimeEnvelope 2 44 ↔ lastRadixBlockQuotient 2 44 = 0 ∨ lastRadixBlockRemainder 2 44 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 44 ≤ 44 * 44 := by native_decide

/-- representative_p3_B2 -/
example : radixRepresentativeBudget 3 2 + radixRepresentativeBudgetPrimeEnvelopeGap 3 2 = radixRepresentativeBudgetPrimeEnvelope 3 2 ∧ radixRepresentativeBudget 3 2 ≤ radixRepresentativeBudgetPrimeEnvelope 3 2 ∧ (radixRepresentativeBudget 3 2 = radixRepresentativeBudgetPrimeEnvelope 3 2 ↔ lastRadixBlockQuotient 3 2 = 0 ∨ lastRadixBlockRemainder 3 2 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 2 ≤ 2 * 2 := by native_decide

/-- representative_p3_B10 -/
example : radixRepresentativeBudget 3 10 + radixRepresentativeBudgetPrimeEnvelopeGap 3 10 = radixRepresentativeBudgetPrimeEnvelope 3 10 ∧ radixRepresentativeBudget 3 10 ≤ radixRepresentativeBudgetPrimeEnvelope 3 10 ∧ (radixRepresentativeBudget 3 10 = radixRepresentativeBudgetPrimeEnvelope 3 10 ↔ lastRadixBlockQuotient 3 10 = 0 ∨ lastRadixBlockRemainder 3 10 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 10 ≤ 10 * 10 := by native_decide

/-- representative_p3_B18 -/
example : radixRepresentativeBudget 3 18 + radixRepresentativeBudgetPrimeEnvelopeGap 3 18 = radixRepresentativeBudgetPrimeEnvelope 3 18 ∧ radixRepresentativeBudget 3 18 ≤ radixRepresentativeBudgetPrimeEnvelope 3 18 ∧ (radixRepresentativeBudget 3 18 = radixRepresentativeBudgetPrimeEnvelope 3 18 ↔ lastRadixBlockQuotient 3 18 = 0 ∨ lastRadixBlockRemainder 3 18 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 18 ≤ 18 * 18 := by native_decide

/-- representative_p3_B26 -/
example : radixRepresentativeBudget 3 26 + radixRepresentativeBudgetPrimeEnvelopeGap 3 26 = radixRepresentativeBudgetPrimeEnvelope 3 26 ∧ radixRepresentativeBudget 3 26 ≤ radixRepresentativeBudgetPrimeEnvelope 3 26 ∧ (radixRepresentativeBudget 3 26 = radixRepresentativeBudgetPrimeEnvelope 3 26 ↔ lastRadixBlockQuotient 3 26 = 0 ∨ lastRadixBlockRemainder 3 26 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 26 ≤ 26 * 26 := by native_decide

/-- representative_p3_B34 -/
example : radixRepresentativeBudget 3 34 + radixRepresentativeBudgetPrimeEnvelopeGap 3 34 = radixRepresentativeBudgetPrimeEnvelope 3 34 ∧ radixRepresentativeBudget 3 34 ≤ radixRepresentativeBudgetPrimeEnvelope 3 34 ∧ (radixRepresentativeBudget 3 34 = radixRepresentativeBudgetPrimeEnvelope 3 34 ↔ lastRadixBlockQuotient 3 34 = 0 ∨ lastRadixBlockRemainder 3 34 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 34 ≤ 34 * 34 := by native_decide

/-- representative_p3_B42 -/
example : radixRepresentativeBudget 3 42 + radixRepresentativeBudgetPrimeEnvelopeGap 3 42 = radixRepresentativeBudgetPrimeEnvelope 3 42 ∧ radixRepresentativeBudget 3 42 ≤ radixRepresentativeBudgetPrimeEnvelope 3 42 ∧ (radixRepresentativeBudget 3 42 = radixRepresentativeBudgetPrimeEnvelope 3 42 ↔ lastRadixBlockQuotient 3 42 = 0 ∨ lastRadixBlockRemainder 3 42 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 42 ≤ 42 * 42 := by native_decide

/-- representative_p4_B0 -/
example : radixRepresentativeBudget 4 0 + radixRepresentativeBudgetPrimeEnvelopeGap 4 0 = radixRepresentativeBudgetPrimeEnvelope 4 0 ∧ radixRepresentativeBudget 4 0 ≤ radixRepresentativeBudgetPrimeEnvelope 4 0 ∧ (radixRepresentativeBudget 4 0 = radixRepresentativeBudgetPrimeEnvelope 4 0 ↔ lastRadixBlockQuotient 4 0 = 0 ∨ lastRadixBlockRemainder 4 0 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 0 ≤ 0 * 0 := by native_decide

/-- representative_p4_B8 -/
example : radixRepresentativeBudget 4 8 + radixRepresentativeBudgetPrimeEnvelopeGap 4 8 = radixRepresentativeBudgetPrimeEnvelope 4 8 ∧ radixRepresentativeBudget 4 8 ≤ radixRepresentativeBudgetPrimeEnvelope 4 8 ∧ (radixRepresentativeBudget 4 8 = radixRepresentativeBudgetPrimeEnvelope 4 8 ↔ lastRadixBlockQuotient 4 8 = 0 ∨ lastRadixBlockRemainder 4 8 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 8 ≤ 8 * 8 := by native_decide

/-- representative_p4_B16 -/
example : radixRepresentativeBudget 4 16 + radixRepresentativeBudgetPrimeEnvelopeGap 4 16 = radixRepresentativeBudgetPrimeEnvelope 4 16 ∧ radixRepresentativeBudget 4 16 ≤ radixRepresentativeBudgetPrimeEnvelope 4 16 ∧ (radixRepresentativeBudget 4 16 = radixRepresentativeBudgetPrimeEnvelope 4 16 ↔ lastRadixBlockQuotient 4 16 = 0 ∨ lastRadixBlockRemainder 4 16 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 16 ≤ 16 * 16 := by native_decide

/-- representative_p4_B24 -/
example : radixRepresentativeBudget 4 24 + radixRepresentativeBudgetPrimeEnvelopeGap 4 24 = radixRepresentativeBudgetPrimeEnvelope 4 24 ∧ radixRepresentativeBudget 4 24 ≤ radixRepresentativeBudgetPrimeEnvelope 4 24 ∧ (radixRepresentativeBudget 4 24 = radixRepresentativeBudgetPrimeEnvelope 4 24 ↔ lastRadixBlockQuotient 4 24 = 0 ∨ lastRadixBlockRemainder 4 24 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 24 ≤ 24 * 24 := by native_decide

/-- representative_p4_B32 -/
example : radixRepresentativeBudget 4 32 + radixRepresentativeBudgetPrimeEnvelopeGap 4 32 = radixRepresentativeBudgetPrimeEnvelope 4 32 ∧ radixRepresentativeBudget 4 32 ≤ radixRepresentativeBudgetPrimeEnvelope 4 32 ∧ (radixRepresentativeBudget 4 32 = radixRepresentativeBudgetPrimeEnvelope 4 32 ↔ lastRadixBlockQuotient 4 32 = 0 ∨ lastRadixBlockRemainder 4 32 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 32 ≤ 32 * 32 := by native_decide

/-- representative_p4_B40 -/
example : radixRepresentativeBudget 4 40 + radixRepresentativeBudgetPrimeEnvelopeGap 4 40 = radixRepresentativeBudgetPrimeEnvelope 4 40 ∧ radixRepresentativeBudget 4 40 ≤ radixRepresentativeBudgetPrimeEnvelope 4 40 ∧ (radixRepresentativeBudget 4 40 = radixRepresentativeBudgetPrimeEnvelope 4 40 ↔ lastRadixBlockQuotient 4 40 = 0 ∨ lastRadixBlockRemainder 4 40 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 40 ≤ 40 * 40 := by native_decide

/-- representative_p4_B48 -/
example : radixRepresentativeBudget 4 48 + radixRepresentativeBudgetPrimeEnvelopeGap 4 48 = radixRepresentativeBudgetPrimeEnvelope 4 48 ∧ radixRepresentativeBudget 4 48 ≤ radixRepresentativeBudgetPrimeEnvelope 4 48 ∧ (radixRepresentativeBudget 4 48 = radixRepresentativeBudgetPrimeEnvelope 4 48 ↔ lastRadixBlockQuotient 4 48 = 0 ∨ lastRadixBlockRemainder 4 48 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 48 ≤ 48 * 48 := by native_decide

/-- representative_p5_B6 -/
example : radixRepresentativeBudget 5 6 + radixRepresentativeBudgetPrimeEnvelopeGap 5 6 = radixRepresentativeBudgetPrimeEnvelope 5 6 ∧ radixRepresentativeBudget 5 6 ≤ radixRepresentativeBudgetPrimeEnvelope 5 6 ∧ (radixRepresentativeBudget 5 6 = radixRepresentativeBudgetPrimeEnvelope 5 6 ↔ lastRadixBlockQuotient 5 6 = 0 ∨ lastRadixBlockRemainder 5 6 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 6 ≤ 6 * 6 := by native_decide

/-- representative_p5_B14 -/
example : radixRepresentativeBudget 5 14 + radixRepresentativeBudgetPrimeEnvelopeGap 5 14 = radixRepresentativeBudgetPrimeEnvelope 5 14 ∧ radixRepresentativeBudget 5 14 ≤ radixRepresentativeBudgetPrimeEnvelope 5 14 ∧ (radixRepresentativeBudget 5 14 = radixRepresentativeBudgetPrimeEnvelope 5 14 ↔ lastRadixBlockQuotient 5 14 = 0 ∨ lastRadixBlockRemainder 5 14 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 14 ≤ 14 * 14 := by native_decide

/-- representative_p5_B22 -/
example : radixRepresentativeBudget 5 22 + radixRepresentativeBudgetPrimeEnvelopeGap 5 22 = radixRepresentativeBudgetPrimeEnvelope 5 22 ∧ radixRepresentativeBudget 5 22 ≤ radixRepresentativeBudgetPrimeEnvelope 5 22 ∧ (radixRepresentativeBudget 5 22 = radixRepresentativeBudgetPrimeEnvelope 5 22 ↔ lastRadixBlockQuotient 5 22 = 0 ∨ lastRadixBlockRemainder 5 22 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 22 ≤ 22 * 22 := by native_decide

/-- representative_p5_B30 -/
example : radixRepresentativeBudget 5 30 + radixRepresentativeBudgetPrimeEnvelopeGap 5 30 = radixRepresentativeBudgetPrimeEnvelope 5 30 ∧ radixRepresentativeBudget 5 30 ≤ radixRepresentativeBudgetPrimeEnvelope 5 30 ∧ (radixRepresentativeBudget 5 30 = radixRepresentativeBudgetPrimeEnvelope 5 30 ↔ lastRadixBlockQuotient 5 30 = 0 ∨ lastRadixBlockRemainder 5 30 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 30 ≤ 30 * 30 := by native_decide

/-- representative_p5_B38 -/
example : radixRepresentativeBudget 5 38 + radixRepresentativeBudgetPrimeEnvelopeGap 5 38 = radixRepresentativeBudgetPrimeEnvelope 5 38 ∧ radixRepresentativeBudget 5 38 ≤ radixRepresentativeBudgetPrimeEnvelope 5 38 ∧ (radixRepresentativeBudget 5 38 = radixRepresentativeBudgetPrimeEnvelope 5 38 ↔ lastRadixBlockQuotient 5 38 = 0 ∨ lastRadixBlockRemainder 5 38 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 38 ≤ 38 * 38 := by native_decide

/-- representative_p5_B46 -/
example : radixRepresentativeBudget 5 46 + radixRepresentativeBudgetPrimeEnvelopeGap 5 46 = radixRepresentativeBudgetPrimeEnvelope 5 46 ∧ radixRepresentativeBudget 5 46 ≤ radixRepresentativeBudgetPrimeEnvelope 5 46 ∧ (radixRepresentativeBudget 5 46 = radixRepresentativeBudgetPrimeEnvelope 5 46 ↔ lastRadixBlockQuotient 5 46 = 0 ∨ lastRadixBlockRemainder 5 46 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 46 ≤ 46 * 46 := by native_decide

/-- representative_p6_B4 -/
example : radixRepresentativeBudget 6 4 + radixRepresentativeBudgetPrimeEnvelopeGap 6 4 = radixRepresentativeBudgetPrimeEnvelope 6 4 ∧ radixRepresentativeBudget 6 4 ≤ radixRepresentativeBudgetPrimeEnvelope 6 4 ∧ (radixRepresentativeBudget 6 4 = radixRepresentativeBudgetPrimeEnvelope 6 4 ↔ lastRadixBlockQuotient 6 4 = 0 ∨ lastRadixBlockRemainder 6 4 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 4 ≤ 4 * 4 := by native_decide

/-- representative_p6_B12 -/
example : radixRepresentativeBudget 6 12 + radixRepresentativeBudgetPrimeEnvelopeGap 6 12 = radixRepresentativeBudgetPrimeEnvelope 6 12 ∧ radixRepresentativeBudget 6 12 ≤ radixRepresentativeBudgetPrimeEnvelope 6 12 ∧ (radixRepresentativeBudget 6 12 = radixRepresentativeBudgetPrimeEnvelope 6 12 ↔ lastRadixBlockQuotient 6 12 = 0 ∨ lastRadixBlockRemainder 6 12 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 12 ≤ 12 * 12 := by native_decide

/-- representative_p6_B20 -/
example : radixRepresentativeBudget 6 20 + radixRepresentativeBudgetPrimeEnvelopeGap 6 20 = radixRepresentativeBudgetPrimeEnvelope 6 20 ∧ radixRepresentativeBudget 6 20 ≤ radixRepresentativeBudgetPrimeEnvelope 6 20 ∧ (radixRepresentativeBudget 6 20 = radixRepresentativeBudgetPrimeEnvelope 6 20 ↔ lastRadixBlockQuotient 6 20 = 0 ∨ lastRadixBlockRemainder 6 20 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 20 ≤ 20 * 20 := by native_decide

/-- representative_p6_B28 -/
example : radixRepresentativeBudget 6 28 + radixRepresentativeBudgetPrimeEnvelopeGap 6 28 = radixRepresentativeBudgetPrimeEnvelope 6 28 ∧ radixRepresentativeBudget 6 28 ≤ radixRepresentativeBudgetPrimeEnvelope 6 28 ∧ (radixRepresentativeBudget 6 28 = radixRepresentativeBudgetPrimeEnvelope 6 28 ↔ lastRadixBlockQuotient 6 28 = 0 ∨ lastRadixBlockRemainder 6 28 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 28 ≤ 28 * 28 := by native_decide

/-- representative_p6_B36 -/
example : radixRepresentativeBudget 6 36 + radixRepresentativeBudgetPrimeEnvelopeGap 6 36 = radixRepresentativeBudgetPrimeEnvelope 6 36 ∧ radixRepresentativeBudget 6 36 ≤ radixRepresentativeBudgetPrimeEnvelope 6 36 ∧ (radixRepresentativeBudget 6 36 = radixRepresentativeBudgetPrimeEnvelope 6 36 ↔ lastRadixBlockQuotient 6 36 = 0 ∨ lastRadixBlockRemainder 6 36 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 36 ≤ 36 * 36 := by native_decide

/-- representative_p6_B44 -/
example : radixRepresentativeBudget 6 44 + radixRepresentativeBudgetPrimeEnvelopeGap 6 44 = radixRepresentativeBudgetPrimeEnvelope 6 44 ∧ radixRepresentativeBudget 6 44 ≤ radixRepresentativeBudgetPrimeEnvelope 6 44 ∧ (radixRepresentativeBudget 6 44 = radixRepresentativeBudgetPrimeEnvelope 6 44 ↔ lastRadixBlockQuotient 6 44 = 0 ∨ lastRadixBlockRemainder 6 44 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 44 ≤ 44 * 44 := by native_decide

/-- representative_p7_B2 -/
example : radixRepresentativeBudget 7 2 + radixRepresentativeBudgetPrimeEnvelopeGap 7 2 = radixRepresentativeBudgetPrimeEnvelope 7 2 ∧ radixRepresentativeBudget 7 2 ≤ radixRepresentativeBudgetPrimeEnvelope 7 2 ∧ (radixRepresentativeBudget 7 2 = radixRepresentativeBudgetPrimeEnvelope 7 2 ↔ lastRadixBlockQuotient 7 2 = 0 ∨ lastRadixBlockRemainder 7 2 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 2 ≤ 2 * 2 := by native_decide

/-- representative_p7_B10 -/
example : radixRepresentativeBudget 7 10 + radixRepresentativeBudgetPrimeEnvelopeGap 7 10 = radixRepresentativeBudgetPrimeEnvelope 7 10 ∧ radixRepresentativeBudget 7 10 ≤ radixRepresentativeBudgetPrimeEnvelope 7 10 ∧ (radixRepresentativeBudget 7 10 = radixRepresentativeBudgetPrimeEnvelope 7 10 ↔ lastRadixBlockQuotient 7 10 = 0 ∨ lastRadixBlockRemainder 7 10 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 10 ≤ 10 * 10 := by native_decide

/-- representative_p7_B18 -/
example : radixRepresentativeBudget 7 18 + radixRepresentativeBudgetPrimeEnvelopeGap 7 18 = radixRepresentativeBudgetPrimeEnvelope 7 18 ∧ radixRepresentativeBudget 7 18 ≤ radixRepresentativeBudgetPrimeEnvelope 7 18 ∧ (radixRepresentativeBudget 7 18 = radixRepresentativeBudgetPrimeEnvelope 7 18 ↔ lastRadixBlockQuotient 7 18 = 0 ∨ lastRadixBlockRemainder 7 18 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 18 ≤ 18 * 18 := by native_decide

/-- representative_p7_B26 -/
example : radixRepresentativeBudget 7 26 + radixRepresentativeBudgetPrimeEnvelopeGap 7 26 = radixRepresentativeBudgetPrimeEnvelope 7 26 ∧ radixRepresentativeBudget 7 26 ≤ radixRepresentativeBudgetPrimeEnvelope 7 26 ∧ (radixRepresentativeBudget 7 26 = radixRepresentativeBudgetPrimeEnvelope 7 26 ↔ lastRadixBlockQuotient 7 26 = 0 ∨ lastRadixBlockRemainder 7 26 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 26 ≤ 26 * 26 := by native_decide

/-- representative_p7_B34 -/
example : radixRepresentativeBudget 7 34 + radixRepresentativeBudgetPrimeEnvelopeGap 7 34 = radixRepresentativeBudgetPrimeEnvelope 7 34 ∧ radixRepresentativeBudget 7 34 ≤ radixRepresentativeBudgetPrimeEnvelope 7 34 ∧ (radixRepresentativeBudget 7 34 = radixRepresentativeBudgetPrimeEnvelope 7 34 ↔ lastRadixBlockQuotient 7 34 = 0 ∨ lastRadixBlockRemainder 7 34 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 34 ≤ 34 * 34 := by native_decide

/-- representative_p7_B42 -/
example : radixRepresentativeBudget 7 42 + radixRepresentativeBudgetPrimeEnvelopeGap 7 42 = radixRepresentativeBudgetPrimeEnvelope 7 42 ∧ radixRepresentativeBudget 7 42 ≤ radixRepresentativeBudgetPrimeEnvelope 7 42 ∧ (radixRepresentativeBudget 7 42 = radixRepresentativeBudgetPrimeEnvelope 7 42 ↔ lastRadixBlockQuotient 7 42 = 0 ∨ lastRadixBlockRemainder 7 42 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 42 ≤ 42 * 42 := by native_decide

/-- representative_p8_B0 -/
example : radixRepresentativeBudget 8 0 + radixRepresentativeBudgetPrimeEnvelopeGap 8 0 = radixRepresentativeBudgetPrimeEnvelope 8 0 ∧ radixRepresentativeBudget 8 0 ≤ radixRepresentativeBudgetPrimeEnvelope 8 0 ∧ (radixRepresentativeBudget 8 0 = radixRepresentativeBudgetPrimeEnvelope 8 0 ↔ lastRadixBlockQuotient 8 0 = 0 ∨ lastRadixBlockRemainder 8 0 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 0 ≤ 0 * 0 := by native_decide

/-- representative_p8_B8 -/
example : radixRepresentativeBudget 8 8 + radixRepresentativeBudgetPrimeEnvelopeGap 8 8 = radixRepresentativeBudgetPrimeEnvelope 8 8 ∧ radixRepresentativeBudget 8 8 ≤ radixRepresentativeBudgetPrimeEnvelope 8 8 ∧ (radixRepresentativeBudget 8 8 = radixRepresentativeBudgetPrimeEnvelope 8 8 ↔ lastRadixBlockQuotient 8 8 = 0 ∨ lastRadixBlockRemainder 8 8 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 8 ≤ 8 * 8 := by native_decide

/-- representative_p8_B16 -/
example : radixRepresentativeBudget 8 16 + radixRepresentativeBudgetPrimeEnvelopeGap 8 16 = radixRepresentativeBudgetPrimeEnvelope 8 16 ∧ radixRepresentativeBudget 8 16 ≤ radixRepresentativeBudgetPrimeEnvelope 8 16 ∧ (radixRepresentativeBudget 8 16 = radixRepresentativeBudgetPrimeEnvelope 8 16 ↔ lastRadixBlockQuotient 8 16 = 0 ∨ lastRadixBlockRemainder 8 16 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 16 ≤ 16 * 16 := by native_decide

/-- representative_p8_B24 -/
example : radixRepresentativeBudget 8 24 + radixRepresentativeBudgetPrimeEnvelopeGap 8 24 = radixRepresentativeBudgetPrimeEnvelope 8 24 ∧ radixRepresentativeBudget 8 24 ≤ radixRepresentativeBudgetPrimeEnvelope 8 24 ∧ (radixRepresentativeBudget 8 24 = radixRepresentativeBudgetPrimeEnvelope 8 24 ↔ lastRadixBlockQuotient 8 24 = 0 ∨ lastRadixBlockRemainder 8 24 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 24 ≤ 24 * 24 := by native_decide

/-- representative_p8_B32 -/
example : radixRepresentativeBudget 8 32 + radixRepresentativeBudgetPrimeEnvelopeGap 8 32 = radixRepresentativeBudgetPrimeEnvelope 8 32 ∧ radixRepresentativeBudget 8 32 ≤ radixRepresentativeBudgetPrimeEnvelope 8 32 ∧ (radixRepresentativeBudget 8 32 = radixRepresentativeBudgetPrimeEnvelope 8 32 ↔ lastRadixBlockQuotient 8 32 = 0 ∨ lastRadixBlockRemainder 8 32 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 32 ≤ 32 * 32 := by native_decide

/-- representative_p8_B40 -/
example : radixRepresentativeBudget 8 40 + radixRepresentativeBudgetPrimeEnvelopeGap 8 40 = radixRepresentativeBudgetPrimeEnvelope 8 40 ∧ radixRepresentativeBudget 8 40 ≤ radixRepresentativeBudgetPrimeEnvelope 8 40 ∧ (radixRepresentativeBudget 8 40 = radixRepresentativeBudgetPrimeEnvelope 8 40 ↔ lastRadixBlockQuotient 8 40 = 0 ∨ lastRadixBlockRemainder 8 40 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 40 ≤ 40 * 40 := by native_decide

/-- representative_p8_B48 -/
example : radixRepresentativeBudget 8 48 + radixRepresentativeBudgetPrimeEnvelopeGap 8 48 = radixRepresentativeBudgetPrimeEnvelope 8 48 ∧ radixRepresentativeBudget 8 48 ≤ radixRepresentativeBudgetPrimeEnvelope 8 48 ∧ (radixRepresentativeBudget 8 48 = radixRepresentativeBudgetPrimeEnvelope 8 48 ↔ lastRadixBlockQuotient 8 48 = 0 ∨ lastRadixBlockRemainder 8 48 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 48 ≤ 48 * 48 := by native_decide

/-- representative_p9_B6 -/
example : radixRepresentativeBudget 9 6 + radixRepresentativeBudgetPrimeEnvelopeGap 9 6 = radixRepresentativeBudgetPrimeEnvelope 9 6 ∧ radixRepresentativeBudget 9 6 ≤ radixRepresentativeBudgetPrimeEnvelope 9 6 ∧ (radixRepresentativeBudget 9 6 = radixRepresentativeBudgetPrimeEnvelope 9 6 ↔ lastRadixBlockQuotient 9 6 = 0 ∨ lastRadixBlockRemainder 9 6 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 6 ≤ 6 * 6 := by native_decide

/-- representative_p9_B14 -/
example : radixRepresentativeBudget 9 14 + radixRepresentativeBudgetPrimeEnvelopeGap 9 14 = radixRepresentativeBudgetPrimeEnvelope 9 14 ∧ radixRepresentativeBudget 9 14 ≤ radixRepresentativeBudgetPrimeEnvelope 9 14 ∧ (radixRepresentativeBudget 9 14 = radixRepresentativeBudgetPrimeEnvelope 9 14 ↔ lastRadixBlockQuotient 9 14 = 0 ∨ lastRadixBlockRemainder 9 14 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 14 ≤ 14 * 14 := by native_decide

/-- representative_p9_B22 -/
example : radixRepresentativeBudget 9 22 + radixRepresentativeBudgetPrimeEnvelopeGap 9 22 = radixRepresentativeBudgetPrimeEnvelope 9 22 ∧ radixRepresentativeBudget 9 22 ≤ radixRepresentativeBudgetPrimeEnvelope 9 22 ∧ (radixRepresentativeBudget 9 22 = radixRepresentativeBudgetPrimeEnvelope 9 22 ↔ lastRadixBlockQuotient 9 22 = 0 ∨ lastRadixBlockRemainder 9 22 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 22 ≤ 22 * 22 := by native_decide

/-- representative_p9_B30 -/
example : radixRepresentativeBudget 9 30 + radixRepresentativeBudgetPrimeEnvelopeGap 9 30 = radixRepresentativeBudgetPrimeEnvelope 9 30 ∧ radixRepresentativeBudget 9 30 ≤ radixRepresentativeBudgetPrimeEnvelope 9 30 ∧ (radixRepresentativeBudget 9 30 = radixRepresentativeBudgetPrimeEnvelope 9 30 ↔ lastRadixBlockQuotient 9 30 = 0 ∨ lastRadixBlockRemainder 9 30 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 30 ≤ 30 * 30 := by native_decide

/-- representative_p9_B38 -/
example : radixRepresentativeBudget 9 38 + radixRepresentativeBudgetPrimeEnvelopeGap 9 38 = radixRepresentativeBudgetPrimeEnvelope 9 38 ∧ radixRepresentativeBudget 9 38 ≤ radixRepresentativeBudgetPrimeEnvelope 9 38 ∧ (radixRepresentativeBudget 9 38 = radixRepresentativeBudgetPrimeEnvelope 9 38 ↔ lastRadixBlockQuotient 9 38 = 0 ∨ lastRadixBlockRemainder 9 38 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 38 ≤ 38 * 38 := by native_decide

/-- representative_p9_B46 -/
example : radixRepresentativeBudget 9 46 + radixRepresentativeBudgetPrimeEnvelopeGap 9 46 = radixRepresentativeBudgetPrimeEnvelope 9 46 ∧ radixRepresentativeBudget 9 46 ≤ radixRepresentativeBudgetPrimeEnvelope 9 46 ∧ (radixRepresentativeBudget 9 46 = radixRepresentativeBudgetPrimeEnvelope 9 46 ↔ lastRadixBlockQuotient 9 46 = 0 ∨ lastRadixBlockRemainder 9 46 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 46 ≤ 46 * 46 := by native_decide

/-- representative_p10_B4 -/
example : radixRepresentativeBudget 10 4 + radixRepresentativeBudgetPrimeEnvelopeGap 10 4 = radixRepresentativeBudgetPrimeEnvelope 10 4 ∧ radixRepresentativeBudget 10 4 ≤ radixRepresentativeBudgetPrimeEnvelope 10 4 ∧ (radixRepresentativeBudget 10 4 = radixRepresentativeBudgetPrimeEnvelope 10 4 ↔ lastRadixBlockQuotient 10 4 = 0 ∨ lastRadixBlockRemainder 10 4 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 4 ≤ 4 * 4 := by native_decide

/-- representative_p10_B12 -/
example : radixRepresentativeBudget 10 12 + radixRepresentativeBudgetPrimeEnvelopeGap 10 12 = radixRepresentativeBudgetPrimeEnvelope 10 12 ∧ radixRepresentativeBudget 10 12 ≤ radixRepresentativeBudgetPrimeEnvelope 10 12 ∧ (radixRepresentativeBudget 10 12 = radixRepresentativeBudgetPrimeEnvelope 10 12 ↔ lastRadixBlockQuotient 10 12 = 0 ∨ lastRadixBlockRemainder 10 12 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 12 ≤ 12 * 12 := by native_decide

/-- representative_p10_B20 -/
example : radixRepresentativeBudget 10 20 + radixRepresentativeBudgetPrimeEnvelopeGap 10 20 = radixRepresentativeBudgetPrimeEnvelope 10 20 ∧ radixRepresentativeBudget 10 20 ≤ radixRepresentativeBudgetPrimeEnvelope 10 20 ∧ (radixRepresentativeBudget 10 20 = radixRepresentativeBudgetPrimeEnvelope 10 20 ↔ lastRadixBlockQuotient 10 20 = 0 ∨ lastRadixBlockRemainder 10 20 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 20 ≤ 20 * 20 := by native_decide

/-- representative_p10_B28 -/
example : radixRepresentativeBudget 10 28 + radixRepresentativeBudgetPrimeEnvelopeGap 10 28 = radixRepresentativeBudgetPrimeEnvelope 10 28 ∧ radixRepresentativeBudget 10 28 ≤ radixRepresentativeBudgetPrimeEnvelope 10 28 ∧ (radixRepresentativeBudget 10 28 = radixRepresentativeBudgetPrimeEnvelope 10 28 ↔ lastRadixBlockQuotient 10 28 = 0 ∨ lastRadixBlockRemainder 10 28 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 28 ≤ 28 * 28 := by native_decide

/-- representative_p10_B36 -/
example : radixRepresentativeBudget 10 36 + radixRepresentativeBudgetPrimeEnvelopeGap 10 36 = radixRepresentativeBudgetPrimeEnvelope 10 36 ∧ radixRepresentativeBudget 10 36 ≤ radixRepresentativeBudgetPrimeEnvelope 10 36 ∧ (radixRepresentativeBudget 10 36 = radixRepresentativeBudgetPrimeEnvelope 10 36 ↔ lastRadixBlockQuotient 10 36 = 0 ∨ lastRadixBlockRemainder 10 36 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 36 ≤ 36 * 36 := by native_decide

/-- representative_p10_B44 -/
example : radixRepresentativeBudget 10 44 + radixRepresentativeBudgetPrimeEnvelopeGap 10 44 = radixRepresentativeBudgetPrimeEnvelope 10 44 ∧ radixRepresentativeBudget 10 44 ≤ radixRepresentativeBudgetPrimeEnvelope 10 44 ∧ (radixRepresentativeBudget 10 44 = radixRepresentativeBudgetPrimeEnvelope 10 44 ↔ lastRadixBlockQuotient 10 44 = 0 ∨ lastRadixBlockRemainder 10 44 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 44 ≤ 44 * 44 := by native_decide

/-- representative_p11_B2 -/
example : radixRepresentativeBudget 11 2 + radixRepresentativeBudgetPrimeEnvelopeGap 11 2 = radixRepresentativeBudgetPrimeEnvelope 11 2 ∧ radixRepresentativeBudget 11 2 ≤ radixRepresentativeBudgetPrimeEnvelope 11 2 ∧ (radixRepresentativeBudget 11 2 = radixRepresentativeBudgetPrimeEnvelope 11 2 ↔ lastRadixBlockQuotient 11 2 = 0 ∨ lastRadixBlockRemainder 11 2 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 2 ≤ 2 * 2 := by native_decide

/-- representative_p11_B10 -/
example : radixRepresentativeBudget 11 10 + radixRepresentativeBudgetPrimeEnvelopeGap 11 10 = radixRepresentativeBudgetPrimeEnvelope 11 10 ∧ radixRepresentativeBudget 11 10 ≤ radixRepresentativeBudgetPrimeEnvelope 11 10 ∧ (radixRepresentativeBudget 11 10 = radixRepresentativeBudgetPrimeEnvelope 11 10 ↔ lastRadixBlockQuotient 11 10 = 0 ∨ lastRadixBlockRemainder 11 10 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 10 ≤ 10 * 10 := by native_decide

/-- representative_p11_B18 -/
example : radixRepresentativeBudget 11 18 + radixRepresentativeBudgetPrimeEnvelopeGap 11 18 = radixRepresentativeBudgetPrimeEnvelope 11 18 ∧ radixRepresentativeBudget 11 18 ≤ radixRepresentativeBudgetPrimeEnvelope 11 18 ∧ (radixRepresentativeBudget 11 18 = radixRepresentativeBudgetPrimeEnvelope 11 18 ↔ lastRadixBlockQuotient 11 18 = 0 ∨ lastRadixBlockRemainder 11 18 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 18 ≤ 18 * 18 := by native_decide

/-- representative_p11_B26 -/
example : radixRepresentativeBudget 11 26 + radixRepresentativeBudgetPrimeEnvelopeGap 11 26 = radixRepresentativeBudgetPrimeEnvelope 11 26 ∧ radixRepresentativeBudget 11 26 ≤ radixRepresentativeBudgetPrimeEnvelope 11 26 ∧ (radixRepresentativeBudget 11 26 = radixRepresentativeBudgetPrimeEnvelope 11 26 ↔ lastRadixBlockQuotient 11 26 = 0 ∨ lastRadixBlockRemainder 11 26 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 26 ≤ 26 * 26 := by native_decide

/-- representative_p11_B34 -/
example : radixRepresentativeBudget 11 34 + radixRepresentativeBudgetPrimeEnvelopeGap 11 34 = radixRepresentativeBudgetPrimeEnvelope 11 34 ∧ radixRepresentativeBudget 11 34 ≤ radixRepresentativeBudgetPrimeEnvelope 11 34 ∧ (radixRepresentativeBudget 11 34 = radixRepresentativeBudgetPrimeEnvelope 11 34 ↔ lastRadixBlockQuotient 11 34 = 0 ∨ lastRadixBlockRemainder 11 34 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 34 ≤ 34 * 34 := by native_decide

/-- representative_p11_B42 -/
example : radixRepresentativeBudget 11 42 + radixRepresentativeBudgetPrimeEnvelopeGap 11 42 = radixRepresentativeBudgetPrimeEnvelope 11 42 ∧ radixRepresentativeBudget 11 42 ≤ radixRepresentativeBudgetPrimeEnvelope 11 42 ∧ (radixRepresentativeBudget 11 42 = radixRepresentativeBudgetPrimeEnvelope 11 42 ↔ lastRadixBlockQuotient 11 42 = 0 ∨ lastRadixBlockRemainder 11 42 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 42 ≤ 42 * 42 := by native_decide

/-- representative_p12_B0 -/
example : radixRepresentativeBudget 12 0 + radixRepresentativeBudgetPrimeEnvelopeGap 12 0 = radixRepresentativeBudgetPrimeEnvelope 12 0 ∧ radixRepresentativeBudget 12 0 ≤ radixRepresentativeBudgetPrimeEnvelope 12 0 ∧ (radixRepresentativeBudget 12 0 = radixRepresentativeBudgetPrimeEnvelope 12 0 ↔ lastRadixBlockQuotient 12 0 = 0 ∨ lastRadixBlockRemainder 12 0 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 0 ≤ 0 * 0 := by native_decide

/-- representative_p12_B8 -/
example : radixRepresentativeBudget 12 8 + radixRepresentativeBudgetPrimeEnvelopeGap 12 8 = radixRepresentativeBudgetPrimeEnvelope 12 8 ∧ radixRepresentativeBudget 12 8 ≤ radixRepresentativeBudgetPrimeEnvelope 12 8 ∧ (radixRepresentativeBudget 12 8 = radixRepresentativeBudgetPrimeEnvelope 12 8 ↔ lastRadixBlockQuotient 12 8 = 0 ∨ lastRadixBlockRemainder 12 8 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 8 ≤ 8 * 8 := by native_decide

/-- representative_p12_B16 -/
example : radixRepresentativeBudget 12 16 + radixRepresentativeBudgetPrimeEnvelopeGap 12 16 = radixRepresentativeBudgetPrimeEnvelope 12 16 ∧ radixRepresentativeBudget 12 16 ≤ radixRepresentativeBudgetPrimeEnvelope 12 16 ∧ (radixRepresentativeBudget 12 16 = radixRepresentativeBudgetPrimeEnvelope 12 16 ↔ lastRadixBlockQuotient 12 16 = 0 ∨ lastRadixBlockRemainder 12 16 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 16 ≤ 16 * 16 := by native_decide

/-- representative_p12_B24 -/
example : radixRepresentativeBudget 12 24 + radixRepresentativeBudgetPrimeEnvelopeGap 12 24 = radixRepresentativeBudgetPrimeEnvelope 12 24 ∧ radixRepresentativeBudget 12 24 ≤ radixRepresentativeBudgetPrimeEnvelope 12 24 ∧ (radixRepresentativeBudget 12 24 = radixRepresentativeBudgetPrimeEnvelope 12 24 ↔ lastRadixBlockQuotient 12 24 = 0 ∨ lastRadixBlockRemainder 12 24 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 24 ≤ 24 * 24 := by native_decide

/-- representative_p12_B32 -/
example : radixRepresentativeBudget 12 32 + radixRepresentativeBudgetPrimeEnvelopeGap 12 32 = radixRepresentativeBudgetPrimeEnvelope 12 32 ∧ radixRepresentativeBudget 12 32 ≤ radixRepresentativeBudgetPrimeEnvelope 12 32 ∧ (radixRepresentativeBudget 12 32 = radixRepresentativeBudgetPrimeEnvelope 12 32 ↔ lastRadixBlockQuotient 12 32 = 0 ∨ lastRadixBlockRemainder 12 32 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 32 ≤ 32 * 32 := by native_decide

/-- representative_p12_B40 -/
example : radixRepresentativeBudget 12 40 + radixRepresentativeBudgetPrimeEnvelopeGap 12 40 = radixRepresentativeBudgetPrimeEnvelope 12 40 ∧ radixRepresentativeBudget 12 40 ≤ radixRepresentativeBudgetPrimeEnvelope 12 40 ∧ (radixRepresentativeBudget 12 40 = radixRepresentativeBudgetPrimeEnvelope 12 40 ↔ lastRadixBlockQuotient 12 40 = 0 ∨ lastRadixBlockRemainder 12 40 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 40 ≤ 40 * 40 := by native_decide

/-- representative_p12_B48 -/
example : radixRepresentativeBudget 12 48 + radixRepresentativeBudgetPrimeEnvelopeGap 12 48 = radixRepresentativeBudgetPrimeEnvelope 12 48 ∧ radixRepresentativeBudget 12 48 ≤ radixRepresentativeBudgetPrimeEnvelope 12 48 ∧ (radixRepresentativeBudget 12 48 = radixRepresentativeBudgetPrimeEnvelope 12 48 ↔ lastRadixBlockQuotient 12 48 = 0 ∨ lastRadixBlockRemainder 12 48 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 48 ≤ 48 * 48 := by native_decide

/-- zero_base_B6 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 6 ≤ 6 * 6 := by native_decide

/-- zero_base_B14 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 14 ≤ 14 * 14 := by native_decide

/-- zero_base_B22 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 22 ≤ 22 * 22 := by native_decide

/-- zero_base_B30 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 30 ≤ 30 * 30 := by native_decide

/-- zero_base_B38 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 38 ≤ 38 * 38 := by native_decide

/-- zero_base_B46 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 46 ≤ 46 * 46 := by native_decide

/-- zero_base_B54 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 54 ≤ 54 * 54 := by native_decide

/-- zero_base_B62 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 62 ≤ 62 * 62 := by native_decide

/-- zero_base_B70 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 70 ≤ 70 * 70 := by native_decide

/-- zero_base_B78 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 78 ≤ 78 * 78 := by native_decide

/-- zero_base_B86 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 86 ≤ 86 * 86 := by native_decide

/-- zero_base_B94 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 94 ≤ 94 * 94 := by native_decide

/-- zero_base_B102 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 102 ≤ 102 * 102 := by native_decide

/-- zero_base_B110 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 110 ≤ 110 * 110 := by native_decide

/-- zero_base_B118 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 118 ≤ 118 * 118 := by native_decide

/-- zero_base_B126 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 126 ≤ 126 * 126 := by native_decide

/-- zero_base_B134 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 134 ≤ 134 * 134 := by native_decide

/-- zero_base_B142 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 142 ≤ 142 * 142 := by native_decide

/-- zero_base_B150 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 150 ≤ 150 * 150 := by native_decide

/-- zero_base_B158 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 158 ≤ 158 * 158 := by native_decide

/-- zero_base_B166 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 166 ≤ 166 * 166 := by native_decide

/-- zero_base_B174 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 174 ≤ 174 * 174 := by native_decide

/-- zero_base_B182 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 182 ≤ 182 * 182 := by native_decide

/-- zero_base_B190 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 190 ≤ 190 * 190 := by native_decide

/-- zero_base_B198 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 198 ≤ 198 * 198 := by native_decide

/-- compiler_p2_r3_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 3 0 + maximumLayerCompilerPrimeEnvelopeGap 2 3 0 = maximumLayerCompilerPrimeEnvelopeBound 2 3 0 ∧ maximumLayerCompilerTotalTests 2 3 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 3 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 3 0 ≤ maximumLayerCompilerTestBound 2 3 0 := by native_decide

/-- compiler_p2_r5_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 5 2 + maximumLayerCompilerPrimeEnvelopeGap 2 5 2 = maximumLayerCompilerPrimeEnvelopeBound 2 5 2 ∧ maximumLayerCompilerTotalTests 2 5 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 5 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 5 2 ≤ maximumLayerCompilerTestBound 2 5 2 := by native_decide

/-- compiler_p2_r8_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 8 1 + maximumLayerCompilerPrimeEnvelopeGap 2 8 1 = maximumLayerCompilerPrimeEnvelopeBound 2 8 1 ∧ maximumLayerCompilerTotalTests 2 8 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 8 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 8 1 ≤ maximumLayerCompilerTestBound 2 8 1 := by native_decide

/-- compiler_p2_r11_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 11 0 + maximumLayerCompilerPrimeEnvelopeGap 2 11 0 = maximumLayerCompilerPrimeEnvelopeBound 2 11 0 ∧ maximumLayerCompilerTotalTests 2 11 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 11 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 11 0 ≤ maximumLayerCompilerTestBound 2 11 0 := by native_decide

/-- compiler_p2_r13_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 13 2 + maximumLayerCompilerPrimeEnvelopeGap 2 13 2 = maximumLayerCompilerPrimeEnvelopeBound 2 13 2 ∧ maximumLayerCompilerTotalTests 2 13 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 13 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 13 2 ≤ maximumLayerCompilerTestBound 2 13 2 := by native_decide

/-- compiler_p2_r16_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 16 1 + maximumLayerCompilerPrimeEnvelopeGap 2 16 1 = maximumLayerCompilerPrimeEnvelopeBound 2 16 1 ∧ maximumLayerCompilerTotalTests 2 16 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 16 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 16 1 ≤ maximumLayerCompilerTestBound 2 16 1 := by native_decide

/-- compiler_p2_r19_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 19 0 + maximumLayerCompilerPrimeEnvelopeGap 2 19 0 = maximumLayerCompilerPrimeEnvelopeBound 2 19 0 ∧ maximumLayerCompilerTotalTests 2 19 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 19 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 19 0 ≤ maximumLayerCompilerTestBound 2 19 0 := by native_decide

/-- compiler_p3_r1_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 1 2 + maximumLayerCompilerPrimeEnvelopeGap 3 1 2 = maximumLayerCompilerPrimeEnvelopeBound 3 1 2 ∧ maximumLayerCompilerTotalTests 3 1 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 1 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 1 2 ≤ maximumLayerCompilerTestBound 3 1 2 := by native_decide

/-- compiler_p3_r4_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 4 1 + maximumLayerCompilerPrimeEnvelopeGap 3 4 1 = maximumLayerCompilerPrimeEnvelopeBound 3 4 1 ∧ maximumLayerCompilerTotalTests 3 4 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 4 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 4 1 ≤ maximumLayerCompilerTestBound 3 4 1 := by native_decide

/-- compiler_p3_r7_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 7 0 + maximumLayerCompilerPrimeEnvelopeGap 3 7 0 = maximumLayerCompilerPrimeEnvelopeBound 3 7 0 ∧ maximumLayerCompilerTotalTests 3 7 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 7 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 7 0 ≤ maximumLayerCompilerTestBound 3 7 0 := by native_decide

/-- compiler_p3_r9_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 9 2 + maximumLayerCompilerPrimeEnvelopeGap 3 9 2 = maximumLayerCompilerPrimeEnvelopeBound 3 9 2 ∧ maximumLayerCompilerTotalTests 3 9 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 9 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 9 2 ≤ maximumLayerCompilerTestBound 3 9 2 := by native_decide

/-- compiler_p3_r12_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 12 1 + maximumLayerCompilerPrimeEnvelopeGap 3 12 1 = maximumLayerCompilerPrimeEnvelopeBound 3 12 1 ∧ maximumLayerCompilerTotalTests 3 12 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 12 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 12 1 ≤ maximumLayerCompilerTestBound 3 12 1 := by native_decide

/-- compiler_p3_r15_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 15 0 + maximumLayerCompilerPrimeEnvelopeGap 3 15 0 = maximumLayerCompilerPrimeEnvelopeBound 3 15 0 ∧ maximumLayerCompilerTotalTests 3 15 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 15 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 15 0 ≤ maximumLayerCompilerTestBound 3 15 0 := by native_decide

/-- compiler_p3_r17_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 17 2 + maximumLayerCompilerPrimeEnvelopeGap 3 17 2 = maximumLayerCompilerPrimeEnvelopeBound 3 17 2 ∧ maximumLayerCompilerTotalTests 3 17 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 17 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 17 2 ≤ maximumLayerCompilerTestBound 3 17 2 := by native_decide

/-- compiler_p3_r20_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 20 1 + maximumLayerCompilerPrimeEnvelopeGap 3 20 1 = maximumLayerCompilerPrimeEnvelopeBound 3 20 1 ∧ maximumLayerCompilerTotalTests 3 20 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 20 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 20 1 ≤ maximumLayerCompilerTestBound 3 20 1 := by native_decide

/-- compiler_p5_r3_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 3 0 + maximumLayerCompilerPrimeEnvelopeGap 5 3 0 = maximumLayerCompilerPrimeEnvelopeBound 5 3 0 ∧ maximumLayerCompilerTotalTests 5 3 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 3 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 3 0 ≤ maximumLayerCompilerTestBound 5 3 0 := by native_decide

/-- compiler_p5_r5_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 5 2 + maximumLayerCompilerPrimeEnvelopeGap 5 5 2 = maximumLayerCompilerPrimeEnvelopeBound 5 5 2 ∧ maximumLayerCompilerTotalTests 5 5 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 5 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 5 2 ≤ maximumLayerCompilerTestBound 5 5 2 := by native_decide

/-- compiler_p5_r8_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 8 1 + maximumLayerCompilerPrimeEnvelopeGap 5 8 1 = maximumLayerCompilerPrimeEnvelopeBound 5 8 1 ∧ maximumLayerCompilerTotalTests 5 8 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 8 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 8 1 ≤ maximumLayerCompilerTestBound 5 8 1 := by native_decide

/-- compiler_p5_r11_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 11 0 + maximumLayerCompilerPrimeEnvelopeGap 5 11 0 = maximumLayerCompilerPrimeEnvelopeBound 5 11 0 ∧ maximumLayerCompilerTotalTests 5 11 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 11 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 11 0 ≤ maximumLayerCompilerTestBound 5 11 0 := by native_decide

/-- compiler_p5_r13_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 13 2 + maximumLayerCompilerPrimeEnvelopeGap 5 13 2 = maximumLayerCompilerPrimeEnvelopeBound 5 13 2 ∧ maximumLayerCompilerTotalTests 5 13 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 13 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 13 2 ≤ maximumLayerCompilerTestBound 5 13 2 := by native_decide

/-- compiler_p5_r16_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 16 1 + maximumLayerCompilerPrimeEnvelopeGap 5 16 1 = maximumLayerCompilerPrimeEnvelopeBound 5 16 1 ∧ maximumLayerCompilerTotalTests 5 16 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 16 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 16 1 ≤ maximumLayerCompilerTestBound 5 16 1 := by native_decide

/-- compiler_p5_r19_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 19 0 + maximumLayerCompilerPrimeEnvelopeGap 5 19 0 = maximumLayerCompilerPrimeEnvelopeBound 5 19 0 ∧ maximumLayerCompilerTotalTests 5 19 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 19 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 19 0 ≤ maximumLayerCompilerTestBound 5 19 0 := by native_decide

/-- compiler_p7_r1_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 1 2 + maximumLayerCompilerPrimeEnvelopeGap 7 1 2 = maximumLayerCompilerPrimeEnvelopeBound 7 1 2 ∧ maximumLayerCompilerTotalTests 7 1 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 1 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 1 2 ≤ maximumLayerCompilerTestBound 7 1 2 := by native_decide

/-- compiler_p7_r4_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 4 1 + maximumLayerCompilerPrimeEnvelopeGap 7 4 1 = maximumLayerCompilerPrimeEnvelopeBound 7 4 1 ∧ maximumLayerCompilerTotalTests 7 4 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 4 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 4 1 ≤ maximumLayerCompilerTestBound 7 4 1 := by native_decide

/-- compiler_p7_r7_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 7 0 + maximumLayerCompilerPrimeEnvelopeGap 7 7 0 = maximumLayerCompilerPrimeEnvelopeBound 7 7 0 ∧ maximumLayerCompilerTotalTests 7 7 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 7 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 7 0 ≤ maximumLayerCompilerTestBound 7 7 0 := by native_decide

/-- compiler_p7_r9_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 9 2 + maximumLayerCompilerPrimeEnvelopeGap 7 9 2 = maximumLayerCompilerPrimeEnvelopeBound 7 9 2 ∧ maximumLayerCompilerTotalTests 7 9 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 9 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 9 2 ≤ maximumLayerCompilerTestBound 7 9 2 := by native_decide

/-- compiler_p7_r12_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 12 1 + maximumLayerCompilerPrimeEnvelopeGap 7 12 1 = maximumLayerCompilerPrimeEnvelopeBound 7 12 1 ∧ maximumLayerCompilerTotalTests 7 12 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 12 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 12 1 ≤ maximumLayerCompilerTestBound 7 12 1 := by native_decide

/-- compiler_p7_r15_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 15 0 + maximumLayerCompilerPrimeEnvelopeGap 7 15 0 = maximumLayerCompilerPrimeEnvelopeBound 7 15 0 ∧ maximumLayerCompilerTotalTests 7 15 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 15 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 15 0 ≤ maximumLayerCompilerTestBound 7 15 0 := by native_decide

/-- compiler_p7_r17_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 17 2 + maximumLayerCompilerPrimeEnvelopeGap 7 17 2 = maximumLayerCompilerPrimeEnvelopeBound 7 17 2 ∧ maximumLayerCompilerTotalTests 7 17 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 17 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 17 2 ≤ maximumLayerCompilerTestBound 7 17 2 := by native_decide

/-- compiler_p7_r20_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 20 1 + maximumLayerCompilerPrimeEnvelopeGap 7 20 1 = maximumLayerCompilerPrimeEnvelopeBound 7 20 1 ∧ maximumLayerCompilerTotalTests 7 20 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 20 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 20 1 ≤ maximumLayerCompilerTestBound 7 20 1 := by native_decide

/-- compiler_p11_r3_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 3 0 + maximumLayerCompilerPrimeEnvelopeGap 11 3 0 = maximumLayerCompilerPrimeEnvelopeBound 11 3 0 ∧ maximumLayerCompilerTotalTests 11 3 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 3 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 3 0 ≤ maximumLayerCompilerTestBound 11 3 0 := by native_decide

/-- compiler_p11_r5_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 5 2 + maximumLayerCompilerPrimeEnvelopeGap 11 5 2 = maximumLayerCompilerPrimeEnvelopeBound 11 5 2 ∧ maximumLayerCompilerTotalTests 11 5 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 5 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 5 2 ≤ maximumLayerCompilerTestBound 11 5 2 := by native_decide

/-- compiler_p11_r8_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 8 1 + maximumLayerCompilerPrimeEnvelopeGap 11 8 1 = maximumLayerCompilerPrimeEnvelopeBound 11 8 1 ∧ maximumLayerCompilerTotalTests 11 8 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 8 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 8 1 ≤ maximumLayerCompilerTestBound 11 8 1 := by native_decide

/-- compiler_p11_r11_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 11 0 + maximumLayerCompilerPrimeEnvelopeGap 11 11 0 = maximumLayerCompilerPrimeEnvelopeBound 11 11 0 ∧ maximumLayerCompilerTotalTests 11 11 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 11 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 11 0 ≤ maximumLayerCompilerTestBound 11 11 0 := by native_decide

/-- compiler_p11_r13_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 13 2 + maximumLayerCompilerPrimeEnvelopeGap 11 13 2 = maximumLayerCompilerPrimeEnvelopeBound 11 13 2 ∧ maximumLayerCompilerTotalTests 11 13 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 13 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 13 2 ≤ maximumLayerCompilerTestBound 11 13 2 := by native_decide

/-- compiler_p11_r16_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 16 1 + maximumLayerCompilerPrimeEnvelopeGap 11 16 1 = maximumLayerCompilerPrimeEnvelopeBound 11 16 1 ∧ maximumLayerCompilerTotalTests 11 16 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 16 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 16 1 ≤ maximumLayerCompilerTestBound 11 16 1 := by native_decide

/-- compiler_p11_r19_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 19 0 + maximumLayerCompilerPrimeEnvelopeGap 11 19 0 = maximumLayerCompilerPrimeEnvelopeBound 11 19 0 ∧ maximumLayerCompilerTotalTests 11 19 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 19 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 19 0 ≤ maximumLayerCompilerTestBound 11 19 0 := by native_decide

/-- compiler_p13_r1_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 1 2 + maximumLayerCompilerPrimeEnvelopeGap 13 1 2 = maximumLayerCompilerPrimeEnvelopeBound 13 1 2 ∧ maximumLayerCompilerTotalTests 13 1 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 1 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 1 2 ≤ maximumLayerCompilerTestBound 13 1 2 := by native_decide

/-- compiler_p13_r4_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 4 1 + maximumLayerCompilerPrimeEnvelopeGap 13 4 1 = maximumLayerCompilerPrimeEnvelopeBound 13 4 1 ∧ maximumLayerCompilerTotalTests 13 4 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 4 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 4 1 ≤ maximumLayerCompilerTestBound 13 4 1 := by native_decide

/-- compiler_p13_r7_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 7 0 + maximumLayerCompilerPrimeEnvelopeGap 13 7 0 = maximumLayerCompilerPrimeEnvelopeBound 13 7 0 ∧ maximumLayerCompilerTotalTests 13 7 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 7 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 7 0 ≤ maximumLayerCompilerTestBound 13 7 0 := by native_decide

/-- compiler_p13_r9_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 9 2 + maximumLayerCompilerPrimeEnvelopeGap 13 9 2 = maximumLayerCompilerPrimeEnvelopeBound 13 9 2 ∧ maximumLayerCompilerTotalTests 13 9 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 9 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 9 2 ≤ maximumLayerCompilerTestBound 13 9 2 := by native_decide

/-- compiler_p13_r12_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 12 1 + maximumLayerCompilerPrimeEnvelopeGap 13 12 1 = maximumLayerCompilerPrimeEnvelopeBound 13 12 1 ∧ maximumLayerCompilerTotalTests 13 12 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 12 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 12 1 ≤ maximumLayerCompilerTestBound 13 12 1 := by native_decide

/-- compiler_p13_r15_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 15 0 + maximumLayerCompilerPrimeEnvelopeGap 13 15 0 = maximumLayerCompilerPrimeEnvelopeBound 13 15 0 ∧ maximumLayerCompilerTotalTests 13 15 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 15 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 15 0 ≤ maximumLayerCompilerTestBound 13 15 0 := by native_decide

/-- compiler_p13_r17_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 17 2 + maximumLayerCompilerPrimeEnvelopeGap 13 17 2 = maximumLayerCompilerPrimeEnvelopeBound 13 17 2 ∧ maximumLayerCompilerTotalTests 13 17 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 17 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 17 2 ≤ maximumLayerCompilerTestBound 13 17 2 := by native_decide

/-- compiler_p13_r20_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 20 1 + maximumLayerCompilerPrimeEnvelopeGap 13 20 1 = maximumLayerCompilerPrimeEnvelopeBound 13 20 1 ∧ maximumLayerCompilerTotalTests 13 20 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 20 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 20 1 ≤ maximumLayerCompilerTestBound 13 20 1 := by native_decide

end KomorebiPadic
