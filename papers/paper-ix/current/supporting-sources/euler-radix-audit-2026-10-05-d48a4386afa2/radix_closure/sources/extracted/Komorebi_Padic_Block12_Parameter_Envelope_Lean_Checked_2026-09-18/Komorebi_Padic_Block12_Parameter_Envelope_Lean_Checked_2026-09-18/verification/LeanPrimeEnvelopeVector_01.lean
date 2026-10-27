import KomorebiPadic

namespace KomorebiPadic

/-- representative_p1_B0 -/
example : radixRepresentativeBudget 1 0 + radixRepresentativeBudgetPrimeEnvelopeGap 1 0 = radixRepresentativeBudgetPrimeEnvelope 1 0 ∧ radixRepresentativeBudget 1 0 ≤ radixRepresentativeBudgetPrimeEnvelope 1 0 ∧ (radixRepresentativeBudget 1 0 = radixRepresentativeBudgetPrimeEnvelope 1 0 ↔ lastRadixBlockQuotient 1 0 = 0 ∨ lastRadixBlockRemainder 1 0 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 0 ≤ 0 * 0 := by native_decide

/-- representative_p1_B8 -/
example : radixRepresentativeBudget 1 8 + radixRepresentativeBudgetPrimeEnvelopeGap 1 8 = radixRepresentativeBudgetPrimeEnvelope 1 8 ∧ radixRepresentativeBudget 1 8 ≤ radixRepresentativeBudgetPrimeEnvelope 1 8 ∧ (radixRepresentativeBudget 1 8 = radixRepresentativeBudgetPrimeEnvelope 1 8 ↔ lastRadixBlockQuotient 1 8 = 0 ∨ lastRadixBlockRemainder 1 8 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 8 ≤ 8 * 8 := by native_decide

/-- representative_p1_B16 -/
example : radixRepresentativeBudget 1 16 + radixRepresentativeBudgetPrimeEnvelopeGap 1 16 = radixRepresentativeBudgetPrimeEnvelope 1 16 ∧ radixRepresentativeBudget 1 16 ≤ radixRepresentativeBudgetPrimeEnvelope 1 16 ∧ (radixRepresentativeBudget 1 16 = radixRepresentativeBudgetPrimeEnvelope 1 16 ↔ lastRadixBlockQuotient 1 16 = 0 ∨ lastRadixBlockRemainder 1 16 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 16 ≤ 16 * 16 := by native_decide

/-- representative_p1_B24 -/
example : radixRepresentativeBudget 1 24 + radixRepresentativeBudgetPrimeEnvelopeGap 1 24 = radixRepresentativeBudgetPrimeEnvelope 1 24 ∧ radixRepresentativeBudget 1 24 ≤ radixRepresentativeBudgetPrimeEnvelope 1 24 ∧ (radixRepresentativeBudget 1 24 = radixRepresentativeBudgetPrimeEnvelope 1 24 ↔ lastRadixBlockQuotient 1 24 = 0 ∨ lastRadixBlockRemainder 1 24 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 24 ≤ 24 * 24 := by native_decide

/-- representative_p1_B32 -/
example : radixRepresentativeBudget 1 32 + radixRepresentativeBudgetPrimeEnvelopeGap 1 32 = radixRepresentativeBudgetPrimeEnvelope 1 32 ∧ radixRepresentativeBudget 1 32 ≤ radixRepresentativeBudgetPrimeEnvelope 1 32 ∧ (radixRepresentativeBudget 1 32 = radixRepresentativeBudgetPrimeEnvelope 1 32 ↔ lastRadixBlockQuotient 1 32 = 0 ∨ lastRadixBlockRemainder 1 32 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 32 ≤ 32 * 32 := by native_decide

/-- representative_p1_B40 -/
example : radixRepresentativeBudget 1 40 + radixRepresentativeBudgetPrimeEnvelopeGap 1 40 = radixRepresentativeBudgetPrimeEnvelope 1 40 ∧ radixRepresentativeBudget 1 40 ≤ radixRepresentativeBudgetPrimeEnvelope 1 40 ∧ (radixRepresentativeBudget 1 40 = radixRepresentativeBudgetPrimeEnvelope 1 40 ↔ lastRadixBlockQuotient 1 40 = 0 ∨ lastRadixBlockRemainder 1 40 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 40 ≤ 40 * 40 := by native_decide

/-- representative_p1_B48 -/
example : radixRepresentativeBudget 1 48 + radixRepresentativeBudgetPrimeEnvelopeGap 1 48 = radixRepresentativeBudgetPrimeEnvelope 1 48 ∧ radixRepresentativeBudget 1 48 ≤ radixRepresentativeBudgetPrimeEnvelope 1 48 ∧ (radixRepresentativeBudget 1 48 = radixRepresentativeBudgetPrimeEnvelope 1 48 ↔ lastRadixBlockQuotient 1 48 = 0 ∨ lastRadixBlockRemainder 1 48 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 48 ≤ 48 * 48 := by native_decide

/-- representative_p2_B6 -/
example : radixRepresentativeBudget 2 6 + radixRepresentativeBudgetPrimeEnvelopeGap 2 6 = radixRepresentativeBudgetPrimeEnvelope 2 6 ∧ radixRepresentativeBudget 2 6 ≤ radixRepresentativeBudgetPrimeEnvelope 2 6 ∧ (radixRepresentativeBudget 2 6 = radixRepresentativeBudgetPrimeEnvelope 2 6 ↔ lastRadixBlockQuotient 2 6 = 0 ∨ lastRadixBlockRemainder 2 6 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 6 ≤ 6 * 6 := by native_decide

/-- representative_p2_B14 -/
example : radixRepresentativeBudget 2 14 + radixRepresentativeBudgetPrimeEnvelopeGap 2 14 = radixRepresentativeBudgetPrimeEnvelope 2 14 ∧ radixRepresentativeBudget 2 14 ≤ radixRepresentativeBudgetPrimeEnvelope 2 14 ∧ (radixRepresentativeBudget 2 14 = radixRepresentativeBudgetPrimeEnvelope 2 14 ↔ lastRadixBlockQuotient 2 14 = 0 ∨ lastRadixBlockRemainder 2 14 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 14 ≤ 14 * 14 := by native_decide

/-- representative_p2_B22 -/
example : radixRepresentativeBudget 2 22 + radixRepresentativeBudgetPrimeEnvelopeGap 2 22 = radixRepresentativeBudgetPrimeEnvelope 2 22 ∧ radixRepresentativeBudget 2 22 ≤ radixRepresentativeBudgetPrimeEnvelope 2 22 ∧ (radixRepresentativeBudget 2 22 = radixRepresentativeBudgetPrimeEnvelope 2 22 ↔ lastRadixBlockQuotient 2 22 = 0 ∨ lastRadixBlockRemainder 2 22 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 22 ≤ 22 * 22 := by native_decide

/-- representative_p2_B30 -/
example : radixRepresentativeBudget 2 30 + radixRepresentativeBudgetPrimeEnvelopeGap 2 30 = radixRepresentativeBudgetPrimeEnvelope 2 30 ∧ radixRepresentativeBudget 2 30 ≤ radixRepresentativeBudgetPrimeEnvelope 2 30 ∧ (radixRepresentativeBudget 2 30 = radixRepresentativeBudgetPrimeEnvelope 2 30 ↔ lastRadixBlockQuotient 2 30 = 0 ∨ lastRadixBlockRemainder 2 30 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 30 ≤ 30 * 30 := by native_decide

/-- representative_p2_B38 -/
example : radixRepresentativeBudget 2 38 + radixRepresentativeBudgetPrimeEnvelopeGap 2 38 = radixRepresentativeBudgetPrimeEnvelope 2 38 ∧ radixRepresentativeBudget 2 38 ≤ radixRepresentativeBudgetPrimeEnvelope 2 38 ∧ (radixRepresentativeBudget 2 38 = radixRepresentativeBudgetPrimeEnvelope 2 38 ↔ lastRadixBlockQuotient 2 38 = 0 ∨ lastRadixBlockRemainder 2 38 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 38 ≤ 38 * 38 := by native_decide

/-- representative_p2_B46 -/
example : radixRepresentativeBudget 2 46 + radixRepresentativeBudgetPrimeEnvelopeGap 2 46 = radixRepresentativeBudgetPrimeEnvelope 2 46 ∧ radixRepresentativeBudget 2 46 ≤ radixRepresentativeBudgetPrimeEnvelope 2 46 ∧ (radixRepresentativeBudget 2 46 = radixRepresentativeBudgetPrimeEnvelope 2 46 ↔ lastRadixBlockQuotient 2 46 = 0 ∨ lastRadixBlockRemainder 2 46 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 46 ≤ 46 * 46 := by native_decide

/-- representative_p3_B4 -/
example : radixRepresentativeBudget 3 4 + radixRepresentativeBudgetPrimeEnvelopeGap 3 4 = radixRepresentativeBudgetPrimeEnvelope 3 4 ∧ radixRepresentativeBudget 3 4 ≤ radixRepresentativeBudgetPrimeEnvelope 3 4 ∧ (radixRepresentativeBudget 3 4 = radixRepresentativeBudgetPrimeEnvelope 3 4 ↔ lastRadixBlockQuotient 3 4 = 0 ∨ lastRadixBlockRemainder 3 4 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 4 ≤ 4 * 4 := by native_decide

/-- representative_p3_B12 -/
example : radixRepresentativeBudget 3 12 + radixRepresentativeBudgetPrimeEnvelopeGap 3 12 = radixRepresentativeBudgetPrimeEnvelope 3 12 ∧ radixRepresentativeBudget 3 12 ≤ radixRepresentativeBudgetPrimeEnvelope 3 12 ∧ (radixRepresentativeBudget 3 12 = radixRepresentativeBudgetPrimeEnvelope 3 12 ↔ lastRadixBlockQuotient 3 12 = 0 ∨ lastRadixBlockRemainder 3 12 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 12 ≤ 12 * 12 := by native_decide

/-- representative_p3_B20 -/
example : radixRepresentativeBudget 3 20 + radixRepresentativeBudgetPrimeEnvelopeGap 3 20 = radixRepresentativeBudgetPrimeEnvelope 3 20 ∧ radixRepresentativeBudget 3 20 ≤ radixRepresentativeBudgetPrimeEnvelope 3 20 ∧ (radixRepresentativeBudget 3 20 = radixRepresentativeBudgetPrimeEnvelope 3 20 ↔ lastRadixBlockQuotient 3 20 = 0 ∨ lastRadixBlockRemainder 3 20 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 20 ≤ 20 * 20 := by native_decide

/-- representative_p3_B28 -/
example : radixRepresentativeBudget 3 28 + radixRepresentativeBudgetPrimeEnvelopeGap 3 28 = radixRepresentativeBudgetPrimeEnvelope 3 28 ∧ radixRepresentativeBudget 3 28 ≤ radixRepresentativeBudgetPrimeEnvelope 3 28 ∧ (radixRepresentativeBudget 3 28 = radixRepresentativeBudgetPrimeEnvelope 3 28 ↔ lastRadixBlockQuotient 3 28 = 0 ∨ lastRadixBlockRemainder 3 28 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 28 ≤ 28 * 28 := by native_decide

/-- representative_p3_B36 -/
example : radixRepresentativeBudget 3 36 + radixRepresentativeBudgetPrimeEnvelopeGap 3 36 = radixRepresentativeBudgetPrimeEnvelope 3 36 ∧ radixRepresentativeBudget 3 36 ≤ radixRepresentativeBudgetPrimeEnvelope 3 36 ∧ (radixRepresentativeBudget 3 36 = radixRepresentativeBudgetPrimeEnvelope 3 36 ↔ lastRadixBlockQuotient 3 36 = 0 ∨ lastRadixBlockRemainder 3 36 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 36 ≤ 36 * 36 := by native_decide

/-- representative_p3_B44 -/
example : radixRepresentativeBudget 3 44 + radixRepresentativeBudgetPrimeEnvelopeGap 3 44 = radixRepresentativeBudgetPrimeEnvelope 3 44 ∧ radixRepresentativeBudget 3 44 ≤ radixRepresentativeBudgetPrimeEnvelope 3 44 ∧ (radixRepresentativeBudget 3 44 = radixRepresentativeBudgetPrimeEnvelope 3 44 ↔ lastRadixBlockQuotient 3 44 = 0 ∨ lastRadixBlockRemainder 3 44 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 44 ≤ 44 * 44 := by native_decide

/-- representative_p4_B2 -/
example : radixRepresentativeBudget 4 2 + radixRepresentativeBudgetPrimeEnvelopeGap 4 2 = radixRepresentativeBudgetPrimeEnvelope 4 2 ∧ radixRepresentativeBudget 4 2 ≤ radixRepresentativeBudgetPrimeEnvelope 4 2 ∧ (radixRepresentativeBudget 4 2 = radixRepresentativeBudgetPrimeEnvelope 4 2 ↔ lastRadixBlockQuotient 4 2 = 0 ∨ lastRadixBlockRemainder 4 2 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 2 ≤ 2 * 2 := by native_decide

/-- representative_p4_B10 -/
example : radixRepresentativeBudget 4 10 + radixRepresentativeBudgetPrimeEnvelopeGap 4 10 = radixRepresentativeBudgetPrimeEnvelope 4 10 ∧ radixRepresentativeBudget 4 10 ≤ radixRepresentativeBudgetPrimeEnvelope 4 10 ∧ (radixRepresentativeBudget 4 10 = radixRepresentativeBudgetPrimeEnvelope 4 10 ↔ lastRadixBlockQuotient 4 10 = 0 ∨ lastRadixBlockRemainder 4 10 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 10 ≤ 10 * 10 := by native_decide

/-- representative_p4_B18 -/
example : radixRepresentativeBudget 4 18 + radixRepresentativeBudgetPrimeEnvelopeGap 4 18 = radixRepresentativeBudgetPrimeEnvelope 4 18 ∧ radixRepresentativeBudget 4 18 ≤ radixRepresentativeBudgetPrimeEnvelope 4 18 ∧ (radixRepresentativeBudget 4 18 = radixRepresentativeBudgetPrimeEnvelope 4 18 ↔ lastRadixBlockQuotient 4 18 = 0 ∨ lastRadixBlockRemainder 4 18 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 18 ≤ 18 * 18 := by native_decide

/-- representative_p4_B26 -/
example : radixRepresentativeBudget 4 26 + radixRepresentativeBudgetPrimeEnvelopeGap 4 26 = radixRepresentativeBudgetPrimeEnvelope 4 26 ∧ radixRepresentativeBudget 4 26 ≤ radixRepresentativeBudgetPrimeEnvelope 4 26 ∧ (radixRepresentativeBudget 4 26 = radixRepresentativeBudgetPrimeEnvelope 4 26 ↔ lastRadixBlockQuotient 4 26 = 0 ∨ lastRadixBlockRemainder 4 26 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 26 ≤ 26 * 26 := by native_decide

/-- representative_p4_B34 -/
example : radixRepresentativeBudget 4 34 + radixRepresentativeBudgetPrimeEnvelopeGap 4 34 = radixRepresentativeBudgetPrimeEnvelope 4 34 ∧ radixRepresentativeBudget 4 34 ≤ radixRepresentativeBudgetPrimeEnvelope 4 34 ∧ (radixRepresentativeBudget 4 34 = radixRepresentativeBudgetPrimeEnvelope 4 34 ↔ lastRadixBlockQuotient 4 34 = 0 ∨ lastRadixBlockRemainder 4 34 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 34 ≤ 34 * 34 := by native_decide

/-- representative_p4_B42 -/
example : radixRepresentativeBudget 4 42 + radixRepresentativeBudgetPrimeEnvelopeGap 4 42 = radixRepresentativeBudgetPrimeEnvelope 4 42 ∧ radixRepresentativeBudget 4 42 ≤ radixRepresentativeBudgetPrimeEnvelope 4 42 ∧ (radixRepresentativeBudget 4 42 = radixRepresentativeBudgetPrimeEnvelope 4 42 ↔ lastRadixBlockQuotient 4 42 = 0 ∨ lastRadixBlockRemainder 4 42 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 42 ≤ 42 * 42 := by native_decide

/-- representative_p5_B0 -/
example : radixRepresentativeBudget 5 0 + radixRepresentativeBudgetPrimeEnvelopeGap 5 0 = radixRepresentativeBudgetPrimeEnvelope 5 0 ∧ radixRepresentativeBudget 5 0 ≤ radixRepresentativeBudgetPrimeEnvelope 5 0 ∧ (radixRepresentativeBudget 5 0 = radixRepresentativeBudgetPrimeEnvelope 5 0 ↔ lastRadixBlockQuotient 5 0 = 0 ∨ lastRadixBlockRemainder 5 0 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 0 ≤ 0 * 0 := by native_decide

/-- representative_p5_B8 -/
example : radixRepresentativeBudget 5 8 + radixRepresentativeBudgetPrimeEnvelopeGap 5 8 = radixRepresentativeBudgetPrimeEnvelope 5 8 ∧ radixRepresentativeBudget 5 8 ≤ radixRepresentativeBudgetPrimeEnvelope 5 8 ∧ (radixRepresentativeBudget 5 8 = radixRepresentativeBudgetPrimeEnvelope 5 8 ↔ lastRadixBlockQuotient 5 8 = 0 ∨ lastRadixBlockRemainder 5 8 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 8 ≤ 8 * 8 := by native_decide

/-- representative_p5_B16 -/
example : radixRepresentativeBudget 5 16 + radixRepresentativeBudgetPrimeEnvelopeGap 5 16 = radixRepresentativeBudgetPrimeEnvelope 5 16 ∧ radixRepresentativeBudget 5 16 ≤ radixRepresentativeBudgetPrimeEnvelope 5 16 ∧ (radixRepresentativeBudget 5 16 = radixRepresentativeBudgetPrimeEnvelope 5 16 ↔ lastRadixBlockQuotient 5 16 = 0 ∨ lastRadixBlockRemainder 5 16 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 16 ≤ 16 * 16 := by native_decide

/-- representative_p5_B24 -/
example : radixRepresentativeBudget 5 24 + radixRepresentativeBudgetPrimeEnvelopeGap 5 24 = radixRepresentativeBudgetPrimeEnvelope 5 24 ∧ radixRepresentativeBudget 5 24 ≤ radixRepresentativeBudgetPrimeEnvelope 5 24 ∧ (radixRepresentativeBudget 5 24 = radixRepresentativeBudgetPrimeEnvelope 5 24 ↔ lastRadixBlockQuotient 5 24 = 0 ∨ lastRadixBlockRemainder 5 24 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 24 ≤ 24 * 24 := by native_decide

/-- representative_p5_B32 -/
example : radixRepresentativeBudget 5 32 + radixRepresentativeBudgetPrimeEnvelopeGap 5 32 = radixRepresentativeBudgetPrimeEnvelope 5 32 ∧ radixRepresentativeBudget 5 32 ≤ radixRepresentativeBudgetPrimeEnvelope 5 32 ∧ (radixRepresentativeBudget 5 32 = radixRepresentativeBudgetPrimeEnvelope 5 32 ↔ lastRadixBlockQuotient 5 32 = 0 ∨ lastRadixBlockRemainder 5 32 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 32 ≤ 32 * 32 := by native_decide

/-- representative_p5_B40 -/
example : radixRepresentativeBudget 5 40 + radixRepresentativeBudgetPrimeEnvelopeGap 5 40 = radixRepresentativeBudgetPrimeEnvelope 5 40 ∧ radixRepresentativeBudget 5 40 ≤ radixRepresentativeBudgetPrimeEnvelope 5 40 ∧ (radixRepresentativeBudget 5 40 = radixRepresentativeBudgetPrimeEnvelope 5 40 ↔ lastRadixBlockQuotient 5 40 = 0 ∨ lastRadixBlockRemainder 5 40 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 40 ≤ 40 * 40 := by native_decide

/-- representative_p5_B48 -/
example : radixRepresentativeBudget 5 48 + radixRepresentativeBudgetPrimeEnvelopeGap 5 48 = radixRepresentativeBudgetPrimeEnvelope 5 48 ∧ radixRepresentativeBudget 5 48 ≤ radixRepresentativeBudgetPrimeEnvelope 5 48 ∧ (radixRepresentativeBudget 5 48 = radixRepresentativeBudgetPrimeEnvelope 5 48 ↔ lastRadixBlockQuotient 5 48 = 0 ∨ lastRadixBlockRemainder 5 48 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 48 ≤ 48 * 48 := by native_decide

/-- representative_p6_B6 -/
example : radixRepresentativeBudget 6 6 + radixRepresentativeBudgetPrimeEnvelopeGap 6 6 = radixRepresentativeBudgetPrimeEnvelope 6 6 ∧ radixRepresentativeBudget 6 6 ≤ radixRepresentativeBudgetPrimeEnvelope 6 6 ∧ (radixRepresentativeBudget 6 6 = radixRepresentativeBudgetPrimeEnvelope 6 6 ↔ lastRadixBlockQuotient 6 6 = 0 ∨ lastRadixBlockRemainder 6 6 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 6 ≤ 6 * 6 := by native_decide

/-- representative_p6_B14 -/
example : radixRepresentativeBudget 6 14 + radixRepresentativeBudgetPrimeEnvelopeGap 6 14 = radixRepresentativeBudgetPrimeEnvelope 6 14 ∧ radixRepresentativeBudget 6 14 ≤ radixRepresentativeBudgetPrimeEnvelope 6 14 ∧ (radixRepresentativeBudget 6 14 = radixRepresentativeBudgetPrimeEnvelope 6 14 ↔ lastRadixBlockQuotient 6 14 = 0 ∨ lastRadixBlockRemainder 6 14 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 14 ≤ 14 * 14 := by native_decide

/-- representative_p6_B22 -/
example : radixRepresentativeBudget 6 22 + radixRepresentativeBudgetPrimeEnvelopeGap 6 22 = radixRepresentativeBudgetPrimeEnvelope 6 22 ∧ radixRepresentativeBudget 6 22 ≤ radixRepresentativeBudgetPrimeEnvelope 6 22 ∧ (radixRepresentativeBudget 6 22 = radixRepresentativeBudgetPrimeEnvelope 6 22 ↔ lastRadixBlockQuotient 6 22 = 0 ∨ lastRadixBlockRemainder 6 22 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 22 ≤ 22 * 22 := by native_decide

/-- representative_p6_B30 -/
example : radixRepresentativeBudget 6 30 + radixRepresentativeBudgetPrimeEnvelopeGap 6 30 = radixRepresentativeBudgetPrimeEnvelope 6 30 ∧ radixRepresentativeBudget 6 30 ≤ radixRepresentativeBudgetPrimeEnvelope 6 30 ∧ (radixRepresentativeBudget 6 30 = radixRepresentativeBudgetPrimeEnvelope 6 30 ↔ lastRadixBlockQuotient 6 30 = 0 ∨ lastRadixBlockRemainder 6 30 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 30 ≤ 30 * 30 := by native_decide

/-- representative_p6_B38 -/
example : radixRepresentativeBudget 6 38 + radixRepresentativeBudgetPrimeEnvelopeGap 6 38 = radixRepresentativeBudgetPrimeEnvelope 6 38 ∧ radixRepresentativeBudget 6 38 ≤ radixRepresentativeBudgetPrimeEnvelope 6 38 ∧ (radixRepresentativeBudget 6 38 = radixRepresentativeBudgetPrimeEnvelope 6 38 ↔ lastRadixBlockQuotient 6 38 = 0 ∨ lastRadixBlockRemainder 6 38 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 38 ≤ 38 * 38 := by native_decide

/-- representative_p6_B46 -/
example : radixRepresentativeBudget 6 46 + radixRepresentativeBudgetPrimeEnvelopeGap 6 46 = radixRepresentativeBudgetPrimeEnvelope 6 46 ∧ radixRepresentativeBudget 6 46 ≤ radixRepresentativeBudgetPrimeEnvelope 6 46 ∧ (radixRepresentativeBudget 6 46 = radixRepresentativeBudgetPrimeEnvelope 6 46 ↔ lastRadixBlockQuotient 6 46 = 0 ∨ lastRadixBlockRemainder 6 46 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 46 ≤ 46 * 46 := by native_decide

/-- representative_p7_B4 -/
example : radixRepresentativeBudget 7 4 + radixRepresentativeBudgetPrimeEnvelopeGap 7 4 = radixRepresentativeBudgetPrimeEnvelope 7 4 ∧ radixRepresentativeBudget 7 4 ≤ radixRepresentativeBudgetPrimeEnvelope 7 4 ∧ (radixRepresentativeBudget 7 4 = radixRepresentativeBudgetPrimeEnvelope 7 4 ↔ lastRadixBlockQuotient 7 4 = 0 ∨ lastRadixBlockRemainder 7 4 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 4 ≤ 4 * 4 := by native_decide

/-- representative_p7_B12 -/
example : radixRepresentativeBudget 7 12 + radixRepresentativeBudgetPrimeEnvelopeGap 7 12 = radixRepresentativeBudgetPrimeEnvelope 7 12 ∧ radixRepresentativeBudget 7 12 ≤ radixRepresentativeBudgetPrimeEnvelope 7 12 ∧ (radixRepresentativeBudget 7 12 = radixRepresentativeBudgetPrimeEnvelope 7 12 ↔ lastRadixBlockQuotient 7 12 = 0 ∨ lastRadixBlockRemainder 7 12 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 12 ≤ 12 * 12 := by native_decide

/-- representative_p7_B20 -/
example : radixRepresentativeBudget 7 20 + radixRepresentativeBudgetPrimeEnvelopeGap 7 20 = radixRepresentativeBudgetPrimeEnvelope 7 20 ∧ radixRepresentativeBudget 7 20 ≤ radixRepresentativeBudgetPrimeEnvelope 7 20 ∧ (radixRepresentativeBudget 7 20 = radixRepresentativeBudgetPrimeEnvelope 7 20 ↔ lastRadixBlockQuotient 7 20 = 0 ∨ lastRadixBlockRemainder 7 20 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 20 ≤ 20 * 20 := by native_decide

/-- representative_p7_B28 -/
example : radixRepresentativeBudget 7 28 + radixRepresentativeBudgetPrimeEnvelopeGap 7 28 = radixRepresentativeBudgetPrimeEnvelope 7 28 ∧ radixRepresentativeBudget 7 28 ≤ radixRepresentativeBudgetPrimeEnvelope 7 28 ∧ (radixRepresentativeBudget 7 28 = radixRepresentativeBudgetPrimeEnvelope 7 28 ↔ lastRadixBlockQuotient 7 28 = 0 ∨ lastRadixBlockRemainder 7 28 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 28 ≤ 28 * 28 := by native_decide

/-- representative_p7_B36 -/
example : radixRepresentativeBudget 7 36 + radixRepresentativeBudgetPrimeEnvelopeGap 7 36 = radixRepresentativeBudgetPrimeEnvelope 7 36 ∧ radixRepresentativeBudget 7 36 ≤ radixRepresentativeBudgetPrimeEnvelope 7 36 ∧ (radixRepresentativeBudget 7 36 = radixRepresentativeBudgetPrimeEnvelope 7 36 ↔ lastRadixBlockQuotient 7 36 = 0 ∨ lastRadixBlockRemainder 7 36 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 36 ≤ 36 * 36 := by native_decide

/-- representative_p7_B44 -/
example : radixRepresentativeBudget 7 44 + radixRepresentativeBudgetPrimeEnvelopeGap 7 44 = radixRepresentativeBudgetPrimeEnvelope 7 44 ∧ radixRepresentativeBudget 7 44 ≤ radixRepresentativeBudgetPrimeEnvelope 7 44 ∧ (radixRepresentativeBudget 7 44 = radixRepresentativeBudgetPrimeEnvelope 7 44 ↔ lastRadixBlockQuotient 7 44 = 0 ∨ lastRadixBlockRemainder 7 44 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 44 ≤ 44 * 44 := by native_decide

/-- representative_p8_B2 -/
example : radixRepresentativeBudget 8 2 + radixRepresentativeBudgetPrimeEnvelopeGap 8 2 = radixRepresentativeBudgetPrimeEnvelope 8 2 ∧ radixRepresentativeBudget 8 2 ≤ radixRepresentativeBudgetPrimeEnvelope 8 2 ∧ (radixRepresentativeBudget 8 2 = radixRepresentativeBudgetPrimeEnvelope 8 2 ↔ lastRadixBlockQuotient 8 2 = 0 ∨ lastRadixBlockRemainder 8 2 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 2 ≤ 2 * 2 := by native_decide

/-- representative_p8_B10 -/
example : radixRepresentativeBudget 8 10 + radixRepresentativeBudgetPrimeEnvelopeGap 8 10 = radixRepresentativeBudgetPrimeEnvelope 8 10 ∧ radixRepresentativeBudget 8 10 ≤ radixRepresentativeBudgetPrimeEnvelope 8 10 ∧ (radixRepresentativeBudget 8 10 = radixRepresentativeBudgetPrimeEnvelope 8 10 ↔ lastRadixBlockQuotient 8 10 = 0 ∨ lastRadixBlockRemainder 8 10 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 10 ≤ 10 * 10 := by native_decide

/-- representative_p8_B18 -/
example : radixRepresentativeBudget 8 18 + radixRepresentativeBudgetPrimeEnvelopeGap 8 18 = radixRepresentativeBudgetPrimeEnvelope 8 18 ∧ radixRepresentativeBudget 8 18 ≤ radixRepresentativeBudgetPrimeEnvelope 8 18 ∧ (radixRepresentativeBudget 8 18 = radixRepresentativeBudgetPrimeEnvelope 8 18 ↔ lastRadixBlockQuotient 8 18 = 0 ∨ lastRadixBlockRemainder 8 18 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 18 ≤ 18 * 18 := by native_decide

/-- representative_p8_B26 -/
example : radixRepresentativeBudget 8 26 + radixRepresentativeBudgetPrimeEnvelopeGap 8 26 = radixRepresentativeBudgetPrimeEnvelope 8 26 ∧ radixRepresentativeBudget 8 26 ≤ radixRepresentativeBudgetPrimeEnvelope 8 26 ∧ (radixRepresentativeBudget 8 26 = radixRepresentativeBudgetPrimeEnvelope 8 26 ↔ lastRadixBlockQuotient 8 26 = 0 ∨ lastRadixBlockRemainder 8 26 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 26 ≤ 26 * 26 := by native_decide

/-- representative_p8_B34 -/
example : radixRepresentativeBudget 8 34 + radixRepresentativeBudgetPrimeEnvelopeGap 8 34 = radixRepresentativeBudgetPrimeEnvelope 8 34 ∧ radixRepresentativeBudget 8 34 ≤ radixRepresentativeBudgetPrimeEnvelope 8 34 ∧ (radixRepresentativeBudget 8 34 = radixRepresentativeBudgetPrimeEnvelope 8 34 ↔ lastRadixBlockQuotient 8 34 = 0 ∨ lastRadixBlockRemainder 8 34 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 34 ≤ 34 * 34 := by native_decide

/-- representative_p8_B42 -/
example : radixRepresentativeBudget 8 42 + radixRepresentativeBudgetPrimeEnvelopeGap 8 42 = radixRepresentativeBudgetPrimeEnvelope 8 42 ∧ radixRepresentativeBudget 8 42 ≤ radixRepresentativeBudgetPrimeEnvelope 8 42 ∧ (radixRepresentativeBudget 8 42 = radixRepresentativeBudgetPrimeEnvelope 8 42 ↔ lastRadixBlockQuotient 8 42 = 0 ∨ lastRadixBlockRemainder 8 42 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 42 ≤ 42 * 42 := by native_decide

/-- representative_p9_B0 -/
example : radixRepresentativeBudget 9 0 + radixRepresentativeBudgetPrimeEnvelopeGap 9 0 = radixRepresentativeBudgetPrimeEnvelope 9 0 ∧ radixRepresentativeBudget 9 0 ≤ radixRepresentativeBudgetPrimeEnvelope 9 0 ∧ (radixRepresentativeBudget 9 0 = radixRepresentativeBudgetPrimeEnvelope 9 0 ↔ lastRadixBlockQuotient 9 0 = 0 ∨ lastRadixBlockRemainder 9 0 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 0 ≤ 0 * 0 := by native_decide

/-- representative_p9_B8 -/
example : radixRepresentativeBudget 9 8 + radixRepresentativeBudgetPrimeEnvelopeGap 9 8 = radixRepresentativeBudgetPrimeEnvelope 9 8 ∧ radixRepresentativeBudget 9 8 ≤ radixRepresentativeBudgetPrimeEnvelope 9 8 ∧ (radixRepresentativeBudget 9 8 = radixRepresentativeBudgetPrimeEnvelope 9 8 ↔ lastRadixBlockQuotient 9 8 = 0 ∨ lastRadixBlockRemainder 9 8 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 8 ≤ 8 * 8 := by native_decide

/-- representative_p9_B16 -/
example : radixRepresentativeBudget 9 16 + radixRepresentativeBudgetPrimeEnvelopeGap 9 16 = radixRepresentativeBudgetPrimeEnvelope 9 16 ∧ radixRepresentativeBudget 9 16 ≤ radixRepresentativeBudgetPrimeEnvelope 9 16 ∧ (radixRepresentativeBudget 9 16 = radixRepresentativeBudgetPrimeEnvelope 9 16 ↔ lastRadixBlockQuotient 9 16 = 0 ∨ lastRadixBlockRemainder 9 16 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 16 ≤ 16 * 16 := by native_decide

/-- representative_p9_B24 -/
example : radixRepresentativeBudget 9 24 + radixRepresentativeBudgetPrimeEnvelopeGap 9 24 = radixRepresentativeBudgetPrimeEnvelope 9 24 ∧ radixRepresentativeBudget 9 24 ≤ radixRepresentativeBudgetPrimeEnvelope 9 24 ∧ (radixRepresentativeBudget 9 24 = radixRepresentativeBudgetPrimeEnvelope 9 24 ↔ lastRadixBlockQuotient 9 24 = 0 ∨ lastRadixBlockRemainder 9 24 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 24 ≤ 24 * 24 := by native_decide

/-- representative_p9_B32 -/
example : radixRepresentativeBudget 9 32 + radixRepresentativeBudgetPrimeEnvelopeGap 9 32 = radixRepresentativeBudgetPrimeEnvelope 9 32 ∧ radixRepresentativeBudget 9 32 ≤ radixRepresentativeBudgetPrimeEnvelope 9 32 ∧ (radixRepresentativeBudget 9 32 = radixRepresentativeBudgetPrimeEnvelope 9 32 ↔ lastRadixBlockQuotient 9 32 = 0 ∨ lastRadixBlockRemainder 9 32 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 32 ≤ 32 * 32 := by native_decide

/-- representative_p9_B40 -/
example : radixRepresentativeBudget 9 40 + radixRepresentativeBudgetPrimeEnvelopeGap 9 40 = radixRepresentativeBudgetPrimeEnvelope 9 40 ∧ radixRepresentativeBudget 9 40 ≤ radixRepresentativeBudgetPrimeEnvelope 9 40 ∧ (radixRepresentativeBudget 9 40 = radixRepresentativeBudgetPrimeEnvelope 9 40 ↔ lastRadixBlockQuotient 9 40 = 0 ∨ lastRadixBlockRemainder 9 40 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 40 ≤ 40 * 40 := by native_decide

/-- representative_p9_B48 -/
example : radixRepresentativeBudget 9 48 + radixRepresentativeBudgetPrimeEnvelopeGap 9 48 = radixRepresentativeBudgetPrimeEnvelope 9 48 ∧ radixRepresentativeBudget 9 48 ≤ radixRepresentativeBudgetPrimeEnvelope 9 48 ∧ (radixRepresentativeBudget 9 48 = radixRepresentativeBudgetPrimeEnvelope 9 48 ↔ lastRadixBlockQuotient 9 48 = 0 ∨ lastRadixBlockRemainder 9 48 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 48 ≤ 48 * 48 := by native_decide

/-- representative_p10_B6 -/
example : radixRepresentativeBudget 10 6 + radixRepresentativeBudgetPrimeEnvelopeGap 10 6 = radixRepresentativeBudgetPrimeEnvelope 10 6 ∧ radixRepresentativeBudget 10 6 ≤ radixRepresentativeBudgetPrimeEnvelope 10 6 ∧ (radixRepresentativeBudget 10 6 = radixRepresentativeBudgetPrimeEnvelope 10 6 ↔ lastRadixBlockQuotient 10 6 = 0 ∨ lastRadixBlockRemainder 10 6 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 6 ≤ 6 * 6 := by native_decide

/-- representative_p10_B14 -/
example : radixRepresentativeBudget 10 14 + radixRepresentativeBudgetPrimeEnvelopeGap 10 14 = radixRepresentativeBudgetPrimeEnvelope 10 14 ∧ radixRepresentativeBudget 10 14 ≤ radixRepresentativeBudgetPrimeEnvelope 10 14 ∧ (radixRepresentativeBudget 10 14 = radixRepresentativeBudgetPrimeEnvelope 10 14 ↔ lastRadixBlockQuotient 10 14 = 0 ∨ lastRadixBlockRemainder 10 14 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 14 ≤ 14 * 14 := by native_decide

/-- representative_p10_B22 -/
example : radixRepresentativeBudget 10 22 + radixRepresentativeBudgetPrimeEnvelopeGap 10 22 = radixRepresentativeBudgetPrimeEnvelope 10 22 ∧ radixRepresentativeBudget 10 22 ≤ radixRepresentativeBudgetPrimeEnvelope 10 22 ∧ (radixRepresentativeBudget 10 22 = radixRepresentativeBudgetPrimeEnvelope 10 22 ↔ lastRadixBlockQuotient 10 22 = 0 ∨ lastRadixBlockRemainder 10 22 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 22 ≤ 22 * 22 := by native_decide

/-- representative_p10_B30 -/
example : radixRepresentativeBudget 10 30 + radixRepresentativeBudgetPrimeEnvelopeGap 10 30 = radixRepresentativeBudgetPrimeEnvelope 10 30 ∧ radixRepresentativeBudget 10 30 ≤ radixRepresentativeBudgetPrimeEnvelope 10 30 ∧ (radixRepresentativeBudget 10 30 = radixRepresentativeBudgetPrimeEnvelope 10 30 ↔ lastRadixBlockQuotient 10 30 = 0 ∨ lastRadixBlockRemainder 10 30 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 30 ≤ 30 * 30 := by native_decide

/-- representative_p10_B38 -/
example : radixRepresentativeBudget 10 38 + radixRepresentativeBudgetPrimeEnvelopeGap 10 38 = radixRepresentativeBudgetPrimeEnvelope 10 38 ∧ radixRepresentativeBudget 10 38 ≤ radixRepresentativeBudgetPrimeEnvelope 10 38 ∧ (radixRepresentativeBudget 10 38 = radixRepresentativeBudgetPrimeEnvelope 10 38 ↔ lastRadixBlockQuotient 10 38 = 0 ∨ lastRadixBlockRemainder 10 38 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 38 ≤ 38 * 38 := by native_decide

/-- representative_p10_B46 -/
example : radixRepresentativeBudget 10 46 + radixRepresentativeBudgetPrimeEnvelopeGap 10 46 = radixRepresentativeBudgetPrimeEnvelope 10 46 ∧ radixRepresentativeBudget 10 46 ≤ radixRepresentativeBudgetPrimeEnvelope 10 46 ∧ (radixRepresentativeBudget 10 46 = radixRepresentativeBudgetPrimeEnvelope 10 46 ↔ lastRadixBlockQuotient 10 46 = 0 ∨ lastRadixBlockRemainder 10 46 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 46 ≤ 46 * 46 := by native_decide

/-- representative_p11_B4 -/
example : radixRepresentativeBudget 11 4 + radixRepresentativeBudgetPrimeEnvelopeGap 11 4 = radixRepresentativeBudgetPrimeEnvelope 11 4 ∧ radixRepresentativeBudget 11 4 ≤ radixRepresentativeBudgetPrimeEnvelope 11 4 ∧ (radixRepresentativeBudget 11 4 = radixRepresentativeBudgetPrimeEnvelope 11 4 ↔ lastRadixBlockQuotient 11 4 = 0 ∨ lastRadixBlockRemainder 11 4 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 4 ≤ 4 * 4 := by native_decide

/-- representative_p11_B12 -/
example : radixRepresentativeBudget 11 12 + radixRepresentativeBudgetPrimeEnvelopeGap 11 12 = radixRepresentativeBudgetPrimeEnvelope 11 12 ∧ radixRepresentativeBudget 11 12 ≤ radixRepresentativeBudgetPrimeEnvelope 11 12 ∧ (radixRepresentativeBudget 11 12 = radixRepresentativeBudgetPrimeEnvelope 11 12 ↔ lastRadixBlockQuotient 11 12 = 0 ∨ lastRadixBlockRemainder 11 12 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 12 ≤ 12 * 12 := by native_decide

/-- representative_p11_B20 -/
example : radixRepresentativeBudget 11 20 + radixRepresentativeBudgetPrimeEnvelopeGap 11 20 = radixRepresentativeBudgetPrimeEnvelope 11 20 ∧ radixRepresentativeBudget 11 20 ≤ radixRepresentativeBudgetPrimeEnvelope 11 20 ∧ (radixRepresentativeBudget 11 20 = radixRepresentativeBudgetPrimeEnvelope 11 20 ↔ lastRadixBlockQuotient 11 20 = 0 ∨ lastRadixBlockRemainder 11 20 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 20 ≤ 20 * 20 := by native_decide

/-- representative_p11_B28 -/
example : radixRepresentativeBudget 11 28 + radixRepresentativeBudgetPrimeEnvelopeGap 11 28 = radixRepresentativeBudgetPrimeEnvelope 11 28 ∧ radixRepresentativeBudget 11 28 ≤ radixRepresentativeBudgetPrimeEnvelope 11 28 ∧ (radixRepresentativeBudget 11 28 = radixRepresentativeBudgetPrimeEnvelope 11 28 ↔ lastRadixBlockQuotient 11 28 = 0 ∨ lastRadixBlockRemainder 11 28 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 28 ≤ 28 * 28 := by native_decide

/-- representative_p11_B36 -/
example : radixRepresentativeBudget 11 36 + radixRepresentativeBudgetPrimeEnvelopeGap 11 36 = radixRepresentativeBudgetPrimeEnvelope 11 36 ∧ radixRepresentativeBudget 11 36 ≤ radixRepresentativeBudgetPrimeEnvelope 11 36 ∧ (radixRepresentativeBudget 11 36 = radixRepresentativeBudgetPrimeEnvelope 11 36 ↔ lastRadixBlockQuotient 11 36 = 0 ∨ lastRadixBlockRemainder 11 36 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 36 ≤ 36 * 36 := by native_decide

/-- representative_p11_B44 -/
example : radixRepresentativeBudget 11 44 + radixRepresentativeBudgetPrimeEnvelopeGap 11 44 = radixRepresentativeBudgetPrimeEnvelope 11 44 ∧ radixRepresentativeBudget 11 44 ≤ radixRepresentativeBudgetPrimeEnvelope 11 44 ∧ (radixRepresentativeBudget 11 44 = radixRepresentativeBudgetPrimeEnvelope 11 44 ↔ lastRadixBlockQuotient 11 44 = 0 ∨ lastRadixBlockRemainder 11 44 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 44 ≤ 44 * 44 := by native_decide

/-- representative_p12_B2 -/
example : radixRepresentativeBudget 12 2 + radixRepresentativeBudgetPrimeEnvelopeGap 12 2 = radixRepresentativeBudgetPrimeEnvelope 12 2 ∧ radixRepresentativeBudget 12 2 ≤ radixRepresentativeBudgetPrimeEnvelope 12 2 ∧ (radixRepresentativeBudget 12 2 = radixRepresentativeBudgetPrimeEnvelope 12 2 ↔ lastRadixBlockQuotient 12 2 = 0 ∨ lastRadixBlockRemainder 12 2 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 2 ≤ 2 * 2 := by native_decide

/-- representative_p12_B10 -/
example : radixRepresentativeBudget 12 10 + radixRepresentativeBudgetPrimeEnvelopeGap 12 10 = radixRepresentativeBudgetPrimeEnvelope 12 10 ∧ radixRepresentativeBudget 12 10 ≤ radixRepresentativeBudgetPrimeEnvelope 12 10 ∧ (radixRepresentativeBudget 12 10 = radixRepresentativeBudgetPrimeEnvelope 12 10 ↔ lastRadixBlockQuotient 12 10 = 0 ∨ lastRadixBlockRemainder 12 10 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 10 ≤ 10 * 10 := by native_decide

/-- representative_p12_B18 -/
example : radixRepresentativeBudget 12 18 + radixRepresentativeBudgetPrimeEnvelopeGap 12 18 = radixRepresentativeBudgetPrimeEnvelope 12 18 ∧ radixRepresentativeBudget 12 18 ≤ radixRepresentativeBudgetPrimeEnvelope 12 18 ∧ (radixRepresentativeBudget 12 18 = radixRepresentativeBudgetPrimeEnvelope 12 18 ↔ lastRadixBlockQuotient 12 18 = 0 ∨ lastRadixBlockRemainder 12 18 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 18 ≤ 18 * 18 := by native_decide

/-- representative_p12_B26 -/
example : radixRepresentativeBudget 12 26 + radixRepresentativeBudgetPrimeEnvelopeGap 12 26 = radixRepresentativeBudgetPrimeEnvelope 12 26 ∧ radixRepresentativeBudget 12 26 ≤ radixRepresentativeBudgetPrimeEnvelope 12 26 ∧ (radixRepresentativeBudget 12 26 = radixRepresentativeBudgetPrimeEnvelope 12 26 ↔ lastRadixBlockQuotient 12 26 = 0 ∨ lastRadixBlockRemainder 12 26 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 26 ≤ 26 * 26 := by native_decide

/-- representative_p12_B34 -/
example : radixRepresentativeBudget 12 34 + radixRepresentativeBudgetPrimeEnvelopeGap 12 34 = radixRepresentativeBudgetPrimeEnvelope 12 34 ∧ radixRepresentativeBudget 12 34 ≤ radixRepresentativeBudgetPrimeEnvelope 12 34 ∧ (radixRepresentativeBudget 12 34 = radixRepresentativeBudgetPrimeEnvelope 12 34 ↔ lastRadixBlockQuotient 12 34 = 0 ∨ lastRadixBlockRemainder 12 34 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 34 ≤ 34 * 34 := by native_decide

/-- representative_p12_B42 -/
example : radixRepresentativeBudget 12 42 + radixRepresentativeBudgetPrimeEnvelopeGap 12 42 = radixRepresentativeBudgetPrimeEnvelope 12 42 ∧ radixRepresentativeBudget 12 42 ≤ radixRepresentativeBudgetPrimeEnvelope 12 42 ∧ (radixRepresentativeBudget 12 42 = radixRepresentativeBudgetPrimeEnvelope 12 42 ↔ lastRadixBlockQuotient 12 42 = 0 ∨ lastRadixBlockRemainder 12 42 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 42 ≤ 42 * 42 := by native_decide

/-- zero_base_B0 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 0 ≤ 0 * 0 := by native_decide

/-- zero_base_B8 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 8 ≤ 8 * 8 := by native_decide

/-- zero_base_B16 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 16 ≤ 16 * 16 := by native_decide

/-- zero_base_B24 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 24 ≤ 24 * 24 := by native_decide

/-- zero_base_B32 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 32 ≤ 32 * 32 := by native_decide

/-- zero_base_B40 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 40 ≤ 40 * 40 := by native_decide

/-- zero_base_B48 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 48 ≤ 48 * 48 := by native_decide

/-- zero_base_B56 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 56 ≤ 56 * 56 := by native_decide

/-- zero_base_B64 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 64 ≤ 64 * 64 := by native_decide

/-- zero_base_B72 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 72 ≤ 72 * 72 := by native_decide

/-- zero_base_B80 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 80 ≤ 80 * 80 := by native_decide

/-- zero_base_B88 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 88 ≤ 88 * 88 := by native_decide

/-- zero_base_B96 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 96 ≤ 96 * 96 := by native_decide

/-- zero_base_B104 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 104 ≤ 104 * 104 := by native_decide

/-- zero_base_B112 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 112 ≤ 112 * 112 := by native_decide

/-- zero_base_B120 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 120 ≤ 120 * 120 := by native_decide

/-- zero_base_B128 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 128 ≤ 128 * 128 := by native_decide

/-- zero_base_B136 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 136 ≤ 136 * 136 := by native_decide

/-- zero_base_B144 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 144 ≤ 144 * 144 := by native_decide

/-- zero_base_B152 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 152 ≤ 152 * 152 := by native_decide

/-- zero_base_B160 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 160 ≤ 160 * 160 := by native_decide

/-- zero_base_B168 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 168 ≤ 168 * 168 := by native_decide

/-- zero_base_B176 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 176 ≤ 176 * 176 := by native_decide

/-- zero_base_B184 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 184 ≤ 184 * 184 := by native_decide

/-- zero_base_B192 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 192 ≤ 192 * 192 := by native_decide

/-- compiler_p2_r1_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 1 0 + maximumLayerCompilerPrimeEnvelopeGap 2 1 0 = maximumLayerCompilerPrimeEnvelopeBound 2 1 0 ∧ maximumLayerCompilerTotalTests 2 1 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 1 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 1 0 ≤ maximumLayerCompilerTestBound 2 1 0 := by native_decide

/-- compiler_p2_r3_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 3 2 + maximumLayerCompilerPrimeEnvelopeGap 2 3 2 = maximumLayerCompilerPrimeEnvelopeBound 2 3 2 ∧ maximumLayerCompilerTotalTests 2 3 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 3 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 3 2 ≤ maximumLayerCompilerTestBound 2 3 2 := by native_decide

/-- compiler_p2_r6_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 6 1 + maximumLayerCompilerPrimeEnvelopeGap 2 6 1 = maximumLayerCompilerPrimeEnvelopeBound 2 6 1 ∧ maximumLayerCompilerTotalTests 2 6 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 6 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 6 1 ≤ maximumLayerCompilerTestBound 2 6 1 := by native_decide

/-- compiler_p2_r9_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 9 0 + maximumLayerCompilerPrimeEnvelopeGap 2 9 0 = maximumLayerCompilerPrimeEnvelopeBound 2 9 0 ∧ maximumLayerCompilerTotalTests 2 9 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 9 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 9 0 ≤ maximumLayerCompilerTestBound 2 9 0 := by native_decide

/-- compiler_p2_r11_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 11 2 + maximumLayerCompilerPrimeEnvelopeGap 2 11 2 = maximumLayerCompilerPrimeEnvelopeBound 2 11 2 ∧ maximumLayerCompilerTotalTests 2 11 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 11 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 11 2 ≤ maximumLayerCompilerTestBound 2 11 2 := by native_decide

/-- compiler_p2_r14_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 14 1 + maximumLayerCompilerPrimeEnvelopeGap 2 14 1 = maximumLayerCompilerPrimeEnvelopeBound 2 14 1 ∧ maximumLayerCompilerTotalTests 2 14 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 14 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 14 1 ≤ maximumLayerCompilerTestBound 2 14 1 := by native_decide

/-- compiler_p2_r17_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 17 0 + maximumLayerCompilerPrimeEnvelopeGap 2 17 0 = maximumLayerCompilerPrimeEnvelopeBound 2 17 0 ∧ maximumLayerCompilerTotalTests 2 17 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 17 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 17 0 ≤ maximumLayerCompilerTestBound 2 17 0 := by native_decide

/-- compiler_p2_r19_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 19 2 + maximumLayerCompilerPrimeEnvelopeGap 2 19 2 = maximumLayerCompilerPrimeEnvelopeBound 2 19 2 ∧ maximumLayerCompilerTotalTests 2 19 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 19 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 19 2 ≤ maximumLayerCompilerTestBound 2 19 2 := by native_decide

/-- compiler_p3_r2_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 2 1 + maximumLayerCompilerPrimeEnvelopeGap 3 2 1 = maximumLayerCompilerPrimeEnvelopeBound 3 2 1 ∧ maximumLayerCompilerTotalTests 3 2 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 2 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 2 1 ≤ maximumLayerCompilerTestBound 3 2 1 := by native_decide

/-- compiler_p3_r5_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 5 0 + maximumLayerCompilerPrimeEnvelopeGap 3 5 0 = maximumLayerCompilerPrimeEnvelopeBound 3 5 0 ∧ maximumLayerCompilerTotalTests 3 5 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 5 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 5 0 ≤ maximumLayerCompilerTestBound 3 5 0 := by native_decide

/-- compiler_p3_r7_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 7 2 + maximumLayerCompilerPrimeEnvelopeGap 3 7 2 = maximumLayerCompilerPrimeEnvelopeBound 3 7 2 ∧ maximumLayerCompilerTotalTests 3 7 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 7 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 7 2 ≤ maximumLayerCompilerTestBound 3 7 2 := by native_decide

/-- compiler_p3_r10_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 10 1 + maximumLayerCompilerPrimeEnvelopeGap 3 10 1 = maximumLayerCompilerPrimeEnvelopeBound 3 10 1 ∧ maximumLayerCompilerTotalTests 3 10 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 10 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 10 1 ≤ maximumLayerCompilerTestBound 3 10 1 := by native_decide

/-- compiler_p3_r13_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 13 0 + maximumLayerCompilerPrimeEnvelopeGap 3 13 0 = maximumLayerCompilerPrimeEnvelopeBound 3 13 0 ∧ maximumLayerCompilerTotalTests 3 13 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 13 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 13 0 ≤ maximumLayerCompilerTestBound 3 13 0 := by native_decide

/-- compiler_p3_r15_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 15 2 + maximumLayerCompilerPrimeEnvelopeGap 3 15 2 = maximumLayerCompilerPrimeEnvelopeBound 3 15 2 ∧ maximumLayerCompilerTotalTests 3 15 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 15 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 15 2 ≤ maximumLayerCompilerTestBound 3 15 2 := by native_decide

/-- compiler_p3_r18_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 18 1 + maximumLayerCompilerPrimeEnvelopeGap 3 18 1 = maximumLayerCompilerPrimeEnvelopeBound 3 18 1 ∧ maximumLayerCompilerTotalTests 3 18 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 18 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 18 1 ≤ maximumLayerCompilerTestBound 3 18 1 := by native_decide

/-- compiler_p5_r1_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 1 0 + maximumLayerCompilerPrimeEnvelopeGap 5 1 0 = maximumLayerCompilerPrimeEnvelopeBound 5 1 0 ∧ maximumLayerCompilerTotalTests 5 1 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 1 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 1 0 ≤ maximumLayerCompilerTestBound 5 1 0 := by native_decide

/-- compiler_p5_r3_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 3 2 + maximumLayerCompilerPrimeEnvelopeGap 5 3 2 = maximumLayerCompilerPrimeEnvelopeBound 5 3 2 ∧ maximumLayerCompilerTotalTests 5 3 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 3 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 3 2 ≤ maximumLayerCompilerTestBound 5 3 2 := by native_decide

/-- compiler_p5_r6_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 6 1 + maximumLayerCompilerPrimeEnvelopeGap 5 6 1 = maximumLayerCompilerPrimeEnvelopeBound 5 6 1 ∧ maximumLayerCompilerTotalTests 5 6 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 6 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 6 1 ≤ maximumLayerCompilerTestBound 5 6 1 := by native_decide

/-- compiler_p5_r9_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 9 0 + maximumLayerCompilerPrimeEnvelopeGap 5 9 0 = maximumLayerCompilerPrimeEnvelopeBound 5 9 0 ∧ maximumLayerCompilerTotalTests 5 9 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 9 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 9 0 ≤ maximumLayerCompilerTestBound 5 9 0 := by native_decide

/-- compiler_p5_r11_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 11 2 + maximumLayerCompilerPrimeEnvelopeGap 5 11 2 = maximumLayerCompilerPrimeEnvelopeBound 5 11 2 ∧ maximumLayerCompilerTotalTests 5 11 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 11 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 11 2 ≤ maximumLayerCompilerTestBound 5 11 2 := by native_decide

/-- compiler_p5_r14_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 14 1 + maximumLayerCompilerPrimeEnvelopeGap 5 14 1 = maximumLayerCompilerPrimeEnvelopeBound 5 14 1 ∧ maximumLayerCompilerTotalTests 5 14 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 14 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 14 1 ≤ maximumLayerCompilerTestBound 5 14 1 := by native_decide

/-- compiler_p5_r17_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 17 0 + maximumLayerCompilerPrimeEnvelopeGap 5 17 0 = maximumLayerCompilerPrimeEnvelopeBound 5 17 0 ∧ maximumLayerCompilerTotalTests 5 17 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 17 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 17 0 ≤ maximumLayerCompilerTestBound 5 17 0 := by native_decide

/-- compiler_p5_r19_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 19 2 + maximumLayerCompilerPrimeEnvelopeGap 5 19 2 = maximumLayerCompilerPrimeEnvelopeBound 5 19 2 ∧ maximumLayerCompilerTotalTests 5 19 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 19 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 19 2 ≤ maximumLayerCompilerTestBound 5 19 2 := by native_decide

/-- compiler_p7_r2_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 2 1 + maximumLayerCompilerPrimeEnvelopeGap 7 2 1 = maximumLayerCompilerPrimeEnvelopeBound 7 2 1 ∧ maximumLayerCompilerTotalTests 7 2 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 2 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 2 1 ≤ maximumLayerCompilerTestBound 7 2 1 := by native_decide

/-- compiler_p7_r5_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 5 0 + maximumLayerCompilerPrimeEnvelopeGap 7 5 0 = maximumLayerCompilerPrimeEnvelopeBound 7 5 0 ∧ maximumLayerCompilerTotalTests 7 5 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 5 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 5 0 ≤ maximumLayerCompilerTestBound 7 5 0 := by native_decide

/-- compiler_p7_r7_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 7 2 + maximumLayerCompilerPrimeEnvelopeGap 7 7 2 = maximumLayerCompilerPrimeEnvelopeBound 7 7 2 ∧ maximumLayerCompilerTotalTests 7 7 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 7 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 7 2 ≤ maximumLayerCompilerTestBound 7 7 2 := by native_decide

/-- compiler_p7_r10_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 10 1 + maximumLayerCompilerPrimeEnvelopeGap 7 10 1 = maximumLayerCompilerPrimeEnvelopeBound 7 10 1 ∧ maximumLayerCompilerTotalTests 7 10 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 10 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 10 1 ≤ maximumLayerCompilerTestBound 7 10 1 := by native_decide

/-- compiler_p7_r13_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 13 0 + maximumLayerCompilerPrimeEnvelopeGap 7 13 0 = maximumLayerCompilerPrimeEnvelopeBound 7 13 0 ∧ maximumLayerCompilerTotalTests 7 13 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 13 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 13 0 ≤ maximumLayerCompilerTestBound 7 13 0 := by native_decide

/-- compiler_p7_r15_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 15 2 + maximumLayerCompilerPrimeEnvelopeGap 7 15 2 = maximumLayerCompilerPrimeEnvelopeBound 7 15 2 ∧ maximumLayerCompilerTotalTests 7 15 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 15 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 15 2 ≤ maximumLayerCompilerTestBound 7 15 2 := by native_decide

/-- compiler_p7_r18_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 18 1 + maximumLayerCompilerPrimeEnvelopeGap 7 18 1 = maximumLayerCompilerPrimeEnvelopeBound 7 18 1 ∧ maximumLayerCompilerTotalTests 7 18 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 18 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 18 1 ≤ maximumLayerCompilerTestBound 7 18 1 := by native_decide

/-- compiler_p11_r1_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 1 0 + maximumLayerCompilerPrimeEnvelopeGap 11 1 0 = maximumLayerCompilerPrimeEnvelopeBound 11 1 0 ∧ maximumLayerCompilerTotalTests 11 1 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 1 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 1 0 ≤ maximumLayerCompilerTestBound 11 1 0 := by native_decide

/-- compiler_p11_r3_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 3 2 + maximumLayerCompilerPrimeEnvelopeGap 11 3 2 = maximumLayerCompilerPrimeEnvelopeBound 11 3 2 ∧ maximumLayerCompilerTotalTests 11 3 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 3 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 3 2 ≤ maximumLayerCompilerTestBound 11 3 2 := by native_decide

/-- compiler_p11_r6_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 6 1 + maximumLayerCompilerPrimeEnvelopeGap 11 6 1 = maximumLayerCompilerPrimeEnvelopeBound 11 6 1 ∧ maximumLayerCompilerTotalTests 11 6 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 6 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 6 1 ≤ maximumLayerCompilerTestBound 11 6 1 := by native_decide

/-- compiler_p11_r9_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 9 0 + maximumLayerCompilerPrimeEnvelopeGap 11 9 0 = maximumLayerCompilerPrimeEnvelopeBound 11 9 0 ∧ maximumLayerCompilerTotalTests 11 9 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 9 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 9 0 ≤ maximumLayerCompilerTestBound 11 9 0 := by native_decide

/-- compiler_p11_r11_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 11 2 + maximumLayerCompilerPrimeEnvelopeGap 11 11 2 = maximumLayerCompilerPrimeEnvelopeBound 11 11 2 ∧ maximumLayerCompilerTotalTests 11 11 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 11 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 11 2 ≤ maximumLayerCompilerTestBound 11 11 2 := by native_decide

/-- compiler_p11_r14_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 14 1 + maximumLayerCompilerPrimeEnvelopeGap 11 14 1 = maximumLayerCompilerPrimeEnvelopeBound 11 14 1 ∧ maximumLayerCompilerTotalTests 11 14 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 14 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 14 1 ≤ maximumLayerCompilerTestBound 11 14 1 := by native_decide

/-- compiler_p11_r17_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 17 0 + maximumLayerCompilerPrimeEnvelopeGap 11 17 0 = maximumLayerCompilerPrimeEnvelopeBound 11 17 0 ∧ maximumLayerCompilerTotalTests 11 17 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 17 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 17 0 ≤ maximumLayerCompilerTestBound 11 17 0 := by native_decide

/-- compiler_p11_r19_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 19 2 + maximumLayerCompilerPrimeEnvelopeGap 11 19 2 = maximumLayerCompilerPrimeEnvelopeBound 11 19 2 ∧ maximumLayerCompilerTotalTests 11 19 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 19 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 19 2 ≤ maximumLayerCompilerTestBound 11 19 2 := by native_decide

/-- compiler_p13_r2_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 2 1 + maximumLayerCompilerPrimeEnvelopeGap 13 2 1 = maximumLayerCompilerPrimeEnvelopeBound 13 2 1 ∧ maximumLayerCompilerTotalTests 13 2 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 2 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 2 1 ≤ maximumLayerCompilerTestBound 13 2 1 := by native_decide

/-- compiler_p13_r5_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 5 0 + maximumLayerCompilerPrimeEnvelopeGap 13 5 0 = maximumLayerCompilerPrimeEnvelopeBound 13 5 0 ∧ maximumLayerCompilerTotalTests 13 5 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 5 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 5 0 ≤ maximumLayerCompilerTestBound 13 5 0 := by native_decide

/-- compiler_p13_r7_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 7 2 + maximumLayerCompilerPrimeEnvelopeGap 13 7 2 = maximumLayerCompilerPrimeEnvelopeBound 13 7 2 ∧ maximumLayerCompilerTotalTests 13 7 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 7 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 7 2 ≤ maximumLayerCompilerTestBound 13 7 2 := by native_decide

/-- compiler_p13_r10_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 10 1 + maximumLayerCompilerPrimeEnvelopeGap 13 10 1 = maximumLayerCompilerPrimeEnvelopeBound 13 10 1 ∧ maximumLayerCompilerTotalTests 13 10 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 10 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 10 1 ≤ maximumLayerCompilerTestBound 13 10 1 := by native_decide

/-- compiler_p13_r13_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 13 0 + maximumLayerCompilerPrimeEnvelopeGap 13 13 0 = maximumLayerCompilerPrimeEnvelopeBound 13 13 0 ∧ maximumLayerCompilerTotalTests 13 13 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 13 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 13 0 ≤ maximumLayerCompilerTestBound 13 13 0 := by native_decide

/-- compiler_p13_r15_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 15 2 + maximumLayerCompilerPrimeEnvelopeGap 13 15 2 = maximumLayerCompilerPrimeEnvelopeBound 13 15 2 ∧ maximumLayerCompilerTotalTests 13 15 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 15 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 15 2 ≤ maximumLayerCompilerTestBound 13 15 2 := by native_decide

/-- compiler_p13_r18_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 18 1 + maximumLayerCompilerPrimeEnvelopeGap 13 18 1 = maximumLayerCompilerPrimeEnvelopeBound 13 18 1 ∧ maximumLayerCompilerTotalTests 13 18 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 18 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 18 1 ≤ maximumLayerCompilerTestBound 13 18 1 := by native_decide

end KomorebiPadic
