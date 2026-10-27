import KomorebiPadic

namespace KomorebiPadic

/-- representative_p1_B7 -/
example : radixRepresentativeBudget 1 7 + radixRepresentativeBudgetPrimeEnvelopeGap 1 7 = radixRepresentativeBudgetPrimeEnvelope 1 7 ∧ radixRepresentativeBudget 1 7 ≤ radixRepresentativeBudgetPrimeEnvelope 1 7 ∧ (radixRepresentativeBudget 1 7 = radixRepresentativeBudgetPrimeEnvelope 1 7 ↔ lastRadixBlockQuotient 1 7 = 0 ∨ lastRadixBlockRemainder 1 7 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 7 ≤ 7 * 7 := by native_decide

/-- representative_p1_B15 -/
example : radixRepresentativeBudget 1 15 + radixRepresentativeBudgetPrimeEnvelopeGap 1 15 = radixRepresentativeBudgetPrimeEnvelope 1 15 ∧ radixRepresentativeBudget 1 15 ≤ radixRepresentativeBudgetPrimeEnvelope 1 15 ∧ (radixRepresentativeBudget 1 15 = radixRepresentativeBudgetPrimeEnvelope 1 15 ↔ lastRadixBlockQuotient 1 15 = 0 ∨ lastRadixBlockRemainder 1 15 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 15 ≤ 15 * 15 := by native_decide

/-- representative_p1_B23 -/
example : radixRepresentativeBudget 1 23 + radixRepresentativeBudgetPrimeEnvelopeGap 1 23 = radixRepresentativeBudgetPrimeEnvelope 1 23 ∧ radixRepresentativeBudget 1 23 ≤ radixRepresentativeBudgetPrimeEnvelope 1 23 ∧ (radixRepresentativeBudget 1 23 = radixRepresentativeBudgetPrimeEnvelope 1 23 ↔ lastRadixBlockQuotient 1 23 = 0 ∨ lastRadixBlockRemainder 1 23 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 23 ≤ 23 * 23 := by native_decide

/-- representative_p1_B31 -/
example : radixRepresentativeBudget 1 31 + radixRepresentativeBudgetPrimeEnvelopeGap 1 31 = radixRepresentativeBudgetPrimeEnvelope 1 31 ∧ radixRepresentativeBudget 1 31 ≤ radixRepresentativeBudgetPrimeEnvelope 1 31 ∧ (radixRepresentativeBudget 1 31 = radixRepresentativeBudgetPrimeEnvelope 1 31 ↔ lastRadixBlockQuotient 1 31 = 0 ∨ lastRadixBlockRemainder 1 31 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 31 ≤ 31 * 31 := by native_decide

/-- representative_p1_B39 -/
example : radixRepresentativeBudget 1 39 + radixRepresentativeBudgetPrimeEnvelopeGap 1 39 = radixRepresentativeBudgetPrimeEnvelope 1 39 ∧ radixRepresentativeBudget 1 39 ≤ radixRepresentativeBudgetPrimeEnvelope 1 39 ∧ (radixRepresentativeBudget 1 39 = radixRepresentativeBudgetPrimeEnvelope 1 39 ↔ lastRadixBlockQuotient 1 39 = 0 ∨ lastRadixBlockRemainder 1 39 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 39 ≤ 39 * 39 := by native_decide

/-- representative_p1_B47 -/
example : radixRepresentativeBudget 1 47 + radixRepresentativeBudgetPrimeEnvelopeGap 1 47 = radixRepresentativeBudgetPrimeEnvelope 1 47 ∧ radixRepresentativeBudget 1 47 ≤ radixRepresentativeBudgetPrimeEnvelope 1 47 ∧ (radixRepresentativeBudget 1 47 = radixRepresentativeBudgetPrimeEnvelope 1 47 ↔ lastRadixBlockQuotient 1 47 = 0 ∨ lastRadixBlockRemainder 1 47 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 47 ≤ 47 * 47 := by native_decide

/-- representative_p2_B5 -/
example : radixRepresentativeBudget 2 5 + radixRepresentativeBudgetPrimeEnvelopeGap 2 5 = radixRepresentativeBudgetPrimeEnvelope 2 5 ∧ radixRepresentativeBudget 2 5 ≤ radixRepresentativeBudgetPrimeEnvelope 2 5 ∧ (radixRepresentativeBudget 2 5 = radixRepresentativeBudgetPrimeEnvelope 2 5 ↔ lastRadixBlockQuotient 2 5 = 0 ∨ lastRadixBlockRemainder 2 5 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 5 ≤ 5 * 5 := by native_decide

/-- representative_p2_B13 -/
example : radixRepresentativeBudget 2 13 + radixRepresentativeBudgetPrimeEnvelopeGap 2 13 = radixRepresentativeBudgetPrimeEnvelope 2 13 ∧ radixRepresentativeBudget 2 13 ≤ radixRepresentativeBudgetPrimeEnvelope 2 13 ∧ (radixRepresentativeBudget 2 13 = radixRepresentativeBudgetPrimeEnvelope 2 13 ↔ lastRadixBlockQuotient 2 13 = 0 ∨ lastRadixBlockRemainder 2 13 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 13 ≤ 13 * 13 := by native_decide

/-- representative_p2_B21 -/
example : radixRepresentativeBudget 2 21 + radixRepresentativeBudgetPrimeEnvelopeGap 2 21 = radixRepresentativeBudgetPrimeEnvelope 2 21 ∧ radixRepresentativeBudget 2 21 ≤ radixRepresentativeBudgetPrimeEnvelope 2 21 ∧ (radixRepresentativeBudget 2 21 = radixRepresentativeBudgetPrimeEnvelope 2 21 ↔ lastRadixBlockQuotient 2 21 = 0 ∨ lastRadixBlockRemainder 2 21 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 21 ≤ 21 * 21 := by native_decide

/-- representative_p2_B29 -/
example : radixRepresentativeBudget 2 29 + radixRepresentativeBudgetPrimeEnvelopeGap 2 29 = radixRepresentativeBudgetPrimeEnvelope 2 29 ∧ radixRepresentativeBudget 2 29 ≤ radixRepresentativeBudgetPrimeEnvelope 2 29 ∧ (radixRepresentativeBudget 2 29 = radixRepresentativeBudgetPrimeEnvelope 2 29 ↔ lastRadixBlockQuotient 2 29 = 0 ∨ lastRadixBlockRemainder 2 29 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 29 ≤ 29 * 29 := by native_decide

/-- representative_p2_B37 -/
example : radixRepresentativeBudget 2 37 + radixRepresentativeBudgetPrimeEnvelopeGap 2 37 = radixRepresentativeBudgetPrimeEnvelope 2 37 ∧ radixRepresentativeBudget 2 37 ≤ radixRepresentativeBudgetPrimeEnvelope 2 37 ∧ (radixRepresentativeBudget 2 37 = radixRepresentativeBudgetPrimeEnvelope 2 37 ↔ lastRadixBlockQuotient 2 37 = 0 ∨ lastRadixBlockRemainder 2 37 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 37 ≤ 37 * 37 := by native_decide

/-- representative_p2_B45 -/
example : radixRepresentativeBudget 2 45 + radixRepresentativeBudgetPrimeEnvelopeGap 2 45 = radixRepresentativeBudgetPrimeEnvelope 2 45 ∧ radixRepresentativeBudget 2 45 ≤ radixRepresentativeBudgetPrimeEnvelope 2 45 ∧ (radixRepresentativeBudget 2 45 = radixRepresentativeBudgetPrimeEnvelope 2 45 ↔ lastRadixBlockQuotient 2 45 = 0 ∨ lastRadixBlockRemainder 2 45 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 45 ≤ 45 * 45 := by native_decide

/-- representative_p3_B3 -/
example : radixRepresentativeBudget 3 3 + radixRepresentativeBudgetPrimeEnvelopeGap 3 3 = radixRepresentativeBudgetPrimeEnvelope 3 3 ∧ radixRepresentativeBudget 3 3 ≤ radixRepresentativeBudgetPrimeEnvelope 3 3 ∧ (radixRepresentativeBudget 3 3 = radixRepresentativeBudgetPrimeEnvelope 3 3 ↔ lastRadixBlockQuotient 3 3 = 0 ∨ lastRadixBlockRemainder 3 3 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 3 ≤ 3 * 3 := by native_decide

/-- representative_p3_B11 -/
example : radixRepresentativeBudget 3 11 + radixRepresentativeBudgetPrimeEnvelopeGap 3 11 = radixRepresentativeBudgetPrimeEnvelope 3 11 ∧ radixRepresentativeBudget 3 11 ≤ radixRepresentativeBudgetPrimeEnvelope 3 11 ∧ (radixRepresentativeBudget 3 11 = radixRepresentativeBudgetPrimeEnvelope 3 11 ↔ lastRadixBlockQuotient 3 11 = 0 ∨ lastRadixBlockRemainder 3 11 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 11 ≤ 11 * 11 := by native_decide

/-- representative_p3_B19 -/
example : radixRepresentativeBudget 3 19 + radixRepresentativeBudgetPrimeEnvelopeGap 3 19 = radixRepresentativeBudgetPrimeEnvelope 3 19 ∧ radixRepresentativeBudget 3 19 ≤ radixRepresentativeBudgetPrimeEnvelope 3 19 ∧ (radixRepresentativeBudget 3 19 = radixRepresentativeBudgetPrimeEnvelope 3 19 ↔ lastRadixBlockQuotient 3 19 = 0 ∨ lastRadixBlockRemainder 3 19 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 19 ≤ 19 * 19 := by native_decide

/-- representative_p3_B27 -/
example : radixRepresentativeBudget 3 27 + radixRepresentativeBudgetPrimeEnvelopeGap 3 27 = radixRepresentativeBudgetPrimeEnvelope 3 27 ∧ radixRepresentativeBudget 3 27 ≤ radixRepresentativeBudgetPrimeEnvelope 3 27 ∧ (radixRepresentativeBudget 3 27 = radixRepresentativeBudgetPrimeEnvelope 3 27 ↔ lastRadixBlockQuotient 3 27 = 0 ∨ lastRadixBlockRemainder 3 27 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 27 ≤ 27 * 27 := by native_decide

/-- representative_p3_B35 -/
example : radixRepresentativeBudget 3 35 + radixRepresentativeBudgetPrimeEnvelopeGap 3 35 = radixRepresentativeBudgetPrimeEnvelope 3 35 ∧ radixRepresentativeBudget 3 35 ≤ radixRepresentativeBudgetPrimeEnvelope 3 35 ∧ (radixRepresentativeBudget 3 35 = radixRepresentativeBudgetPrimeEnvelope 3 35 ↔ lastRadixBlockQuotient 3 35 = 0 ∨ lastRadixBlockRemainder 3 35 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 35 ≤ 35 * 35 := by native_decide

/-- representative_p3_B43 -/
example : radixRepresentativeBudget 3 43 + radixRepresentativeBudgetPrimeEnvelopeGap 3 43 = radixRepresentativeBudgetPrimeEnvelope 3 43 ∧ radixRepresentativeBudget 3 43 ≤ radixRepresentativeBudgetPrimeEnvelope 3 43 ∧ (radixRepresentativeBudget 3 43 = radixRepresentativeBudgetPrimeEnvelope 3 43 ↔ lastRadixBlockQuotient 3 43 = 0 ∨ lastRadixBlockRemainder 3 43 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 43 ≤ 43 * 43 := by native_decide

/-- representative_p4_B1 -/
example : radixRepresentativeBudget 4 1 + radixRepresentativeBudgetPrimeEnvelopeGap 4 1 = radixRepresentativeBudgetPrimeEnvelope 4 1 ∧ radixRepresentativeBudget 4 1 ≤ radixRepresentativeBudgetPrimeEnvelope 4 1 ∧ (radixRepresentativeBudget 4 1 = radixRepresentativeBudgetPrimeEnvelope 4 1 ↔ lastRadixBlockQuotient 4 1 = 0 ∨ lastRadixBlockRemainder 4 1 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 1 ≤ 1 * 1 := by native_decide

/-- representative_p4_B9 -/
example : radixRepresentativeBudget 4 9 + radixRepresentativeBudgetPrimeEnvelopeGap 4 9 = radixRepresentativeBudgetPrimeEnvelope 4 9 ∧ radixRepresentativeBudget 4 9 ≤ radixRepresentativeBudgetPrimeEnvelope 4 9 ∧ (radixRepresentativeBudget 4 9 = radixRepresentativeBudgetPrimeEnvelope 4 9 ↔ lastRadixBlockQuotient 4 9 = 0 ∨ lastRadixBlockRemainder 4 9 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 9 ≤ 9 * 9 := by native_decide

/-- representative_p4_B17 -/
example : radixRepresentativeBudget 4 17 + radixRepresentativeBudgetPrimeEnvelopeGap 4 17 = radixRepresentativeBudgetPrimeEnvelope 4 17 ∧ radixRepresentativeBudget 4 17 ≤ radixRepresentativeBudgetPrimeEnvelope 4 17 ∧ (radixRepresentativeBudget 4 17 = radixRepresentativeBudgetPrimeEnvelope 4 17 ↔ lastRadixBlockQuotient 4 17 = 0 ∨ lastRadixBlockRemainder 4 17 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 17 ≤ 17 * 17 := by native_decide

/-- representative_p4_B25 -/
example : radixRepresentativeBudget 4 25 + radixRepresentativeBudgetPrimeEnvelopeGap 4 25 = radixRepresentativeBudgetPrimeEnvelope 4 25 ∧ radixRepresentativeBudget 4 25 ≤ radixRepresentativeBudgetPrimeEnvelope 4 25 ∧ (radixRepresentativeBudget 4 25 = radixRepresentativeBudgetPrimeEnvelope 4 25 ↔ lastRadixBlockQuotient 4 25 = 0 ∨ lastRadixBlockRemainder 4 25 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 25 ≤ 25 * 25 := by native_decide

/-- representative_p4_B33 -/
example : radixRepresentativeBudget 4 33 + radixRepresentativeBudgetPrimeEnvelopeGap 4 33 = radixRepresentativeBudgetPrimeEnvelope 4 33 ∧ radixRepresentativeBudget 4 33 ≤ radixRepresentativeBudgetPrimeEnvelope 4 33 ∧ (radixRepresentativeBudget 4 33 = radixRepresentativeBudgetPrimeEnvelope 4 33 ↔ lastRadixBlockQuotient 4 33 = 0 ∨ lastRadixBlockRemainder 4 33 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 33 ≤ 33 * 33 := by native_decide

/-- representative_p4_B41 -/
example : radixRepresentativeBudget 4 41 + radixRepresentativeBudgetPrimeEnvelopeGap 4 41 = radixRepresentativeBudgetPrimeEnvelope 4 41 ∧ radixRepresentativeBudget 4 41 ≤ radixRepresentativeBudgetPrimeEnvelope 4 41 ∧ (radixRepresentativeBudget 4 41 = radixRepresentativeBudgetPrimeEnvelope 4 41 ↔ lastRadixBlockQuotient 4 41 = 0 ∨ lastRadixBlockRemainder 4 41 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 41 ≤ 41 * 41 := by native_decide

/-- representative_p4_B49 -/
example : radixRepresentativeBudget 4 49 + radixRepresentativeBudgetPrimeEnvelopeGap 4 49 = radixRepresentativeBudgetPrimeEnvelope 4 49 ∧ radixRepresentativeBudget 4 49 ≤ radixRepresentativeBudgetPrimeEnvelope 4 49 ∧ (radixRepresentativeBudget 4 49 = radixRepresentativeBudgetPrimeEnvelope 4 49 ↔ lastRadixBlockQuotient 4 49 = 0 ∨ lastRadixBlockRemainder 4 49 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 49 ≤ 49 * 49 := by native_decide

/-- representative_p5_B7 -/
example : radixRepresentativeBudget 5 7 + radixRepresentativeBudgetPrimeEnvelopeGap 5 7 = radixRepresentativeBudgetPrimeEnvelope 5 7 ∧ radixRepresentativeBudget 5 7 ≤ radixRepresentativeBudgetPrimeEnvelope 5 7 ∧ (radixRepresentativeBudget 5 7 = radixRepresentativeBudgetPrimeEnvelope 5 7 ↔ lastRadixBlockQuotient 5 7 = 0 ∨ lastRadixBlockRemainder 5 7 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 7 ≤ 7 * 7 := by native_decide

/-- representative_p5_B15 -/
example : radixRepresentativeBudget 5 15 + radixRepresentativeBudgetPrimeEnvelopeGap 5 15 = radixRepresentativeBudgetPrimeEnvelope 5 15 ∧ radixRepresentativeBudget 5 15 ≤ radixRepresentativeBudgetPrimeEnvelope 5 15 ∧ (radixRepresentativeBudget 5 15 = radixRepresentativeBudgetPrimeEnvelope 5 15 ↔ lastRadixBlockQuotient 5 15 = 0 ∨ lastRadixBlockRemainder 5 15 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 15 ≤ 15 * 15 := by native_decide

/-- representative_p5_B23 -/
example : radixRepresentativeBudget 5 23 + radixRepresentativeBudgetPrimeEnvelopeGap 5 23 = radixRepresentativeBudgetPrimeEnvelope 5 23 ∧ radixRepresentativeBudget 5 23 ≤ radixRepresentativeBudgetPrimeEnvelope 5 23 ∧ (radixRepresentativeBudget 5 23 = radixRepresentativeBudgetPrimeEnvelope 5 23 ↔ lastRadixBlockQuotient 5 23 = 0 ∨ lastRadixBlockRemainder 5 23 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 23 ≤ 23 * 23 := by native_decide

/-- representative_p5_B31 -/
example : radixRepresentativeBudget 5 31 + radixRepresentativeBudgetPrimeEnvelopeGap 5 31 = radixRepresentativeBudgetPrimeEnvelope 5 31 ∧ radixRepresentativeBudget 5 31 ≤ radixRepresentativeBudgetPrimeEnvelope 5 31 ∧ (radixRepresentativeBudget 5 31 = radixRepresentativeBudgetPrimeEnvelope 5 31 ↔ lastRadixBlockQuotient 5 31 = 0 ∨ lastRadixBlockRemainder 5 31 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 31 ≤ 31 * 31 := by native_decide

/-- representative_p5_B39 -/
example : radixRepresentativeBudget 5 39 + radixRepresentativeBudgetPrimeEnvelopeGap 5 39 = radixRepresentativeBudgetPrimeEnvelope 5 39 ∧ radixRepresentativeBudget 5 39 ≤ radixRepresentativeBudgetPrimeEnvelope 5 39 ∧ (radixRepresentativeBudget 5 39 = radixRepresentativeBudgetPrimeEnvelope 5 39 ↔ lastRadixBlockQuotient 5 39 = 0 ∨ lastRadixBlockRemainder 5 39 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 39 ≤ 39 * 39 := by native_decide

/-- representative_p5_B47 -/
example : radixRepresentativeBudget 5 47 + radixRepresentativeBudgetPrimeEnvelopeGap 5 47 = radixRepresentativeBudgetPrimeEnvelope 5 47 ∧ radixRepresentativeBudget 5 47 ≤ radixRepresentativeBudgetPrimeEnvelope 5 47 ∧ (radixRepresentativeBudget 5 47 = radixRepresentativeBudgetPrimeEnvelope 5 47 ↔ lastRadixBlockQuotient 5 47 = 0 ∨ lastRadixBlockRemainder 5 47 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 47 ≤ 47 * 47 := by native_decide

/-- representative_p6_B5 -/
example : radixRepresentativeBudget 6 5 + radixRepresentativeBudgetPrimeEnvelopeGap 6 5 = radixRepresentativeBudgetPrimeEnvelope 6 5 ∧ radixRepresentativeBudget 6 5 ≤ radixRepresentativeBudgetPrimeEnvelope 6 5 ∧ (radixRepresentativeBudget 6 5 = radixRepresentativeBudgetPrimeEnvelope 6 5 ↔ lastRadixBlockQuotient 6 5 = 0 ∨ lastRadixBlockRemainder 6 5 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 5 ≤ 5 * 5 := by native_decide

/-- representative_p6_B13 -/
example : radixRepresentativeBudget 6 13 + radixRepresentativeBudgetPrimeEnvelopeGap 6 13 = radixRepresentativeBudgetPrimeEnvelope 6 13 ∧ radixRepresentativeBudget 6 13 ≤ radixRepresentativeBudgetPrimeEnvelope 6 13 ∧ (radixRepresentativeBudget 6 13 = radixRepresentativeBudgetPrimeEnvelope 6 13 ↔ lastRadixBlockQuotient 6 13 = 0 ∨ lastRadixBlockRemainder 6 13 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 13 ≤ 13 * 13 := by native_decide

/-- representative_p6_B21 -/
example : radixRepresentativeBudget 6 21 + radixRepresentativeBudgetPrimeEnvelopeGap 6 21 = radixRepresentativeBudgetPrimeEnvelope 6 21 ∧ radixRepresentativeBudget 6 21 ≤ radixRepresentativeBudgetPrimeEnvelope 6 21 ∧ (radixRepresentativeBudget 6 21 = radixRepresentativeBudgetPrimeEnvelope 6 21 ↔ lastRadixBlockQuotient 6 21 = 0 ∨ lastRadixBlockRemainder 6 21 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 21 ≤ 21 * 21 := by native_decide

/-- representative_p6_B29 -/
example : radixRepresentativeBudget 6 29 + radixRepresentativeBudgetPrimeEnvelopeGap 6 29 = radixRepresentativeBudgetPrimeEnvelope 6 29 ∧ radixRepresentativeBudget 6 29 ≤ radixRepresentativeBudgetPrimeEnvelope 6 29 ∧ (radixRepresentativeBudget 6 29 = radixRepresentativeBudgetPrimeEnvelope 6 29 ↔ lastRadixBlockQuotient 6 29 = 0 ∨ lastRadixBlockRemainder 6 29 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 29 ≤ 29 * 29 := by native_decide

/-- representative_p6_B37 -/
example : radixRepresentativeBudget 6 37 + radixRepresentativeBudgetPrimeEnvelopeGap 6 37 = radixRepresentativeBudgetPrimeEnvelope 6 37 ∧ radixRepresentativeBudget 6 37 ≤ radixRepresentativeBudgetPrimeEnvelope 6 37 ∧ (radixRepresentativeBudget 6 37 = radixRepresentativeBudgetPrimeEnvelope 6 37 ↔ lastRadixBlockQuotient 6 37 = 0 ∨ lastRadixBlockRemainder 6 37 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 37 ≤ 37 * 37 := by native_decide

/-- representative_p6_B45 -/
example : radixRepresentativeBudget 6 45 + radixRepresentativeBudgetPrimeEnvelopeGap 6 45 = radixRepresentativeBudgetPrimeEnvelope 6 45 ∧ radixRepresentativeBudget 6 45 ≤ radixRepresentativeBudgetPrimeEnvelope 6 45 ∧ (radixRepresentativeBudget 6 45 = radixRepresentativeBudgetPrimeEnvelope 6 45 ↔ lastRadixBlockQuotient 6 45 = 0 ∨ lastRadixBlockRemainder 6 45 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 45 ≤ 45 * 45 := by native_decide

/-- representative_p7_B3 -/
example : radixRepresentativeBudget 7 3 + radixRepresentativeBudgetPrimeEnvelopeGap 7 3 = radixRepresentativeBudgetPrimeEnvelope 7 3 ∧ radixRepresentativeBudget 7 3 ≤ radixRepresentativeBudgetPrimeEnvelope 7 3 ∧ (radixRepresentativeBudget 7 3 = radixRepresentativeBudgetPrimeEnvelope 7 3 ↔ lastRadixBlockQuotient 7 3 = 0 ∨ lastRadixBlockRemainder 7 3 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 3 ≤ 3 * 3 := by native_decide

/-- representative_p7_B11 -/
example : radixRepresentativeBudget 7 11 + radixRepresentativeBudgetPrimeEnvelopeGap 7 11 = radixRepresentativeBudgetPrimeEnvelope 7 11 ∧ radixRepresentativeBudget 7 11 ≤ radixRepresentativeBudgetPrimeEnvelope 7 11 ∧ (radixRepresentativeBudget 7 11 = radixRepresentativeBudgetPrimeEnvelope 7 11 ↔ lastRadixBlockQuotient 7 11 = 0 ∨ lastRadixBlockRemainder 7 11 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 11 ≤ 11 * 11 := by native_decide

/-- representative_p7_B19 -/
example : radixRepresentativeBudget 7 19 + radixRepresentativeBudgetPrimeEnvelopeGap 7 19 = radixRepresentativeBudgetPrimeEnvelope 7 19 ∧ radixRepresentativeBudget 7 19 ≤ radixRepresentativeBudgetPrimeEnvelope 7 19 ∧ (radixRepresentativeBudget 7 19 = radixRepresentativeBudgetPrimeEnvelope 7 19 ↔ lastRadixBlockQuotient 7 19 = 0 ∨ lastRadixBlockRemainder 7 19 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 19 ≤ 19 * 19 := by native_decide

/-- representative_p7_B27 -/
example : radixRepresentativeBudget 7 27 + radixRepresentativeBudgetPrimeEnvelopeGap 7 27 = radixRepresentativeBudgetPrimeEnvelope 7 27 ∧ radixRepresentativeBudget 7 27 ≤ radixRepresentativeBudgetPrimeEnvelope 7 27 ∧ (radixRepresentativeBudget 7 27 = radixRepresentativeBudgetPrimeEnvelope 7 27 ↔ lastRadixBlockQuotient 7 27 = 0 ∨ lastRadixBlockRemainder 7 27 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 27 ≤ 27 * 27 := by native_decide

/-- representative_p7_B35 -/
example : radixRepresentativeBudget 7 35 + radixRepresentativeBudgetPrimeEnvelopeGap 7 35 = radixRepresentativeBudgetPrimeEnvelope 7 35 ∧ radixRepresentativeBudget 7 35 ≤ radixRepresentativeBudgetPrimeEnvelope 7 35 ∧ (radixRepresentativeBudget 7 35 = radixRepresentativeBudgetPrimeEnvelope 7 35 ↔ lastRadixBlockQuotient 7 35 = 0 ∨ lastRadixBlockRemainder 7 35 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 35 ≤ 35 * 35 := by native_decide

/-- representative_p7_B43 -/
example : radixRepresentativeBudget 7 43 + radixRepresentativeBudgetPrimeEnvelopeGap 7 43 = radixRepresentativeBudgetPrimeEnvelope 7 43 ∧ radixRepresentativeBudget 7 43 ≤ radixRepresentativeBudgetPrimeEnvelope 7 43 ∧ (radixRepresentativeBudget 7 43 = radixRepresentativeBudgetPrimeEnvelope 7 43 ↔ lastRadixBlockQuotient 7 43 = 0 ∨ lastRadixBlockRemainder 7 43 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 43 ≤ 43 * 43 := by native_decide

/-- representative_p8_B1 -/
example : radixRepresentativeBudget 8 1 + radixRepresentativeBudgetPrimeEnvelopeGap 8 1 = radixRepresentativeBudgetPrimeEnvelope 8 1 ∧ radixRepresentativeBudget 8 1 ≤ radixRepresentativeBudgetPrimeEnvelope 8 1 ∧ (radixRepresentativeBudget 8 1 = radixRepresentativeBudgetPrimeEnvelope 8 1 ↔ lastRadixBlockQuotient 8 1 = 0 ∨ lastRadixBlockRemainder 8 1 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 1 ≤ 1 * 1 := by native_decide

/-- representative_p8_B9 -/
example : radixRepresentativeBudget 8 9 + radixRepresentativeBudgetPrimeEnvelopeGap 8 9 = radixRepresentativeBudgetPrimeEnvelope 8 9 ∧ radixRepresentativeBudget 8 9 ≤ radixRepresentativeBudgetPrimeEnvelope 8 9 ∧ (radixRepresentativeBudget 8 9 = radixRepresentativeBudgetPrimeEnvelope 8 9 ↔ lastRadixBlockQuotient 8 9 = 0 ∨ lastRadixBlockRemainder 8 9 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 9 ≤ 9 * 9 := by native_decide

/-- representative_p8_B17 -/
example : radixRepresentativeBudget 8 17 + radixRepresentativeBudgetPrimeEnvelopeGap 8 17 = radixRepresentativeBudgetPrimeEnvelope 8 17 ∧ radixRepresentativeBudget 8 17 ≤ radixRepresentativeBudgetPrimeEnvelope 8 17 ∧ (radixRepresentativeBudget 8 17 = radixRepresentativeBudgetPrimeEnvelope 8 17 ↔ lastRadixBlockQuotient 8 17 = 0 ∨ lastRadixBlockRemainder 8 17 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 17 ≤ 17 * 17 := by native_decide

/-- representative_p8_B25 -/
example : radixRepresentativeBudget 8 25 + radixRepresentativeBudgetPrimeEnvelopeGap 8 25 = radixRepresentativeBudgetPrimeEnvelope 8 25 ∧ radixRepresentativeBudget 8 25 ≤ radixRepresentativeBudgetPrimeEnvelope 8 25 ∧ (radixRepresentativeBudget 8 25 = radixRepresentativeBudgetPrimeEnvelope 8 25 ↔ lastRadixBlockQuotient 8 25 = 0 ∨ lastRadixBlockRemainder 8 25 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 25 ≤ 25 * 25 := by native_decide

/-- representative_p8_B33 -/
example : radixRepresentativeBudget 8 33 + radixRepresentativeBudgetPrimeEnvelopeGap 8 33 = radixRepresentativeBudgetPrimeEnvelope 8 33 ∧ radixRepresentativeBudget 8 33 ≤ radixRepresentativeBudgetPrimeEnvelope 8 33 ∧ (radixRepresentativeBudget 8 33 = radixRepresentativeBudgetPrimeEnvelope 8 33 ↔ lastRadixBlockQuotient 8 33 = 0 ∨ lastRadixBlockRemainder 8 33 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 33 ≤ 33 * 33 := by native_decide

/-- representative_p8_B41 -/
example : radixRepresentativeBudget 8 41 + radixRepresentativeBudgetPrimeEnvelopeGap 8 41 = radixRepresentativeBudgetPrimeEnvelope 8 41 ∧ radixRepresentativeBudget 8 41 ≤ radixRepresentativeBudgetPrimeEnvelope 8 41 ∧ (radixRepresentativeBudget 8 41 = radixRepresentativeBudgetPrimeEnvelope 8 41 ↔ lastRadixBlockQuotient 8 41 = 0 ∨ lastRadixBlockRemainder 8 41 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 41 ≤ 41 * 41 := by native_decide

/-- representative_p8_B49 -/
example : radixRepresentativeBudget 8 49 + radixRepresentativeBudgetPrimeEnvelopeGap 8 49 = radixRepresentativeBudgetPrimeEnvelope 8 49 ∧ radixRepresentativeBudget 8 49 ≤ radixRepresentativeBudgetPrimeEnvelope 8 49 ∧ (radixRepresentativeBudget 8 49 = radixRepresentativeBudgetPrimeEnvelope 8 49 ↔ lastRadixBlockQuotient 8 49 = 0 ∨ lastRadixBlockRemainder 8 49 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 49 ≤ 49 * 49 := by native_decide

/-- representative_p9_B7 -/
example : radixRepresentativeBudget 9 7 + radixRepresentativeBudgetPrimeEnvelopeGap 9 7 = radixRepresentativeBudgetPrimeEnvelope 9 7 ∧ radixRepresentativeBudget 9 7 ≤ radixRepresentativeBudgetPrimeEnvelope 9 7 ∧ (radixRepresentativeBudget 9 7 = radixRepresentativeBudgetPrimeEnvelope 9 7 ↔ lastRadixBlockQuotient 9 7 = 0 ∨ lastRadixBlockRemainder 9 7 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 7 ≤ 7 * 7 := by native_decide

/-- representative_p9_B15 -/
example : radixRepresentativeBudget 9 15 + radixRepresentativeBudgetPrimeEnvelopeGap 9 15 = radixRepresentativeBudgetPrimeEnvelope 9 15 ∧ radixRepresentativeBudget 9 15 ≤ radixRepresentativeBudgetPrimeEnvelope 9 15 ∧ (radixRepresentativeBudget 9 15 = radixRepresentativeBudgetPrimeEnvelope 9 15 ↔ lastRadixBlockQuotient 9 15 = 0 ∨ lastRadixBlockRemainder 9 15 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 15 ≤ 15 * 15 := by native_decide

/-- representative_p9_B23 -/
example : radixRepresentativeBudget 9 23 + radixRepresentativeBudgetPrimeEnvelopeGap 9 23 = radixRepresentativeBudgetPrimeEnvelope 9 23 ∧ radixRepresentativeBudget 9 23 ≤ radixRepresentativeBudgetPrimeEnvelope 9 23 ∧ (radixRepresentativeBudget 9 23 = radixRepresentativeBudgetPrimeEnvelope 9 23 ↔ lastRadixBlockQuotient 9 23 = 0 ∨ lastRadixBlockRemainder 9 23 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 23 ≤ 23 * 23 := by native_decide

/-- representative_p9_B31 -/
example : radixRepresentativeBudget 9 31 + radixRepresentativeBudgetPrimeEnvelopeGap 9 31 = radixRepresentativeBudgetPrimeEnvelope 9 31 ∧ radixRepresentativeBudget 9 31 ≤ radixRepresentativeBudgetPrimeEnvelope 9 31 ∧ (radixRepresentativeBudget 9 31 = radixRepresentativeBudgetPrimeEnvelope 9 31 ↔ lastRadixBlockQuotient 9 31 = 0 ∨ lastRadixBlockRemainder 9 31 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 31 ≤ 31 * 31 := by native_decide

/-- representative_p9_B39 -/
example : radixRepresentativeBudget 9 39 + radixRepresentativeBudgetPrimeEnvelopeGap 9 39 = radixRepresentativeBudgetPrimeEnvelope 9 39 ∧ radixRepresentativeBudget 9 39 ≤ radixRepresentativeBudgetPrimeEnvelope 9 39 ∧ (radixRepresentativeBudget 9 39 = radixRepresentativeBudgetPrimeEnvelope 9 39 ↔ lastRadixBlockQuotient 9 39 = 0 ∨ lastRadixBlockRemainder 9 39 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 39 ≤ 39 * 39 := by native_decide

/-- representative_p9_B47 -/
example : radixRepresentativeBudget 9 47 + radixRepresentativeBudgetPrimeEnvelopeGap 9 47 = radixRepresentativeBudgetPrimeEnvelope 9 47 ∧ radixRepresentativeBudget 9 47 ≤ radixRepresentativeBudgetPrimeEnvelope 9 47 ∧ (radixRepresentativeBudget 9 47 = radixRepresentativeBudgetPrimeEnvelope 9 47 ↔ lastRadixBlockQuotient 9 47 = 0 ∨ lastRadixBlockRemainder 9 47 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 47 ≤ 47 * 47 := by native_decide

/-- representative_p10_B5 -/
example : radixRepresentativeBudget 10 5 + radixRepresentativeBudgetPrimeEnvelopeGap 10 5 = radixRepresentativeBudgetPrimeEnvelope 10 5 ∧ radixRepresentativeBudget 10 5 ≤ radixRepresentativeBudgetPrimeEnvelope 10 5 ∧ (radixRepresentativeBudget 10 5 = radixRepresentativeBudgetPrimeEnvelope 10 5 ↔ lastRadixBlockQuotient 10 5 = 0 ∨ lastRadixBlockRemainder 10 5 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 5 ≤ 5 * 5 := by native_decide

/-- representative_p10_B13 -/
example : radixRepresentativeBudget 10 13 + radixRepresentativeBudgetPrimeEnvelopeGap 10 13 = radixRepresentativeBudgetPrimeEnvelope 10 13 ∧ radixRepresentativeBudget 10 13 ≤ radixRepresentativeBudgetPrimeEnvelope 10 13 ∧ (radixRepresentativeBudget 10 13 = radixRepresentativeBudgetPrimeEnvelope 10 13 ↔ lastRadixBlockQuotient 10 13 = 0 ∨ lastRadixBlockRemainder 10 13 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 13 ≤ 13 * 13 := by native_decide

/-- representative_p10_B21 -/
example : radixRepresentativeBudget 10 21 + radixRepresentativeBudgetPrimeEnvelopeGap 10 21 = radixRepresentativeBudgetPrimeEnvelope 10 21 ∧ radixRepresentativeBudget 10 21 ≤ radixRepresentativeBudgetPrimeEnvelope 10 21 ∧ (radixRepresentativeBudget 10 21 = radixRepresentativeBudgetPrimeEnvelope 10 21 ↔ lastRadixBlockQuotient 10 21 = 0 ∨ lastRadixBlockRemainder 10 21 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 21 ≤ 21 * 21 := by native_decide

/-- representative_p10_B29 -/
example : radixRepresentativeBudget 10 29 + radixRepresentativeBudgetPrimeEnvelopeGap 10 29 = radixRepresentativeBudgetPrimeEnvelope 10 29 ∧ radixRepresentativeBudget 10 29 ≤ radixRepresentativeBudgetPrimeEnvelope 10 29 ∧ (radixRepresentativeBudget 10 29 = radixRepresentativeBudgetPrimeEnvelope 10 29 ↔ lastRadixBlockQuotient 10 29 = 0 ∨ lastRadixBlockRemainder 10 29 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 29 ≤ 29 * 29 := by native_decide

/-- representative_p10_B37 -/
example : radixRepresentativeBudget 10 37 + radixRepresentativeBudgetPrimeEnvelopeGap 10 37 = radixRepresentativeBudgetPrimeEnvelope 10 37 ∧ radixRepresentativeBudget 10 37 ≤ radixRepresentativeBudgetPrimeEnvelope 10 37 ∧ (radixRepresentativeBudget 10 37 = radixRepresentativeBudgetPrimeEnvelope 10 37 ↔ lastRadixBlockQuotient 10 37 = 0 ∨ lastRadixBlockRemainder 10 37 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 37 ≤ 37 * 37 := by native_decide

/-- representative_p10_B45 -/
example : radixRepresentativeBudget 10 45 + radixRepresentativeBudgetPrimeEnvelopeGap 10 45 = radixRepresentativeBudgetPrimeEnvelope 10 45 ∧ radixRepresentativeBudget 10 45 ≤ radixRepresentativeBudgetPrimeEnvelope 10 45 ∧ (radixRepresentativeBudget 10 45 = radixRepresentativeBudgetPrimeEnvelope 10 45 ↔ lastRadixBlockQuotient 10 45 = 0 ∨ lastRadixBlockRemainder 10 45 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 45 ≤ 45 * 45 := by native_decide

/-- representative_p11_B3 -/
example : radixRepresentativeBudget 11 3 + radixRepresentativeBudgetPrimeEnvelopeGap 11 3 = radixRepresentativeBudgetPrimeEnvelope 11 3 ∧ radixRepresentativeBudget 11 3 ≤ radixRepresentativeBudgetPrimeEnvelope 11 3 ∧ (radixRepresentativeBudget 11 3 = radixRepresentativeBudgetPrimeEnvelope 11 3 ↔ lastRadixBlockQuotient 11 3 = 0 ∨ lastRadixBlockRemainder 11 3 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 3 ≤ 3 * 3 := by native_decide

/-- representative_p11_B11 -/
example : radixRepresentativeBudget 11 11 + radixRepresentativeBudgetPrimeEnvelopeGap 11 11 = radixRepresentativeBudgetPrimeEnvelope 11 11 ∧ radixRepresentativeBudget 11 11 ≤ radixRepresentativeBudgetPrimeEnvelope 11 11 ∧ (radixRepresentativeBudget 11 11 = radixRepresentativeBudgetPrimeEnvelope 11 11 ↔ lastRadixBlockQuotient 11 11 = 0 ∨ lastRadixBlockRemainder 11 11 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 11 ≤ 11 * 11 := by native_decide

/-- representative_p11_B19 -/
example : radixRepresentativeBudget 11 19 + radixRepresentativeBudgetPrimeEnvelopeGap 11 19 = radixRepresentativeBudgetPrimeEnvelope 11 19 ∧ radixRepresentativeBudget 11 19 ≤ radixRepresentativeBudgetPrimeEnvelope 11 19 ∧ (radixRepresentativeBudget 11 19 = radixRepresentativeBudgetPrimeEnvelope 11 19 ↔ lastRadixBlockQuotient 11 19 = 0 ∨ lastRadixBlockRemainder 11 19 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 19 ≤ 19 * 19 := by native_decide

/-- representative_p11_B27 -/
example : radixRepresentativeBudget 11 27 + radixRepresentativeBudgetPrimeEnvelopeGap 11 27 = radixRepresentativeBudgetPrimeEnvelope 11 27 ∧ radixRepresentativeBudget 11 27 ≤ radixRepresentativeBudgetPrimeEnvelope 11 27 ∧ (radixRepresentativeBudget 11 27 = radixRepresentativeBudgetPrimeEnvelope 11 27 ↔ lastRadixBlockQuotient 11 27 = 0 ∨ lastRadixBlockRemainder 11 27 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 27 ≤ 27 * 27 := by native_decide

/-- representative_p11_B35 -/
example : radixRepresentativeBudget 11 35 + radixRepresentativeBudgetPrimeEnvelopeGap 11 35 = radixRepresentativeBudgetPrimeEnvelope 11 35 ∧ radixRepresentativeBudget 11 35 ≤ radixRepresentativeBudgetPrimeEnvelope 11 35 ∧ (radixRepresentativeBudget 11 35 = radixRepresentativeBudgetPrimeEnvelope 11 35 ↔ lastRadixBlockQuotient 11 35 = 0 ∨ lastRadixBlockRemainder 11 35 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 35 ≤ 35 * 35 := by native_decide

/-- representative_p11_B43 -/
example : radixRepresentativeBudget 11 43 + radixRepresentativeBudgetPrimeEnvelopeGap 11 43 = radixRepresentativeBudgetPrimeEnvelope 11 43 ∧ radixRepresentativeBudget 11 43 ≤ radixRepresentativeBudgetPrimeEnvelope 11 43 ∧ (radixRepresentativeBudget 11 43 = radixRepresentativeBudgetPrimeEnvelope 11 43 ↔ lastRadixBlockQuotient 11 43 = 0 ∨ lastRadixBlockRemainder 11 43 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 43 ≤ 43 * 43 := by native_decide

/-- representative_p12_B1 -/
example : radixRepresentativeBudget 12 1 + radixRepresentativeBudgetPrimeEnvelopeGap 12 1 = radixRepresentativeBudgetPrimeEnvelope 12 1 ∧ radixRepresentativeBudget 12 1 ≤ radixRepresentativeBudgetPrimeEnvelope 12 1 ∧ (radixRepresentativeBudget 12 1 = radixRepresentativeBudgetPrimeEnvelope 12 1 ↔ lastRadixBlockQuotient 12 1 = 0 ∨ lastRadixBlockRemainder 12 1 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 1 ≤ 1 * 1 := by native_decide

/-- representative_p12_B9 -/
example : radixRepresentativeBudget 12 9 + radixRepresentativeBudgetPrimeEnvelopeGap 12 9 = radixRepresentativeBudgetPrimeEnvelope 12 9 ∧ radixRepresentativeBudget 12 9 ≤ radixRepresentativeBudgetPrimeEnvelope 12 9 ∧ (radixRepresentativeBudget 12 9 = radixRepresentativeBudgetPrimeEnvelope 12 9 ↔ lastRadixBlockQuotient 12 9 = 0 ∨ lastRadixBlockRemainder 12 9 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 9 ≤ 9 * 9 := by native_decide

/-- representative_p12_B17 -/
example : radixRepresentativeBudget 12 17 + radixRepresentativeBudgetPrimeEnvelopeGap 12 17 = radixRepresentativeBudgetPrimeEnvelope 12 17 ∧ radixRepresentativeBudget 12 17 ≤ radixRepresentativeBudgetPrimeEnvelope 12 17 ∧ (radixRepresentativeBudget 12 17 = radixRepresentativeBudgetPrimeEnvelope 12 17 ↔ lastRadixBlockQuotient 12 17 = 0 ∨ lastRadixBlockRemainder 12 17 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 17 ≤ 17 * 17 := by native_decide

/-- representative_p12_B25 -/
example : radixRepresentativeBudget 12 25 + radixRepresentativeBudgetPrimeEnvelopeGap 12 25 = radixRepresentativeBudgetPrimeEnvelope 12 25 ∧ radixRepresentativeBudget 12 25 ≤ radixRepresentativeBudgetPrimeEnvelope 12 25 ∧ (radixRepresentativeBudget 12 25 = radixRepresentativeBudgetPrimeEnvelope 12 25 ↔ lastRadixBlockQuotient 12 25 = 0 ∨ lastRadixBlockRemainder 12 25 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 25 ≤ 25 * 25 := by native_decide

/-- representative_p12_B33 -/
example : radixRepresentativeBudget 12 33 + radixRepresentativeBudgetPrimeEnvelopeGap 12 33 = radixRepresentativeBudgetPrimeEnvelope 12 33 ∧ radixRepresentativeBudget 12 33 ≤ radixRepresentativeBudgetPrimeEnvelope 12 33 ∧ (radixRepresentativeBudget 12 33 = radixRepresentativeBudgetPrimeEnvelope 12 33 ↔ lastRadixBlockQuotient 12 33 = 0 ∨ lastRadixBlockRemainder 12 33 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 33 ≤ 33 * 33 := by native_decide

/-- representative_p12_B41 -/
example : radixRepresentativeBudget 12 41 + radixRepresentativeBudgetPrimeEnvelopeGap 12 41 = radixRepresentativeBudgetPrimeEnvelope 12 41 ∧ radixRepresentativeBudget 12 41 ≤ radixRepresentativeBudgetPrimeEnvelope 12 41 ∧ (radixRepresentativeBudget 12 41 = radixRepresentativeBudgetPrimeEnvelope 12 41 ↔ lastRadixBlockQuotient 12 41 = 0 ∨ lastRadixBlockRemainder 12 41 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 41 ≤ 41 * 41 := by native_decide

/-- representative_p12_B49 -/
example : radixRepresentativeBudget 12 49 + radixRepresentativeBudgetPrimeEnvelopeGap 12 49 = radixRepresentativeBudgetPrimeEnvelope 12 49 ∧ radixRepresentativeBudget 12 49 ≤ radixRepresentativeBudgetPrimeEnvelope 12 49 ∧ (radixRepresentativeBudget 12 49 = radixRepresentativeBudgetPrimeEnvelope 12 49 ↔ lastRadixBlockQuotient 12 49 = 0 ∨ lastRadixBlockRemainder 12 49 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 49 ≤ 49 * 49 := by native_decide

/-- zero_base_B7 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 7 ≤ 7 * 7 := by native_decide

/-- zero_base_B15 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 15 ≤ 15 * 15 := by native_decide

/-- zero_base_B23 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 23 ≤ 23 * 23 := by native_decide

/-- zero_base_B31 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 31 ≤ 31 * 31 := by native_decide

/-- zero_base_B39 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 39 ≤ 39 * 39 := by native_decide

/-- zero_base_B47 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 47 ≤ 47 * 47 := by native_decide

/-- zero_base_B55 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 55 ≤ 55 * 55 := by native_decide

/-- zero_base_B63 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 63 ≤ 63 * 63 := by native_decide

/-- zero_base_B71 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 71 ≤ 71 * 71 := by native_decide

/-- zero_base_B79 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 79 ≤ 79 * 79 := by native_decide

/-- zero_base_B87 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 87 ≤ 87 * 87 := by native_decide

/-- zero_base_B95 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 95 ≤ 95 * 95 := by native_decide

/-- zero_base_B103 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 103 ≤ 103 * 103 := by native_decide

/-- zero_base_B111 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 111 ≤ 111 * 111 := by native_decide

/-- zero_base_B119 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 119 ≤ 119 * 119 := by native_decide

/-- zero_base_B127 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 127 ≤ 127 * 127 := by native_decide

/-- zero_base_B135 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 135 ≤ 135 * 135 := by native_decide

/-- zero_base_B143 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 143 ≤ 143 * 143 := by native_decide

/-- zero_base_B151 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 151 ≤ 151 * 151 := by native_decide

/-- zero_base_B159 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 159 ≤ 159 * 159 := by native_decide

/-- zero_base_B167 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 167 ≤ 167 * 167 := by native_decide

/-- zero_base_B175 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 175 ≤ 175 * 175 := by native_decide

/-- zero_base_B183 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 183 ≤ 183 * 183 := by native_decide

/-- zero_base_B191 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 191 ≤ 191 * 191 := by native_decide

/-- zero_base_B199 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 199 ≤ 199 * 199 := by native_decide

/-- compiler_p2_r3_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 3 1 + maximumLayerCompilerPrimeEnvelopeGap 2 3 1 = maximumLayerCompilerPrimeEnvelopeBound 2 3 1 ∧ maximumLayerCompilerTotalTests 2 3 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 3 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 3 1 ≤ maximumLayerCompilerTestBound 2 3 1 := by native_decide

/-- compiler_p2_r6_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 6 0 + maximumLayerCompilerPrimeEnvelopeGap 2 6 0 = maximumLayerCompilerPrimeEnvelopeBound 2 6 0 ∧ maximumLayerCompilerTotalTests 2 6 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 6 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 6 0 ≤ maximumLayerCompilerTestBound 2 6 0 := by native_decide

/-- compiler_p2_r8_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 8 2 + maximumLayerCompilerPrimeEnvelopeGap 2 8 2 = maximumLayerCompilerPrimeEnvelopeBound 2 8 2 ∧ maximumLayerCompilerTotalTests 2 8 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 8 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 8 2 ≤ maximumLayerCompilerTestBound 2 8 2 := by native_decide

/-- compiler_p2_r11_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 11 1 + maximumLayerCompilerPrimeEnvelopeGap 2 11 1 = maximumLayerCompilerPrimeEnvelopeBound 2 11 1 ∧ maximumLayerCompilerTotalTests 2 11 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 11 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 11 1 ≤ maximumLayerCompilerTestBound 2 11 1 := by native_decide

/-- compiler_p2_r14_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 14 0 + maximumLayerCompilerPrimeEnvelopeGap 2 14 0 = maximumLayerCompilerPrimeEnvelopeBound 2 14 0 ∧ maximumLayerCompilerTotalTests 2 14 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 14 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 14 0 ≤ maximumLayerCompilerTestBound 2 14 0 := by native_decide

/-- compiler_p2_r16_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 16 2 + maximumLayerCompilerPrimeEnvelopeGap 2 16 2 = maximumLayerCompilerPrimeEnvelopeBound 2 16 2 ∧ maximumLayerCompilerTotalTests 2 16 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 16 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 16 2 ≤ maximumLayerCompilerTestBound 2 16 2 := by native_decide

/-- compiler_p2_r19_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 19 1 + maximumLayerCompilerPrimeEnvelopeGap 2 19 1 = maximumLayerCompilerPrimeEnvelopeBound 2 19 1 ∧ maximumLayerCompilerTotalTests 2 19 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 19 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 19 1 ≤ maximumLayerCompilerTestBound 2 19 1 := by native_decide

/-- compiler_p3_r2_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 2 0 + maximumLayerCompilerPrimeEnvelopeGap 3 2 0 = maximumLayerCompilerPrimeEnvelopeBound 3 2 0 ∧ maximumLayerCompilerTotalTests 3 2 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 2 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 2 0 ≤ maximumLayerCompilerTestBound 3 2 0 := by native_decide

/-- compiler_p3_r4_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 4 2 + maximumLayerCompilerPrimeEnvelopeGap 3 4 2 = maximumLayerCompilerPrimeEnvelopeBound 3 4 2 ∧ maximumLayerCompilerTotalTests 3 4 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 4 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 4 2 ≤ maximumLayerCompilerTestBound 3 4 2 := by native_decide

/-- compiler_p3_r7_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 7 1 + maximumLayerCompilerPrimeEnvelopeGap 3 7 1 = maximumLayerCompilerPrimeEnvelopeBound 3 7 1 ∧ maximumLayerCompilerTotalTests 3 7 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 7 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 7 1 ≤ maximumLayerCompilerTestBound 3 7 1 := by native_decide

/-- compiler_p3_r10_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 10 0 + maximumLayerCompilerPrimeEnvelopeGap 3 10 0 = maximumLayerCompilerPrimeEnvelopeBound 3 10 0 ∧ maximumLayerCompilerTotalTests 3 10 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 10 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 10 0 ≤ maximumLayerCompilerTestBound 3 10 0 := by native_decide

/-- compiler_p3_r12_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 12 2 + maximumLayerCompilerPrimeEnvelopeGap 3 12 2 = maximumLayerCompilerPrimeEnvelopeBound 3 12 2 ∧ maximumLayerCompilerTotalTests 3 12 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 12 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 12 2 ≤ maximumLayerCompilerTestBound 3 12 2 := by native_decide

/-- compiler_p3_r15_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 15 1 + maximumLayerCompilerPrimeEnvelopeGap 3 15 1 = maximumLayerCompilerPrimeEnvelopeBound 3 15 1 ∧ maximumLayerCompilerTotalTests 3 15 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 15 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 15 1 ≤ maximumLayerCompilerTestBound 3 15 1 := by native_decide

/-- compiler_p3_r18_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 18 0 + maximumLayerCompilerPrimeEnvelopeGap 3 18 0 = maximumLayerCompilerPrimeEnvelopeBound 3 18 0 ∧ maximumLayerCompilerTotalTests 3 18 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 18 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 18 0 ≤ maximumLayerCompilerTestBound 3 18 0 := by native_decide

/-- compiler_p3_r20_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 20 2 + maximumLayerCompilerPrimeEnvelopeGap 3 20 2 = maximumLayerCompilerPrimeEnvelopeBound 3 20 2 ∧ maximumLayerCompilerTotalTests 3 20 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 20 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 20 2 ≤ maximumLayerCompilerTestBound 3 20 2 := by native_decide

/-- compiler_p5_r3_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 3 1 + maximumLayerCompilerPrimeEnvelopeGap 5 3 1 = maximumLayerCompilerPrimeEnvelopeBound 5 3 1 ∧ maximumLayerCompilerTotalTests 5 3 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 3 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 3 1 ≤ maximumLayerCompilerTestBound 5 3 1 := by native_decide

/-- compiler_p5_r6_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 6 0 + maximumLayerCompilerPrimeEnvelopeGap 5 6 0 = maximumLayerCompilerPrimeEnvelopeBound 5 6 0 ∧ maximumLayerCompilerTotalTests 5 6 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 6 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 6 0 ≤ maximumLayerCompilerTestBound 5 6 0 := by native_decide

/-- compiler_p5_r8_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 8 2 + maximumLayerCompilerPrimeEnvelopeGap 5 8 2 = maximumLayerCompilerPrimeEnvelopeBound 5 8 2 ∧ maximumLayerCompilerTotalTests 5 8 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 8 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 8 2 ≤ maximumLayerCompilerTestBound 5 8 2 := by native_decide

/-- compiler_p5_r11_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 11 1 + maximumLayerCompilerPrimeEnvelopeGap 5 11 1 = maximumLayerCompilerPrimeEnvelopeBound 5 11 1 ∧ maximumLayerCompilerTotalTests 5 11 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 11 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 11 1 ≤ maximumLayerCompilerTestBound 5 11 1 := by native_decide

/-- compiler_p5_r14_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 14 0 + maximumLayerCompilerPrimeEnvelopeGap 5 14 0 = maximumLayerCompilerPrimeEnvelopeBound 5 14 0 ∧ maximumLayerCompilerTotalTests 5 14 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 14 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 14 0 ≤ maximumLayerCompilerTestBound 5 14 0 := by native_decide

/-- compiler_p5_r16_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 16 2 + maximumLayerCompilerPrimeEnvelopeGap 5 16 2 = maximumLayerCompilerPrimeEnvelopeBound 5 16 2 ∧ maximumLayerCompilerTotalTests 5 16 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 16 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 16 2 ≤ maximumLayerCompilerTestBound 5 16 2 := by native_decide

/-- compiler_p5_r19_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 19 1 + maximumLayerCompilerPrimeEnvelopeGap 5 19 1 = maximumLayerCompilerPrimeEnvelopeBound 5 19 1 ∧ maximumLayerCompilerTotalTests 5 19 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 19 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 19 1 ≤ maximumLayerCompilerTestBound 5 19 1 := by native_decide

/-- compiler_p7_r2_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 2 0 + maximumLayerCompilerPrimeEnvelopeGap 7 2 0 = maximumLayerCompilerPrimeEnvelopeBound 7 2 0 ∧ maximumLayerCompilerTotalTests 7 2 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 2 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 2 0 ≤ maximumLayerCompilerTestBound 7 2 0 := by native_decide

/-- compiler_p7_r4_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 4 2 + maximumLayerCompilerPrimeEnvelopeGap 7 4 2 = maximumLayerCompilerPrimeEnvelopeBound 7 4 2 ∧ maximumLayerCompilerTotalTests 7 4 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 4 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 4 2 ≤ maximumLayerCompilerTestBound 7 4 2 := by native_decide

/-- compiler_p7_r7_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 7 1 + maximumLayerCompilerPrimeEnvelopeGap 7 7 1 = maximumLayerCompilerPrimeEnvelopeBound 7 7 1 ∧ maximumLayerCompilerTotalTests 7 7 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 7 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 7 1 ≤ maximumLayerCompilerTestBound 7 7 1 := by native_decide

/-- compiler_p7_r10_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 10 0 + maximumLayerCompilerPrimeEnvelopeGap 7 10 0 = maximumLayerCompilerPrimeEnvelopeBound 7 10 0 ∧ maximumLayerCompilerTotalTests 7 10 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 10 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 10 0 ≤ maximumLayerCompilerTestBound 7 10 0 := by native_decide

/-- compiler_p7_r12_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 12 2 + maximumLayerCompilerPrimeEnvelopeGap 7 12 2 = maximumLayerCompilerPrimeEnvelopeBound 7 12 2 ∧ maximumLayerCompilerTotalTests 7 12 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 12 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 12 2 ≤ maximumLayerCompilerTestBound 7 12 2 := by native_decide

/-- compiler_p7_r15_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 15 1 + maximumLayerCompilerPrimeEnvelopeGap 7 15 1 = maximumLayerCompilerPrimeEnvelopeBound 7 15 1 ∧ maximumLayerCompilerTotalTests 7 15 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 15 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 15 1 ≤ maximumLayerCompilerTestBound 7 15 1 := by native_decide

/-- compiler_p7_r18_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 18 0 + maximumLayerCompilerPrimeEnvelopeGap 7 18 0 = maximumLayerCompilerPrimeEnvelopeBound 7 18 0 ∧ maximumLayerCompilerTotalTests 7 18 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 18 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 18 0 ≤ maximumLayerCompilerTestBound 7 18 0 := by native_decide

/-- compiler_p7_r20_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 20 2 + maximumLayerCompilerPrimeEnvelopeGap 7 20 2 = maximumLayerCompilerPrimeEnvelopeBound 7 20 2 ∧ maximumLayerCompilerTotalTests 7 20 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 20 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 20 2 ≤ maximumLayerCompilerTestBound 7 20 2 := by native_decide

/-- compiler_p11_r3_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 3 1 + maximumLayerCompilerPrimeEnvelopeGap 11 3 1 = maximumLayerCompilerPrimeEnvelopeBound 11 3 1 ∧ maximumLayerCompilerTotalTests 11 3 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 3 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 3 1 ≤ maximumLayerCompilerTestBound 11 3 1 := by native_decide

/-- compiler_p11_r6_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 6 0 + maximumLayerCompilerPrimeEnvelopeGap 11 6 0 = maximumLayerCompilerPrimeEnvelopeBound 11 6 0 ∧ maximumLayerCompilerTotalTests 11 6 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 6 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 6 0 ≤ maximumLayerCompilerTestBound 11 6 0 := by native_decide

/-- compiler_p11_r8_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 8 2 + maximumLayerCompilerPrimeEnvelopeGap 11 8 2 = maximumLayerCompilerPrimeEnvelopeBound 11 8 2 ∧ maximumLayerCompilerTotalTests 11 8 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 8 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 8 2 ≤ maximumLayerCompilerTestBound 11 8 2 := by native_decide

/-- compiler_p11_r11_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 11 1 + maximumLayerCompilerPrimeEnvelopeGap 11 11 1 = maximumLayerCompilerPrimeEnvelopeBound 11 11 1 ∧ maximumLayerCompilerTotalTests 11 11 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 11 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 11 1 ≤ maximumLayerCompilerTestBound 11 11 1 := by native_decide

/-- compiler_p11_r14_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 14 0 + maximumLayerCompilerPrimeEnvelopeGap 11 14 0 = maximumLayerCompilerPrimeEnvelopeBound 11 14 0 ∧ maximumLayerCompilerTotalTests 11 14 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 14 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 14 0 ≤ maximumLayerCompilerTestBound 11 14 0 := by native_decide

/-- compiler_p11_r16_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 16 2 + maximumLayerCompilerPrimeEnvelopeGap 11 16 2 = maximumLayerCompilerPrimeEnvelopeBound 11 16 2 ∧ maximumLayerCompilerTotalTests 11 16 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 16 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 16 2 ≤ maximumLayerCompilerTestBound 11 16 2 := by native_decide

/-- compiler_p11_r19_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 19 1 + maximumLayerCompilerPrimeEnvelopeGap 11 19 1 = maximumLayerCompilerPrimeEnvelopeBound 11 19 1 ∧ maximumLayerCompilerTotalTests 11 19 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 19 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 19 1 ≤ maximumLayerCompilerTestBound 11 19 1 := by native_decide

/-- compiler_p13_r2_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 2 0 + maximumLayerCompilerPrimeEnvelopeGap 13 2 0 = maximumLayerCompilerPrimeEnvelopeBound 13 2 0 ∧ maximumLayerCompilerTotalTests 13 2 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 2 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 2 0 ≤ maximumLayerCompilerTestBound 13 2 0 := by native_decide

/-- compiler_p13_r4_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 4 2 + maximumLayerCompilerPrimeEnvelopeGap 13 4 2 = maximumLayerCompilerPrimeEnvelopeBound 13 4 2 ∧ maximumLayerCompilerTotalTests 13 4 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 4 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 4 2 ≤ maximumLayerCompilerTestBound 13 4 2 := by native_decide

/-- compiler_p13_r7_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 7 1 + maximumLayerCompilerPrimeEnvelopeGap 13 7 1 = maximumLayerCompilerPrimeEnvelopeBound 13 7 1 ∧ maximumLayerCompilerTotalTests 13 7 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 7 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 7 1 ≤ maximumLayerCompilerTestBound 13 7 1 := by native_decide

/-- compiler_p13_r10_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 10 0 + maximumLayerCompilerPrimeEnvelopeGap 13 10 0 = maximumLayerCompilerPrimeEnvelopeBound 13 10 0 ∧ maximumLayerCompilerTotalTests 13 10 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 10 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 10 0 ≤ maximumLayerCompilerTestBound 13 10 0 := by native_decide

/-- compiler_p13_r12_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 12 2 + maximumLayerCompilerPrimeEnvelopeGap 13 12 2 = maximumLayerCompilerPrimeEnvelopeBound 13 12 2 ∧ maximumLayerCompilerTotalTests 13 12 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 12 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 12 2 ≤ maximumLayerCompilerTestBound 13 12 2 := by native_decide

/-- compiler_p13_r15_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 15 1 + maximumLayerCompilerPrimeEnvelopeGap 13 15 1 = maximumLayerCompilerPrimeEnvelopeBound 13 15 1 ∧ maximumLayerCompilerTotalTests 13 15 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 15 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 15 1 ≤ maximumLayerCompilerTestBound 13 15 1 := by native_decide

/-- compiler_p13_r18_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 18 0 + maximumLayerCompilerPrimeEnvelopeGap 13 18 0 = maximumLayerCompilerPrimeEnvelopeBound 13 18 0 ∧ maximumLayerCompilerTotalTests 13 18 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 18 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 18 0 ≤ maximumLayerCompilerTestBound 13 18 0 := by native_decide

/-- compiler_p13_r20_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 20 2 + maximumLayerCompilerPrimeEnvelopeGap 13 20 2 = maximumLayerCompilerPrimeEnvelopeBound 13 20 2 ∧ maximumLayerCompilerTotalTests 13 20 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 20 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 20 2 ≤ maximumLayerCompilerTestBound 13 20 2 := by native_decide

end KomorebiPadic
