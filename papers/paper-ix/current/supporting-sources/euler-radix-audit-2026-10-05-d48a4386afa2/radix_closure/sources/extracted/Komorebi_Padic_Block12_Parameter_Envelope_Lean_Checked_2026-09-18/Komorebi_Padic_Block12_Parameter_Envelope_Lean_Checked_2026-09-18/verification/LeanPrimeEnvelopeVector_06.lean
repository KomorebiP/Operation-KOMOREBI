import KomorebiPadic

namespace KomorebiPadic

/-- representative_p1_B5 -/
example : radixRepresentativeBudget 1 5 + radixRepresentativeBudgetPrimeEnvelopeGap 1 5 = radixRepresentativeBudgetPrimeEnvelope 1 5 ∧ radixRepresentativeBudget 1 5 ≤ radixRepresentativeBudgetPrimeEnvelope 1 5 ∧ (radixRepresentativeBudget 1 5 = radixRepresentativeBudgetPrimeEnvelope 1 5 ↔ lastRadixBlockQuotient 1 5 = 0 ∨ lastRadixBlockRemainder 1 5 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 5 ≤ 5 * 5 := by native_decide

/-- representative_p1_B13 -/
example : radixRepresentativeBudget 1 13 + radixRepresentativeBudgetPrimeEnvelopeGap 1 13 = radixRepresentativeBudgetPrimeEnvelope 1 13 ∧ radixRepresentativeBudget 1 13 ≤ radixRepresentativeBudgetPrimeEnvelope 1 13 ∧ (radixRepresentativeBudget 1 13 = radixRepresentativeBudgetPrimeEnvelope 1 13 ↔ lastRadixBlockQuotient 1 13 = 0 ∨ lastRadixBlockRemainder 1 13 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 13 ≤ 13 * 13 := by native_decide

/-- representative_p1_B21 -/
example : radixRepresentativeBudget 1 21 + radixRepresentativeBudgetPrimeEnvelopeGap 1 21 = radixRepresentativeBudgetPrimeEnvelope 1 21 ∧ radixRepresentativeBudget 1 21 ≤ radixRepresentativeBudgetPrimeEnvelope 1 21 ∧ (radixRepresentativeBudget 1 21 = radixRepresentativeBudgetPrimeEnvelope 1 21 ↔ lastRadixBlockQuotient 1 21 = 0 ∨ lastRadixBlockRemainder 1 21 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 21 ≤ 21 * 21 := by native_decide

/-- representative_p1_B29 -/
example : radixRepresentativeBudget 1 29 + radixRepresentativeBudgetPrimeEnvelopeGap 1 29 = radixRepresentativeBudgetPrimeEnvelope 1 29 ∧ radixRepresentativeBudget 1 29 ≤ radixRepresentativeBudgetPrimeEnvelope 1 29 ∧ (radixRepresentativeBudget 1 29 = radixRepresentativeBudgetPrimeEnvelope 1 29 ↔ lastRadixBlockQuotient 1 29 = 0 ∨ lastRadixBlockRemainder 1 29 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 29 ≤ 29 * 29 := by native_decide

/-- representative_p1_B37 -/
example : radixRepresentativeBudget 1 37 + radixRepresentativeBudgetPrimeEnvelopeGap 1 37 = radixRepresentativeBudgetPrimeEnvelope 1 37 ∧ radixRepresentativeBudget 1 37 ≤ radixRepresentativeBudgetPrimeEnvelope 1 37 ∧ (radixRepresentativeBudget 1 37 = radixRepresentativeBudgetPrimeEnvelope 1 37 ↔ lastRadixBlockQuotient 1 37 = 0 ∨ lastRadixBlockRemainder 1 37 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 37 ≤ 37 * 37 := by native_decide

/-- representative_p1_B45 -/
example : radixRepresentativeBudget 1 45 + radixRepresentativeBudgetPrimeEnvelopeGap 1 45 = radixRepresentativeBudgetPrimeEnvelope 1 45 ∧ radixRepresentativeBudget 1 45 ≤ radixRepresentativeBudgetPrimeEnvelope 1 45 ∧ (radixRepresentativeBudget 1 45 = radixRepresentativeBudgetPrimeEnvelope 1 45 ↔ lastRadixBlockQuotient 1 45 = 0 ∨ lastRadixBlockRemainder 1 45 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 45 ≤ 45 * 45 := by native_decide

/-- representative_p2_B3 -/
example : radixRepresentativeBudget 2 3 + radixRepresentativeBudgetPrimeEnvelopeGap 2 3 = radixRepresentativeBudgetPrimeEnvelope 2 3 ∧ radixRepresentativeBudget 2 3 ≤ radixRepresentativeBudgetPrimeEnvelope 2 3 ∧ (radixRepresentativeBudget 2 3 = radixRepresentativeBudgetPrimeEnvelope 2 3 ↔ lastRadixBlockQuotient 2 3 = 0 ∨ lastRadixBlockRemainder 2 3 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 3 ≤ 3 * 3 := by native_decide

/-- representative_p2_B11 -/
example : radixRepresentativeBudget 2 11 + radixRepresentativeBudgetPrimeEnvelopeGap 2 11 = radixRepresentativeBudgetPrimeEnvelope 2 11 ∧ radixRepresentativeBudget 2 11 ≤ radixRepresentativeBudgetPrimeEnvelope 2 11 ∧ (radixRepresentativeBudget 2 11 = radixRepresentativeBudgetPrimeEnvelope 2 11 ↔ lastRadixBlockQuotient 2 11 = 0 ∨ lastRadixBlockRemainder 2 11 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 11 ≤ 11 * 11 := by native_decide

/-- representative_p2_B19 -/
example : radixRepresentativeBudget 2 19 + radixRepresentativeBudgetPrimeEnvelopeGap 2 19 = radixRepresentativeBudgetPrimeEnvelope 2 19 ∧ radixRepresentativeBudget 2 19 ≤ radixRepresentativeBudgetPrimeEnvelope 2 19 ∧ (radixRepresentativeBudget 2 19 = radixRepresentativeBudgetPrimeEnvelope 2 19 ↔ lastRadixBlockQuotient 2 19 = 0 ∨ lastRadixBlockRemainder 2 19 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 19 ≤ 19 * 19 := by native_decide

/-- representative_p2_B27 -/
example : radixRepresentativeBudget 2 27 + radixRepresentativeBudgetPrimeEnvelopeGap 2 27 = radixRepresentativeBudgetPrimeEnvelope 2 27 ∧ radixRepresentativeBudget 2 27 ≤ radixRepresentativeBudgetPrimeEnvelope 2 27 ∧ (radixRepresentativeBudget 2 27 = radixRepresentativeBudgetPrimeEnvelope 2 27 ↔ lastRadixBlockQuotient 2 27 = 0 ∨ lastRadixBlockRemainder 2 27 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 27 ≤ 27 * 27 := by native_decide

/-- representative_p2_B35 -/
example : radixRepresentativeBudget 2 35 + radixRepresentativeBudgetPrimeEnvelopeGap 2 35 = radixRepresentativeBudgetPrimeEnvelope 2 35 ∧ radixRepresentativeBudget 2 35 ≤ radixRepresentativeBudgetPrimeEnvelope 2 35 ∧ (radixRepresentativeBudget 2 35 = radixRepresentativeBudgetPrimeEnvelope 2 35 ↔ lastRadixBlockQuotient 2 35 = 0 ∨ lastRadixBlockRemainder 2 35 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 35 ≤ 35 * 35 := by native_decide

/-- representative_p2_B43 -/
example : radixRepresentativeBudget 2 43 + radixRepresentativeBudgetPrimeEnvelopeGap 2 43 = radixRepresentativeBudgetPrimeEnvelope 2 43 ∧ radixRepresentativeBudget 2 43 ≤ radixRepresentativeBudgetPrimeEnvelope 2 43 ∧ (radixRepresentativeBudget 2 43 = radixRepresentativeBudgetPrimeEnvelope 2 43 ↔ lastRadixBlockQuotient 2 43 = 0 ∨ lastRadixBlockRemainder 2 43 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 43 ≤ 43 * 43 := by native_decide

/-- representative_p3_B1 -/
example : radixRepresentativeBudget 3 1 + radixRepresentativeBudgetPrimeEnvelopeGap 3 1 = radixRepresentativeBudgetPrimeEnvelope 3 1 ∧ radixRepresentativeBudget 3 1 ≤ radixRepresentativeBudgetPrimeEnvelope 3 1 ∧ (radixRepresentativeBudget 3 1 = radixRepresentativeBudgetPrimeEnvelope 3 1 ↔ lastRadixBlockQuotient 3 1 = 0 ∨ lastRadixBlockRemainder 3 1 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 1 ≤ 1 * 1 := by native_decide

/-- representative_p3_B9 -/
example : radixRepresentativeBudget 3 9 + radixRepresentativeBudgetPrimeEnvelopeGap 3 9 = radixRepresentativeBudgetPrimeEnvelope 3 9 ∧ radixRepresentativeBudget 3 9 ≤ radixRepresentativeBudgetPrimeEnvelope 3 9 ∧ (radixRepresentativeBudget 3 9 = radixRepresentativeBudgetPrimeEnvelope 3 9 ↔ lastRadixBlockQuotient 3 9 = 0 ∨ lastRadixBlockRemainder 3 9 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 9 ≤ 9 * 9 := by native_decide

/-- representative_p3_B17 -/
example : radixRepresentativeBudget 3 17 + radixRepresentativeBudgetPrimeEnvelopeGap 3 17 = radixRepresentativeBudgetPrimeEnvelope 3 17 ∧ radixRepresentativeBudget 3 17 ≤ radixRepresentativeBudgetPrimeEnvelope 3 17 ∧ (radixRepresentativeBudget 3 17 = radixRepresentativeBudgetPrimeEnvelope 3 17 ↔ lastRadixBlockQuotient 3 17 = 0 ∨ lastRadixBlockRemainder 3 17 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 17 ≤ 17 * 17 := by native_decide

/-- representative_p3_B25 -/
example : radixRepresentativeBudget 3 25 + radixRepresentativeBudgetPrimeEnvelopeGap 3 25 = radixRepresentativeBudgetPrimeEnvelope 3 25 ∧ radixRepresentativeBudget 3 25 ≤ radixRepresentativeBudgetPrimeEnvelope 3 25 ∧ (radixRepresentativeBudget 3 25 = radixRepresentativeBudgetPrimeEnvelope 3 25 ↔ lastRadixBlockQuotient 3 25 = 0 ∨ lastRadixBlockRemainder 3 25 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 25 ≤ 25 * 25 := by native_decide

/-- representative_p3_B33 -/
example : radixRepresentativeBudget 3 33 + radixRepresentativeBudgetPrimeEnvelopeGap 3 33 = radixRepresentativeBudgetPrimeEnvelope 3 33 ∧ radixRepresentativeBudget 3 33 ≤ radixRepresentativeBudgetPrimeEnvelope 3 33 ∧ (radixRepresentativeBudget 3 33 = radixRepresentativeBudgetPrimeEnvelope 3 33 ↔ lastRadixBlockQuotient 3 33 = 0 ∨ lastRadixBlockRemainder 3 33 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 33 ≤ 33 * 33 := by native_decide

/-- representative_p3_B41 -/
example : radixRepresentativeBudget 3 41 + radixRepresentativeBudgetPrimeEnvelopeGap 3 41 = radixRepresentativeBudgetPrimeEnvelope 3 41 ∧ radixRepresentativeBudget 3 41 ≤ radixRepresentativeBudgetPrimeEnvelope 3 41 ∧ (radixRepresentativeBudget 3 41 = radixRepresentativeBudgetPrimeEnvelope 3 41 ↔ lastRadixBlockQuotient 3 41 = 0 ∨ lastRadixBlockRemainder 3 41 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 41 ≤ 41 * 41 := by native_decide

/-- representative_p3_B49 -/
example : radixRepresentativeBudget 3 49 + radixRepresentativeBudgetPrimeEnvelopeGap 3 49 = radixRepresentativeBudgetPrimeEnvelope 3 49 ∧ radixRepresentativeBudget 3 49 ≤ radixRepresentativeBudgetPrimeEnvelope 3 49 ∧ (radixRepresentativeBudget 3 49 = radixRepresentativeBudgetPrimeEnvelope 3 49 ↔ lastRadixBlockQuotient 3 49 = 0 ∨ lastRadixBlockRemainder 3 49 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 49 ≤ 49 * 49 := by native_decide

/-- representative_p4_B7 -/
example : radixRepresentativeBudget 4 7 + radixRepresentativeBudgetPrimeEnvelopeGap 4 7 = radixRepresentativeBudgetPrimeEnvelope 4 7 ∧ radixRepresentativeBudget 4 7 ≤ radixRepresentativeBudgetPrimeEnvelope 4 7 ∧ (radixRepresentativeBudget 4 7 = radixRepresentativeBudgetPrimeEnvelope 4 7 ↔ lastRadixBlockQuotient 4 7 = 0 ∨ lastRadixBlockRemainder 4 7 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 7 ≤ 7 * 7 := by native_decide

/-- representative_p4_B15 -/
example : radixRepresentativeBudget 4 15 + radixRepresentativeBudgetPrimeEnvelopeGap 4 15 = radixRepresentativeBudgetPrimeEnvelope 4 15 ∧ radixRepresentativeBudget 4 15 ≤ radixRepresentativeBudgetPrimeEnvelope 4 15 ∧ (radixRepresentativeBudget 4 15 = radixRepresentativeBudgetPrimeEnvelope 4 15 ↔ lastRadixBlockQuotient 4 15 = 0 ∨ lastRadixBlockRemainder 4 15 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 15 ≤ 15 * 15 := by native_decide

/-- representative_p4_B23 -/
example : radixRepresentativeBudget 4 23 + radixRepresentativeBudgetPrimeEnvelopeGap 4 23 = radixRepresentativeBudgetPrimeEnvelope 4 23 ∧ radixRepresentativeBudget 4 23 ≤ radixRepresentativeBudgetPrimeEnvelope 4 23 ∧ (radixRepresentativeBudget 4 23 = radixRepresentativeBudgetPrimeEnvelope 4 23 ↔ lastRadixBlockQuotient 4 23 = 0 ∨ lastRadixBlockRemainder 4 23 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 23 ≤ 23 * 23 := by native_decide

/-- representative_p4_B31 -/
example : radixRepresentativeBudget 4 31 + radixRepresentativeBudgetPrimeEnvelopeGap 4 31 = radixRepresentativeBudgetPrimeEnvelope 4 31 ∧ radixRepresentativeBudget 4 31 ≤ radixRepresentativeBudgetPrimeEnvelope 4 31 ∧ (radixRepresentativeBudget 4 31 = radixRepresentativeBudgetPrimeEnvelope 4 31 ↔ lastRadixBlockQuotient 4 31 = 0 ∨ lastRadixBlockRemainder 4 31 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 31 ≤ 31 * 31 := by native_decide

/-- representative_p4_B39 -/
example : radixRepresentativeBudget 4 39 + radixRepresentativeBudgetPrimeEnvelopeGap 4 39 = radixRepresentativeBudgetPrimeEnvelope 4 39 ∧ radixRepresentativeBudget 4 39 ≤ radixRepresentativeBudgetPrimeEnvelope 4 39 ∧ (radixRepresentativeBudget 4 39 = radixRepresentativeBudgetPrimeEnvelope 4 39 ↔ lastRadixBlockQuotient 4 39 = 0 ∨ lastRadixBlockRemainder 4 39 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 39 ≤ 39 * 39 := by native_decide

/-- representative_p4_B47 -/
example : radixRepresentativeBudget 4 47 + radixRepresentativeBudgetPrimeEnvelopeGap 4 47 = radixRepresentativeBudgetPrimeEnvelope 4 47 ∧ radixRepresentativeBudget 4 47 ≤ radixRepresentativeBudgetPrimeEnvelope 4 47 ∧ (radixRepresentativeBudget 4 47 = radixRepresentativeBudgetPrimeEnvelope 4 47 ↔ lastRadixBlockQuotient 4 47 = 0 ∨ lastRadixBlockRemainder 4 47 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 47 ≤ 47 * 47 := by native_decide

/-- representative_p5_B5 -/
example : radixRepresentativeBudget 5 5 + radixRepresentativeBudgetPrimeEnvelopeGap 5 5 = radixRepresentativeBudgetPrimeEnvelope 5 5 ∧ radixRepresentativeBudget 5 5 ≤ radixRepresentativeBudgetPrimeEnvelope 5 5 ∧ (radixRepresentativeBudget 5 5 = radixRepresentativeBudgetPrimeEnvelope 5 5 ↔ lastRadixBlockQuotient 5 5 = 0 ∨ lastRadixBlockRemainder 5 5 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 5 ≤ 5 * 5 := by native_decide

/-- representative_p5_B13 -/
example : radixRepresentativeBudget 5 13 + radixRepresentativeBudgetPrimeEnvelopeGap 5 13 = radixRepresentativeBudgetPrimeEnvelope 5 13 ∧ radixRepresentativeBudget 5 13 ≤ radixRepresentativeBudgetPrimeEnvelope 5 13 ∧ (radixRepresentativeBudget 5 13 = radixRepresentativeBudgetPrimeEnvelope 5 13 ↔ lastRadixBlockQuotient 5 13 = 0 ∨ lastRadixBlockRemainder 5 13 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 13 ≤ 13 * 13 := by native_decide

/-- representative_p5_B21 -/
example : radixRepresentativeBudget 5 21 + radixRepresentativeBudgetPrimeEnvelopeGap 5 21 = radixRepresentativeBudgetPrimeEnvelope 5 21 ∧ radixRepresentativeBudget 5 21 ≤ radixRepresentativeBudgetPrimeEnvelope 5 21 ∧ (radixRepresentativeBudget 5 21 = radixRepresentativeBudgetPrimeEnvelope 5 21 ↔ lastRadixBlockQuotient 5 21 = 0 ∨ lastRadixBlockRemainder 5 21 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 21 ≤ 21 * 21 := by native_decide

/-- representative_p5_B29 -/
example : radixRepresentativeBudget 5 29 + radixRepresentativeBudgetPrimeEnvelopeGap 5 29 = radixRepresentativeBudgetPrimeEnvelope 5 29 ∧ radixRepresentativeBudget 5 29 ≤ radixRepresentativeBudgetPrimeEnvelope 5 29 ∧ (radixRepresentativeBudget 5 29 = radixRepresentativeBudgetPrimeEnvelope 5 29 ↔ lastRadixBlockQuotient 5 29 = 0 ∨ lastRadixBlockRemainder 5 29 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 29 ≤ 29 * 29 := by native_decide

/-- representative_p5_B37 -/
example : radixRepresentativeBudget 5 37 + radixRepresentativeBudgetPrimeEnvelopeGap 5 37 = radixRepresentativeBudgetPrimeEnvelope 5 37 ∧ radixRepresentativeBudget 5 37 ≤ radixRepresentativeBudgetPrimeEnvelope 5 37 ∧ (radixRepresentativeBudget 5 37 = radixRepresentativeBudgetPrimeEnvelope 5 37 ↔ lastRadixBlockQuotient 5 37 = 0 ∨ lastRadixBlockRemainder 5 37 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 37 ≤ 37 * 37 := by native_decide

/-- representative_p5_B45 -/
example : radixRepresentativeBudget 5 45 + radixRepresentativeBudgetPrimeEnvelopeGap 5 45 = radixRepresentativeBudgetPrimeEnvelope 5 45 ∧ radixRepresentativeBudget 5 45 ≤ radixRepresentativeBudgetPrimeEnvelope 5 45 ∧ (radixRepresentativeBudget 5 45 = radixRepresentativeBudgetPrimeEnvelope 5 45 ↔ lastRadixBlockQuotient 5 45 = 0 ∨ lastRadixBlockRemainder 5 45 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 45 ≤ 45 * 45 := by native_decide

/-- representative_p6_B3 -/
example : radixRepresentativeBudget 6 3 + radixRepresentativeBudgetPrimeEnvelopeGap 6 3 = radixRepresentativeBudgetPrimeEnvelope 6 3 ∧ radixRepresentativeBudget 6 3 ≤ radixRepresentativeBudgetPrimeEnvelope 6 3 ∧ (radixRepresentativeBudget 6 3 = radixRepresentativeBudgetPrimeEnvelope 6 3 ↔ lastRadixBlockQuotient 6 3 = 0 ∨ lastRadixBlockRemainder 6 3 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 3 ≤ 3 * 3 := by native_decide

/-- representative_p6_B11 -/
example : radixRepresentativeBudget 6 11 + radixRepresentativeBudgetPrimeEnvelopeGap 6 11 = radixRepresentativeBudgetPrimeEnvelope 6 11 ∧ radixRepresentativeBudget 6 11 ≤ radixRepresentativeBudgetPrimeEnvelope 6 11 ∧ (radixRepresentativeBudget 6 11 = radixRepresentativeBudgetPrimeEnvelope 6 11 ↔ lastRadixBlockQuotient 6 11 = 0 ∨ lastRadixBlockRemainder 6 11 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 11 ≤ 11 * 11 := by native_decide

/-- representative_p6_B19 -/
example : radixRepresentativeBudget 6 19 + radixRepresentativeBudgetPrimeEnvelopeGap 6 19 = radixRepresentativeBudgetPrimeEnvelope 6 19 ∧ radixRepresentativeBudget 6 19 ≤ radixRepresentativeBudgetPrimeEnvelope 6 19 ∧ (radixRepresentativeBudget 6 19 = radixRepresentativeBudgetPrimeEnvelope 6 19 ↔ lastRadixBlockQuotient 6 19 = 0 ∨ lastRadixBlockRemainder 6 19 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 19 ≤ 19 * 19 := by native_decide

/-- representative_p6_B27 -/
example : radixRepresentativeBudget 6 27 + radixRepresentativeBudgetPrimeEnvelopeGap 6 27 = radixRepresentativeBudgetPrimeEnvelope 6 27 ∧ radixRepresentativeBudget 6 27 ≤ radixRepresentativeBudgetPrimeEnvelope 6 27 ∧ (radixRepresentativeBudget 6 27 = radixRepresentativeBudgetPrimeEnvelope 6 27 ↔ lastRadixBlockQuotient 6 27 = 0 ∨ lastRadixBlockRemainder 6 27 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 27 ≤ 27 * 27 := by native_decide

/-- representative_p6_B35 -/
example : radixRepresentativeBudget 6 35 + radixRepresentativeBudgetPrimeEnvelopeGap 6 35 = radixRepresentativeBudgetPrimeEnvelope 6 35 ∧ radixRepresentativeBudget 6 35 ≤ radixRepresentativeBudgetPrimeEnvelope 6 35 ∧ (radixRepresentativeBudget 6 35 = radixRepresentativeBudgetPrimeEnvelope 6 35 ↔ lastRadixBlockQuotient 6 35 = 0 ∨ lastRadixBlockRemainder 6 35 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 35 ≤ 35 * 35 := by native_decide

/-- representative_p6_B43 -/
example : radixRepresentativeBudget 6 43 + radixRepresentativeBudgetPrimeEnvelopeGap 6 43 = radixRepresentativeBudgetPrimeEnvelope 6 43 ∧ radixRepresentativeBudget 6 43 ≤ radixRepresentativeBudgetPrimeEnvelope 6 43 ∧ (radixRepresentativeBudget 6 43 = radixRepresentativeBudgetPrimeEnvelope 6 43 ↔ lastRadixBlockQuotient 6 43 = 0 ∨ lastRadixBlockRemainder 6 43 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 43 ≤ 43 * 43 := by native_decide

/-- representative_p7_B1 -/
example : radixRepresentativeBudget 7 1 + radixRepresentativeBudgetPrimeEnvelopeGap 7 1 = radixRepresentativeBudgetPrimeEnvelope 7 1 ∧ radixRepresentativeBudget 7 1 ≤ radixRepresentativeBudgetPrimeEnvelope 7 1 ∧ (radixRepresentativeBudget 7 1 = radixRepresentativeBudgetPrimeEnvelope 7 1 ↔ lastRadixBlockQuotient 7 1 = 0 ∨ lastRadixBlockRemainder 7 1 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 1 ≤ 1 * 1 := by native_decide

/-- representative_p7_B9 -/
example : radixRepresentativeBudget 7 9 + radixRepresentativeBudgetPrimeEnvelopeGap 7 9 = radixRepresentativeBudgetPrimeEnvelope 7 9 ∧ radixRepresentativeBudget 7 9 ≤ radixRepresentativeBudgetPrimeEnvelope 7 9 ∧ (radixRepresentativeBudget 7 9 = radixRepresentativeBudgetPrimeEnvelope 7 9 ↔ lastRadixBlockQuotient 7 9 = 0 ∨ lastRadixBlockRemainder 7 9 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 9 ≤ 9 * 9 := by native_decide

/-- representative_p7_B17 -/
example : radixRepresentativeBudget 7 17 + radixRepresentativeBudgetPrimeEnvelopeGap 7 17 = radixRepresentativeBudgetPrimeEnvelope 7 17 ∧ radixRepresentativeBudget 7 17 ≤ radixRepresentativeBudgetPrimeEnvelope 7 17 ∧ (radixRepresentativeBudget 7 17 = radixRepresentativeBudgetPrimeEnvelope 7 17 ↔ lastRadixBlockQuotient 7 17 = 0 ∨ lastRadixBlockRemainder 7 17 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 17 ≤ 17 * 17 := by native_decide

/-- representative_p7_B25 -/
example : radixRepresentativeBudget 7 25 + radixRepresentativeBudgetPrimeEnvelopeGap 7 25 = radixRepresentativeBudgetPrimeEnvelope 7 25 ∧ radixRepresentativeBudget 7 25 ≤ radixRepresentativeBudgetPrimeEnvelope 7 25 ∧ (radixRepresentativeBudget 7 25 = radixRepresentativeBudgetPrimeEnvelope 7 25 ↔ lastRadixBlockQuotient 7 25 = 0 ∨ lastRadixBlockRemainder 7 25 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 25 ≤ 25 * 25 := by native_decide

/-- representative_p7_B33 -/
example : radixRepresentativeBudget 7 33 + radixRepresentativeBudgetPrimeEnvelopeGap 7 33 = radixRepresentativeBudgetPrimeEnvelope 7 33 ∧ radixRepresentativeBudget 7 33 ≤ radixRepresentativeBudgetPrimeEnvelope 7 33 ∧ (radixRepresentativeBudget 7 33 = radixRepresentativeBudgetPrimeEnvelope 7 33 ↔ lastRadixBlockQuotient 7 33 = 0 ∨ lastRadixBlockRemainder 7 33 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 33 ≤ 33 * 33 := by native_decide

/-- representative_p7_B41 -/
example : radixRepresentativeBudget 7 41 + radixRepresentativeBudgetPrimeEnvelopeGap 7 41 = radixRepresentativeBudgetPrimeEnvelope 7 41 ∧ radixRepresentativeBudget 7 41 ≤ radixRepresentativeBudgetPrimeEnvelope 7 41 ∧ (radixRepresentativeBudget 7 41 = radixRepresentativeBudgetPrimeEnvelope 7 41 ↔ lastRadixBlockQuotient 7 41 = 0 ∨ lastRadixBlockRemainder 7 41 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 41 ≤ 41 * 41 := by native_decide

/-- representative_p7_B49 -/
example : radixRepresentativeBudget 7 49 + radixRepresentativeBudgetPrimeEnvelopeGap 7 49 = radixRepresentativeBudgetPrimeEnvelope 7 49 ∧ radixRepresentativeBudget 7 49 ≤ radixRepresentativeBudgetPrimeEnvelope 7 49 ∧ (radixRepresentativeBudget 7 49 = radixRepresentativeBudgetPrimeEnvelope 7 49 ↔ lastRadixBlockQuotient 7 49 = 0 ∨ lastRadixBlockRemainder 7 49 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 49 ≤ 49 * 49 := by native_decide

/-- representative_p8_B7 -/
example : radixRepresentativeBudget 8 7 + radixRepresentativeBudgetPrimeEnvelopeGap 8 7 = radixRepresentativeBudgetPrimeEnvelope 8 7 ∧ radixRepresentativeBudget 8 7 ≤ radixRepresentativeBudgetPrimeEnvelope 8 7 ∧ (radixRepresentativeBudget 8 7 = radixRepresentativeBudgetPrimeEnvelope 8 7 ↔ lastRadixBlockQuotient 8 7 = 0 ∨ lastRadixBlockRemainder 8 7 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 7 ≤ 7 * 7 := by native_decide

/-- representative_p8_B15 -/
example : radixRepresentativeBudget 8 15 + radixRepresentativeBudgetPrimeEnvelopeGap 8 15 = radixRepresentativeBudgetPrimeEnvelope 8 15 ∧ radixRepresentativeBudget 8 15 ≤ radixRepresentativeBudgetPrimeEnvelope 8 15 ∧ (radixRepresentativeBudget 8 15 = radixRepresentativeBudgetPrimeEnvelope 8 15 ↔ lastRadixBlockQuotient 8 15 = 0 ∨ lastRadixBlockRemainder 8 15 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 15 ≤ 15 * 15 := by native_decide

/-- representative_p8_B23 -/
example : radixRepresentativeBudget 8 23 + radixRepresentativeBudgetPrimeEnvelopeGap 8 23 = radixRepresentativeBudgetPrimeEnvelope 8 23 ∧ radixRepresentativeBudget 8 23 ≤ radixRepresentativeBudgetPrimeEnvelope 8 23 ∧ (radixRepresentativeBudget 8 23 = radixRepresentativeBudgetPrimeEnvelope 8 23 ↔ lastRadixBlockQuotient 8 23 = 0 ∨ lastRadixBlockRemainder 8 23 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 23 ≤ 23 * 23 := by native_decide

/-- representative_p8_B31 -/
example : radixRepresentativeBudget 8 31 + radixRepresentativeBudgetPrimeEnvelopeGap 8 31 = radixRepresentativeBudgetPrimeEnvelope 8 31 ∧ radixRepresentativeBudget 8 31 ≤ radixRepresentativeBudgetPrimeEnvelope 8 31 ∧ (radixRepresentativeBudget 8 31 = radixRepresentativeBudgetPrimeEnvelope 8 31 ↔ lastRadixBlockQuotient 8 31 = 0 ∨ lastRadixBlockRemainder 8 31 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 31 ≤ 31 * 31 := by native_decide

/-- representative_p8_B39 -/
example : radixRepresentativeBudget 8 39 + radixRepresentativeBudgetPrimeEnvelopeGap 8 39 = radixRepresentativeBudgetPrimeEnvelope 8 39 ∧ radixRepresentativeBudget 8 39 ≤ radixRepresentativeBudgetPrimeEnvelope 8 39 ∧ (radixRepresentativeBudget 8 39 = radixRepresentativeBudgetPrimeEnvelope 8 39 ↔ lastRadixBlockQuotient 8 39 = 0 ∨ lastRadixBlockRemainder 8 39 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 39 ≤ 39 * 39 := by native_decide

/-- representative_p8_B47 -/
example : radixRepresentativeBudget 8 47 + radixRepresentativeBudgetPrimeEnvelopeGap 8 47 = radixRepresentativeBudgetPrimeEnvelope 8 47 ∧ radixRepresentativeBudget 8 47 ≤ radixRepresentativeBudgetPrimeEnvelope 8 47 ∧ (radixRepresentativeBudget 8 47 = radixRepresentativeBudgetPrimeEnvelope 8 47 ↔ lastRadixBlockQuotient 8 47 = 0 ∨ lastRadixBlockRemainder 8 47 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 47 ≤ 47 * 47 := by native_decide

/-- representative_p9_B5 -/
example : radixRepresentativeBudget 9 5 + radixRepresentativeBudgetPrimeEnvelopeGap 9 5 = radixRepresentativeBudgetPrimeEnvelope 9 5 ∧ radixRepresentativeBudget 9 5 ≤ radixRepresentativeBudgetPrimeEnvelope 9 5 ∧ (radixRepresentativeBudget 9 5 = radixRepresentativeBudgetPrimeEnvelope 9 5 ↔ lastRadixBlockQuotient 9 5 = 0 ∨ lastRadixBlockRemainder 9 5 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 5 ≤ 5 * 5 := by native_decide

/-- representative_p9_B13 -/
example : radixRepresentativeBudget 9 13 + radixRepresentativeBudgetPrimeEnvelopeGap 9 13 = radixRepresentativeBudgetPrimeEnvelope 9 13 ∧ radixRepresentativeBudget 9 13 ≤ radixRepresentativeBudgetPrimeEnvelope 9 13 ∧ (radixRepresentativeBudget 9 13 = radixRepresentativeBudgetPrimeEnvelope 9 13 ↔ lastRadixBlockQuotient 9 13 = 0 ∨ lastRadixBlockRemainder 9 13 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 13 ≤ 13 * 13 := by native_decide

/-- representative_p9_B21 -/
example : radixRepresentativeBudget 9 21 + radixRepresentativeBudgetPrimeEnvelopeGap 9 21 = radixRepresentativeBudgetPrimeEnvelope 9 21 ∧ radixRepresentativeBudget 9 21 ≤ radixRepresentativeBudgetPrimeEnvelope 9 21 ∧ (radixRepresentativeBudget 9 21 = radixRepresentativeBudgetPrimeEnvelope 9 21 ↔ lastRadixBlockQuotient 9 21 = 0 ∨ lastRadixBlockRemainder 9 21 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 21 ≤ 21 * 21 := by native_decide

/-- representative_p9_B29 -/
example : radixRepresentativeBudget 9 29 + radixRepresentativeBudgetPrimeEnvelopeGap 9 29 = radixRepresentativeBudgetPrimeEnvelope 9 29 ∧ radixRepresentativeBudget 9 29 ≤ radixRepresentativeBudgetPrimeEnvelope 9 29 ∧ (radixRepresentativeBudget 9 29 = radixRepresentativeBudgetPrimeEnvelope 9 29 ↔ lastRadixBlockQuotient 9 29 = 0 ∨ lastRadixBlockRemainder 9 29 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 29 ≤ 29 * 29 := by native_decide

/-- representative_p9_B37 -/
example : radixRepresentativeBudget 9 37 + radixRepresentativeBudgetPrimeEnvelopeGap 9 37 = radixRepresentativeBudgetPrimeEnvelope 9 37 ∧ radixRepresentativeBudget 9 37 ≤ radixRepresentativeBudgetPrimeEnvelope 9 37 ∧ (radixRepresentativeBudget 9 37 = radixRepresentativeBudgetPrimeEnvelope 9 37 ↔ lastRadixBlockQuotient 9 37 = 0 ∨ lastRadixBlockRemainder 9 37 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 37 ≤ 37 * 37 := by native_decide

/-- representative_p9_B45 -/
example : radixRepresentativeBudget 9 45 + radixRepresentativeBudgetPrimeEnvelopeGap 9 45 = radixRepresentativeBudgetPrimeEnvelope 9 45 ∧ radixRepresentativeBudget 9 45 ≤ radixRepresentativeBudgetPrimeEnvelope 9 45 ∧ (radixRepresentativeBudget 9 45 = radixRepresentativeBudgetPrimeEnvelope 9 45 ↔ lastRadixBlockQuotient 9 45 = 0 ∨ lastRadixBlockRemainder 9 45 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 45 ≤ 45 * 45 := by native_decide

/-- representative_p10_B3 -/
example : radixRepresentativeBudget 10 3 + radixRepresentativeBudgetPrimeEnvelopeGap 10 3 = radixRepresentativeBudgetPrimeEnvelope 10 3 ∧ radixRepresentativeBudget 10 3 ≤ radixRepresentativeBudgetPrimeEnvelope 10 3 ∧ (radixRepresentativeBudget 10 3 = radixRepresentativeBudgetPrimeEnvelope 10 3 ↔ lastRadixBlockQuotient 10 3 = 0 ∨ lastRadixBlockRemainder 10 3 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 3 ≤ 3 * 3 := by native_decide

/-- representative_p10_B11 -/
example : radixRepresentativeBudget 10 11 + radixRepresentativeBudgetPrimeEnvelopeGap 10 11 = radixRepresentativeBudgetPrimeEnvelope 10 11 ∧ radixRepresentativeBudget 10 11 ≤ radixRepresentativeBudgetPrimeEnvelope 10 11 ∧ (radixRepresentativeBudget 10 11 = radixRepresentativeBudgetPrimeEnvelope 10 11 ↔ lastRadixBlockQuotient 10 11 = 0 ∨ lastRadixBlockRemainder 10 11 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 11 ≤ 11 * 11 := by native_decide

/-- representative_p10_B19 -/
example : radixRepresentativeBudget 10 19 + radixRepresentativeBudgetPrimeEnvelopeGap 10 19 = radixRepresentativeBudgetPrimeEnvelope 10 19 ∧ radixRepresentativeBudget 10 19 ≤ radixRepresentativeBudgetPrimeEnvelope 10 19 ∧ (radixRepresentativeBudget 10 19 = radixRepresentativeBudgetPrimeEnvelope 10 19 ↔ lastRadixBlockQuotient 10 19 = 0 ∨ lastRadixBlockRemainder 10 19 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 19 ≤ 19 * 19 := by native_decide

/-- representative_p10_B27 -/
example : radixRepresentativeBudget 10 27 + radixRepresentativeBudgetPrimeEnvelopeGap 10 27 = radixRepresentativeBudgetPrimeEnvelope 10 27 ∧ radixRepresentativeBudget 10 27 ≤ radixRepresentativeBudgetPrimeEnvelope 10 27 ∧ (radixRepresentativeBudget 10 27 = radixRepresentativeBudgetPrimeEnvelope 10 27 ↔ lastRadixBlockQuotient 10 27 = 0 ∨ lastRadixBlockRemainder 10 27 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 27 ≤ 27 * 27 := by native_decide

/-- representative_p10_B35 -/
example : radixRepresentativeBudget 10 35 + radixRepresentativeBudgetPrimeEnvelopeGap 10 35 = radixRepresentativeBudgetPrimeEnvelope 10 35 ∧ radixRepresentativeBudget 10 35 ≤ radixRepresentativeBudgetPrimeEnvelope 10 35 ∧ (radixRepresentativeBudget 10 35 = radixRepresentativeBudgetPrimeEnvelope 10 35 ↔ lastRadixBlockQuotient 10 35 = 0 ∨ lastRadixBlockRemainder 10 35 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 35 ≤ 35 * 35 := by native_decide

/-- representative_p10_B43 -/
example : radixRepresentativeBudget 10 43 + radixRepresentativeBudgetPrimeEnvelopeGap 10 43 = radixRepresentativeBudgetPrimeEnvelope 10 43 ∧ radixRepresentativeBudget 10 43 ≤ radixRepresentativeBudgetPrimeEnvelope 10 43 ∧ (radixRepresentativeBudget 10 43 = radixRepresentativeBudgetPrimeEnvelope 10 43 ↔ lastRadixBlockQuotient 10 43 = 0 ∨ lastRadixBlockRemainder 10 43 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 43 ≤ 43 * 43 := by native_decide

/-- representative_p11_B1 -/
example : radixRepresentativeBudget 11 1 + radixRepresentativeBudgetPrimeEnvelopeGap 11 1 = radixRepresentativeBudgetPrimeEnvelope 11 1 ∧ radixRepresentativeBudget 11 1 ≤ radixRepresentativeBudgetPrimeEnvelope 11 1 ∧ (radixRepresentativeBudget 11 1 = radixRepresentativeBudgetPrimeEnvelope 11 1 ↔ lastRadixBlockQuotient 11 1 = 0 ∨ lastRadixBlockRemainder 11 1 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 1 ≤ 1 * 1 := by native_decide

/-- representative_p11_B9 -/
example : radixRepresentativeBudget 11 9 + radixRepresentativeBudgetPrimeEnvelopeGap 11 9 = radixRepresentativeBudgetPrimeEnvelope 11 9 ∧ radixRepresentativeBudget 11 9 ≤ radixRepresentativeBudgetPrimeEnvelope 11 9 ∧ (radixRepresentativeBudget 11 9 = radixRepresentativeBudgetPrimeEnvelope 11 9 ↔ lastRadixBlockQuotient 11 9 = 0 ∨ lastRadixBlockRemainder 11 9 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 9 ≤ 9 * 9 := by native_decide

/-- representative_p11_B17 -/
example : radixRepresentativeBudget 11 17 + radixRepresentativeBudgetPrimeEnvelopeGap 11 17 = radixRepresentativeBudgetPrimeEnvelope 11 17 ∧ radixRepresentativeBudget 11 17 ≤ radixRepresentativeBudgetPrimeEnvelope 11 17 ∧ (radixRepresentativeBudget 11 17 = radixRepresentativeBudgetPrimeEnvelope 11 17 ↔ lastRadixBlockQuotient 11 17 = 0 ∨ lastRadixBlockRemainder 11 17 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 17 ≤ 17 * 17 := by native_decide

/-- representative_p11_B25 -/
example : radixRepresentativeBudget 11 25 + radixRepresentativeBudgetPrimeEnvelopeGap 11 25 = radixRepresentativeBudgetPrimeEnvelope 11 25 ∧ radixRepresentativeBudget 11 25 ≤ radixRepresentativeBudgetPrimeEnvelope 11 25 ∧ (radixRepresentativeBudget 11 25 = radixRepresentativeBudgetPrimeEnvelope 11 25 ↔ lastRadixBlockQuotient 11 25 = 0 ∨ lastRadixBlockRemainder 11 25 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 25 ≤ 25 * 25 := by native_decide

/-- representative_p11_B33 -/
example : radixRepresentativeBudget 11 33 + radixRepresentativeBudgetPrimeEnvelopeGap 11 33 = radixRepresentativeBudgetPrimeEnvelope 11 33 ∧ radixRepresentativeBudget 11 33 ≤ radixRepresentativeBudgetPrimeEnvelope 11 33 ∧ (radixRepresentativeBudget 11 33 = radixRepresentativeBudgetPrimeEnvelope 11 33 ↔ lastRadixBlockQuotient 11 33 = 0 ∨ lastRadixBlockRemainder 11 33 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 33 ≤ 33 * 33 := by native_decide

/-- representative_p11_B41 -/
example : radixRepresentativeBudget 11 41 + radixRepresentativeBudgetPrimeEnvelopeGap 11 41 = radixRepresentativeBudgetPrimeEnvelope 11 41 ∧ radixRepresentativeBudget 11 41 ≤ radixRepresentativeBudgetPrimeEnvelope 11 41 ∧ (radixRepresentativeBudget 11 41 = radixRepresentativeBudgetPrimeEnvelope 11 41 ↔ lastRadixBlockQuotient 11 41 = 0 ∨ lastRadixBlockRemainder 11 41 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 41 ≤ 41 * 41 := by native_decide

/-- representative_p11_B49 -/
example : radixRepresentativeBudget 11 49 + radixRepresentativeBudgetPrimeEnvelopeGap 11 49 = radixRepresentativeBudgetPrimeEnvelope 11 49 ∧ radixRepresentativeBudget 11 49 ≤ radixRepresentativeBudgetPrimeEnvelope 11 49 ∧ (radixRepresentativeBudget 11 49 = radixRepresentativeBudgetPrimeEnvelope 11 49 ↔ lastRadixBlockQuotient 11 49 = 0 ∨ lastRadixBlockRemainder 11 49 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 49 ≤ 49 * 49 := by native_decide

/-- representative_p12_B7 -/
example : radixRepresentativeBudget 12 7 + radixRepresentativeBudgetPrimeEnvelopeGap 12 7 = radixRepresentativeBudgetPrimeEnvelope 12 7 ∧ radixRepresentativeBudget 12 7 ≤ radixRepresentativeBudgetPrimeEnvelope 12 7 ∧ (radixRepresentativeBudget 12 7 = radixRepresentativeBudgetPrimeEnvelope 12 7 ↔ lastRadixBlockQuotient 12 7 = 0 ∨ lastRadixBlockRemainder 12 7 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 7 ≤ 7 * 7 := by native_decide

/-- representative_p12_B15 -/
example : radixRepresentativeBudget 12 15 + radixRepresentativeBudgetPrimeEnvelopeGap 12 15 = radixRepresentativeBudgetPrimeEnvelope 12 15 ∧ radixRepresentativeBudget 12 15 ≤ radixRepresentativeBudgetPrimeEnvelope 12 15 ∧ (radixRepresentativeBudget 12 15 = radixRepresentativeBudgetPrimeEnvelope 12 15 ↔ lastRadixBlockQuotient 12 15 = 0 ∨ lastRadixBlockRemainder 12 15 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 15 ≤ 15 * 15 := by native_decide

/-- representative_p12_B23 -/
example : radixRepresentativeBudget 12 23 + radixRepresentativeBudgetPrimeEnvelopeGap 12 23 = radixRepresentativeBudgetPrimeEnvelope 12 23 ∧ radixRepresentativeBudget 12 23 ≤ radixRepresentativeBudgetPrimeEnvelope 12 23 ∧ (radixRepresentativeBudget 12 23 = radixRepresentativeBudgetPrimeEnvelope 12 23 ↔ lastRadixBlockQuotient 12 23 = 0 ∨ lastRadixBlockRemainder 12 23 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 23 ≤ 23 * 23 := by native_decide

/-- representative_p12_B31 -/
example : radixRepresentativeBudget 12 31 + radixRepresentativeBudgetPrimeEnvelopeGap 12 31 = radixRepresentativeBudgetPrimeEnvelope 12 31 ∧ radixRepresentativeBudget 12 31 ≤ radixRepresentativeBudgetPrimeEnvelope 12 31 ∧ (radixRepresentativeBudget 12 31 = radixRepresentativeBudgetPrimeEnvelope 12 31 ↔ lastRadixBlockQuotient 12 31 = 0 ∨ lastRadixBlockRemainder 12 31 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 31 ≤ 31 * 31 := by native_decide

/-- representative_p12_B39 -/
example : radixRepresentativeBudget 12 39 + radixRepresentativeBudgetPrimeEnvelopeGap 12 39 = radixRepresentativeBudgetPrimeEnvelope 12 39 ∧ radixRepresentativeBudget 12 39 ≤ radixRepresentativeBudgetPrimeEnvelope 12 39 ∧ (radixRepresentativeBudget 12 39 = radixRepresentativeBudgetPrimeEnvelope 12 39 ↔ lastRadixBlockQuotient 12 39 = 0 ∨ lastRadixBlockRemainder 12 39 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 39 ≤ 39 * 39 := by native_decide

/-- representative_p12_B47 -/
example : radixRepresentativeBudget 12 47 + radixRepresentativeBudgetPrimeEnvelopeGap 12 47 = radixRepresentativeBudgetPrimeEnvelope 12 47 ∧ radixRepresentativeBudget 12 47 ≤ radixRepresentativeBudgetPrimeEnvelope 12 47 ∧ (radixRepresentativeBudget 12 47 = radixRepresentativeBudgetPrimeEnvelope 12 47 ↔ lastRadixBlockQuotient 12 47 = 0 ∨ lastRadixBlockRemainder 12 47 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 47 ≤ 47 * 47 := by native_decide

/-- zero_base_B5 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 5 ≤ 5 * 5 := by native_decide

/-- zero_base_B13 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 13 ≤ 13 * 13 := by native_decide

/-- zero_base_B21 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 21 ≤ 21 * 21 := by native_decide

/-- zero_base_B29 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 29 ≤ 29 * 29 := by native_decide

/-- zero_base_B37 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 37 ≤ 37 * 37 := by native_decide

/-- zero_base_B45 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 45 ≤ 45 * 45 := by native_decide

/-- zero_base_B53 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 53 ≤ 53 * 53 := by native_decide

/-- zero_base_B61 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 61 ≤ 61 * 61 := by native_decide

/-- zero_base_B69 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 69 ≤ 69 * 69 := by native_decide

/-- zero_base_B77 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 77 ≤ 77 * 77 := by native_decide

/-- zero_base_B85 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 85 ≤ 85 * 85 := by native_decide

/-- zero_base_B93 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 93 ≤ 93 * 93 := by native_decide

/-- zero_base_B101 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 101 ≤ 101 * 101 := by native_decide

/-- zero_base_B109 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 109 ≤ 109 * 109 := by native_decide

/-- zero_base_B117 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 117 ≤ 117 * 117 := by native_decide

/-- zero_base_B125 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 125 ≤ 125 * 125 := by native_decide

/-- zero_base_B133 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 133 ≤ 133 * 133 := by native_decide

/-- zero_base_B141 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 141 ≤ 141 * 141 := by native_decide

/-- zero_base_B149 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 149 ≤ 149 * 149 := by native_decide

/-- zero_base_B157 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 157 ≤ 157 * 157 := by native_decide

/-- zero_base_B165 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 165 ≤ 165 * 165 := by native_decide

/-- zero_base_B173 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 173 ≤ 173 * 173 := by native_decide

/-- zero_base_B181 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 181 ≤ 181 * 181 := by native_decide

/-- zero_base_B189 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 189 ≤ 189 * 189 := by native_decide

/-- zero_base_B197 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 197 ≤ 197 * 197 := by native_decide

/-- compiler_p2_r2_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 2 2 + maximumLayerCompilerPrimeEnvelopeGap 2 2 2 = maximumLayerCompilerPrimeEnvelopeBound 2 2 2 ∧ maximumLayerCompilerTotalTests 2 2 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 2 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 2 2 ≤ maximumLayerCompilerTestBound 2 2 2 := by native_decide

/-- compiler_p2_r5_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 5 1 + maximumLayerCompilerPrimeEnvelopeGap 2 5 1 = maximumLayerCompilerPrimeEnvelopeBound 2 5 1 ∧ maximumLayerCompilerTotalTests 2 5 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 5 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 5 1 ≤ maximumLayerCompilerTestBound 2 5 1 := by native_decide

/-- compiler_p2_r8_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 8 0 + maximumLayerCompilerPrimeEnvelopeGap 2 8 0 = maximumLayerCompilerPrimeEnvelopeBound 2 8 0 ∧ maximumLayerCompilerTotalTests 2 8 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 8 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 8 0 ≤ maximumLayerCompilerTestBound 2 8 0 := by native_decide

/-- compiler_p2_r10_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 10 2 + maximumLayerCompilerPrimeEnvelopeGap 2 10 2 = maximumLayerCompilerPrimeEnvelopeBound 2 10 2 ∧ maximumLayerCompilerTotalTests 2 10 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 10 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 10 2 ≤ maximumLayerCompilerTestBound 2 10 2 := by native_decide

/-- compiler_p2_r13_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 13 1 + maximumLayerCompilerPrimeEnvelopeGap 2 13 1 = maximumLayerCompilerPrimeEnvelopeBound 2 13 1 ∧ maximumLayerCompilerTotalTests 2 13 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 13 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 13 1 ≤ maximumLayerCompilerTestBound 2 13 1 := by native_decide

/-- compiler_p2_r16_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 16 0 + maximumLayerCompilerPrimeEnvelopeGap 2 16 0 = maximumLayerCompilerPrimeEnvelopeBound 2 16 0 ∧ maximumLayerCompilerTotalTests 2 16 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 16 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 16 0 ≤ maximumLayerCompilerTestBound 2 16 0 := by native_decide

/-- compiler_p2_r18_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 18 2 + maximumLayerCompilerPrimeEnvelopeGap 2 18 2 = maximumLayerCompilerPrimeEnvelopeBound 2 18 2 ∧ maximumLayerCompilerTotalTests 2 18 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 18 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 18 2 ≤ maximumLayerCompilerTestBound 2 18 2 := by native_decide

/-- compiler_p3_r1_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 1 1 + maximumLayerCompilerPrimeEnvelopeGap 3 1 1 = maximumLayerCompilerPrimeEnvelopeBound 3 1 1 ∧ maximumLayerCompilerTotalTests 3 1 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 1 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 1 1 ≤ maximumLayerCompilerTestBound 3 1 1 := by native_decide

/-- compiler_p3_r4_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 4 0 + maximumLayerCompilerPrimeEnvelopeGap 3 4 0 = maximumLayerCompilerPrimeEnvelopeBound 3 4 0 ∧ maximumLayerCompilerTotalTests 3 4 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 4 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 4 0 ≤ maximumLayerCompilerTestBound 3 4 0 := by native_decide

/-- compiler_p3_r6_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 6 2 + maximumLayerCompilerPrimeEnvelopeGap 3 6 2 = maximumLayerCompilerPrimeEnvelopeBound 3 6 2 ∧ maximumLayerCompilerTotalTests 3 6 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 6 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 6 2 ≤ maximumLayerCompilerTestBound 3 6 2 := by native_decide

/-- compiler_p3_r9_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 9 1 + maximumLayerCompilerPrimeEnvelopeGap 3 9 1 = maximumLayerCompilerPrimeEnvelopeBound 3 9 1 ∧ maximumLayerCompilerTotalTests 3 9 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 9 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 9 1 ≤ maximumLayerCompilerTestBound 3 9 1 := by native_decide

/-- compiler_p3_r12_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 12 0 + maximumLayerCompilerPrimeEnvelopeGap 3 12 0 = maximumLayerCompilerPrimeEnvelopeBound 3 12 0 ∧ maximumLayerCompilerTotalTests 3 12 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 12 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 12 0 ≤ maximumLayerCompilerTestBound 3 12 0 := by native_decide

/-- compiler_p3_r14_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 14 2 + maximumLayerCompilerPrimeEnvelopeGap 3 14 2 = maximumLayerCompilerPrimeEnvelopeBound 3 14 2 ∧ maximumLayerCompilerTotalTests 3 14 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 14 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 14 2 ≤ maximumLayerCompilerTestBound 3 14 2 := by native_decide

/-- compiler_p3_r17_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 17 1 + maximumLayerCompilerPrimeEnvelopeGap 3 17 1 = maximumLayerCompilerPrimeEnvelopeBound 3 17 1 ∧ maximumLayerCompilerTotalTests 3 17 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 17 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 17 1 ≤ maximumLayerCompilerTestBound 3 17 1 := by native_decide

/-- compiler_p3_r20_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 20 0 + maximumLayerCompilerPrimeEnvelopeGap 3 20 0 = maximumLayerCompilerPrimeEnvelopeBound 3 20 0 ∧ maximumLayerCompilerTotalTests 3 20 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 20 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 20 0 ≤ maximumLayerCompilerTestBound 3 20 0 := by native_decide

/-- compiler_p5_r2_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 2 2 + maximumLayerCompilerPrimeEnvelopeGap 5 2 2 = maximumLayerCompilerPrimeEnvelopeBound 5 2 2 ∧ maximumLayerCompilerTotalTests 5 2 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 2 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 2 2 ≤ maximumLayerCompilerTestBound 5 2 2 := by native_decide

/-- compiler_p5_r5_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 5 1 + maximumLayerCompilerPrimeEnvelopeGap 5 5 1 = maximumLayerCompilerPrimeEnvelopeBound 5 5 1 ∧ maximumLayerCompilerTotalTests 5 5 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 5 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 5 1 ≤ maximumLayerCompilerTestBound 5 5 1 := by native_decide

/-- compiler_p5_r8_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 8 0 + maximumLayerCompilerPrimeEnvelopeGap 5 8 0 = maximumLayerCompilerPrimeEnvelopeBound 5 8 0 ∧ maximumLayerCompilerTotalTests 5 8 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 8 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 8 0 ≤ maximumLayerCompilerTestBound 5 8 0 := by native_decide

/-- compiler_p5_r10_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 10 2 + maximumLayerCompilerPrimeEnvelopeGap 5 10 2 = maximumLayerCompilerPrimeEnvelopeBound 5 10 2 ∧ maximumLayerCompilerTotalTests 5 10 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 10 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 10 2 ≤ maximumLayerCompilerTestBound 5 10 2 := by native_decide

/-- compiler_p5_r13_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 13 1 + maximumLayerCompilerPrimeEnvelopeGap 5 13 1 = maximumLayerCompilerPrimeEnvelopeBound 5 13 1 ∧ maximumLayerCompilerTotalTests 5 13 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 13 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 13 1 ≤ maximumLayerCompilerTestBound 5 13 1 := by native_decide

/-- compiler_p5_r16_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 16 0 + maximumLayerCompilerPrimeEnvelopeGap 5 16 0 = maximumLayerCompilerPrimeEnvelopeBound 5 16 0 ∧ maximumLayerCompilerTotalTests 5 16 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 16 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 16 0 ≤ maximumLayerCompilerTestBound 5 16 0 := by native_decide

/-- compiler_p5_r18_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 18 2 + maximumLayerCompilerPrimeEnvelopeGap 5 18 2 = maximumLayerCompilerPrimeEnvelopeBound 5 18 2 ∧ maximumLayerCompilerTotalTests 5 18 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 18 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 18 2 ≤ maximumLayerCompilerTestBound 5 18 2 := by native_decide

/-- compiler_p7_r1_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 1 1 + maximumLayerCompilerPrimeEnvelopeGap 7 1 1 = maximumLayerCompilerPrimeEnvelopeBound 7 1 1 ∧ maximumLayerCompilerTotalTests 7 1 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 1 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 1 1 ≤ maximumLayerCompilerTestBound 7 1 1 := by native_decide

/-- compiler_p7_r4_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 4 0 + maximumLayerCompilerPrimeEnvelopeGap 7 4 0 = maximumLayerCompilerPrimeEnvelopeBound 7 4 0 ∧ maximumLayerCompilerTotalTests 7 4 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 4 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 4 0 ≤ maximumLayerCompilerTestBound 7 4 0 := by native_decide

/-- compiler_p7_r6_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 6 2 + maximumLayerCompilerPrimeEnvelopeGap 7 6 2 = maximumLayerCompilerPrimeEnvelopeBound 7 6 2 ∧ maximumLayerCompilerTotalTests 7 6 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 6 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 6 2 ≤ maximumLayerCompilerTestBound 7 6 2 := by native_decide

/-- compiler_p7_r9_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 9 1 + maximumLayerCompilerPrimeEnvelopeGap 7 9 1 = maximumLayerCompilerPrimeEnvelopeBound 7 9 1 ∧ maximumLayerCompilerTotalTests 7 9 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 9 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 9 1 ≤ maximumLayerCompilerTestBound 7 9 1 := by native_decide

/-- compiler_p7_r12_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 12 0 + maximumLayerCompilerPrimeEnvelopeGap 7 12 0 = maximumLayerCompilerPrimeEnvelopeBound 7 12 0 ∧ maximumLayerCompilerTotalTests 7 12 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 12 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 12 0 ≤ maximumLayerCompilerTestBound 7 12 0 := by native_decide

/-- compiler_p7_r14_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 14 2 + maximumLayerCompilerPrimeEnvelopeGap 7 14 2 = maximumLayerCompilerPrimeEnvelopeBound 7 14 2 ∧ maximumLayerCompilerTotalTests 7 14 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 14 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 14 2 ≤ maximumLayerCompilerTestBound 7 14 2 := by native_decide

/-- compiler_p7_r17_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 17 1 + maximumLayerCompilerPrimeEnvelopeGap 7 17 1 = maximumLayerCompilerPrimeEnvelopeBound 7 17 1 ∧ maximumLayerCompilerTotalTests 7 17 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 17 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 17 1 ≤ maximumLayerCompilerTestBound 7 17 1 := by native_decide

/-- compiler_p7_r20_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 20 0 + maximumLayerCompilerPrimeEnvelopeGap 7 20 0 = maximumLayerCompilerPrimeEnvelopeBound 7 20 0 ∧ maximumLayerCompilerTotalTests 7 20 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 20 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 20 0 ≤ maximumLayerCompilerTestBound 7 20 0 := by native_decide

/-- compiler_p11_r2_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 2 2 + maximumLayerCompilerPrimeEnvelopeGap 11 2 2 = maximumLayerCompilerPrimeEnvelopeBound 11 2 2 ∧ maximumLayerCompilerTotalTests 11 2 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 2 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 2 2 ≤ maximumLayerCompilerTestBound 11 2 2 := by native_decide

/-- compiler_p11_r5_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 5 1 + maximumLayerCompilerPrimeEnvelopeGap 11 5 1 = maximumLayerCompilerPrimeEnvelopeBound 11 5 1 ∧ maximumLayerCompilerTotalTests 11 5 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 5 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 5 1 ≤ maximumLayerCompilerTestBound 11 5 1 := by native_decide

/-- compiler_p11_r8_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 8 0 + maximumLayerCompilerPrimeEnvelopeGap 11 8 0 = maximumLayerCompilerPrimeEnvelopeBound 11 8 0 ∧ maximumLayerCompilerTotalTests 11 8 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 8 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 8 0 ≤ maximumLayerCompilerTestBound 11 8 0 := by native_decide

/-- compiler_p11_r10_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 10 2 + maximumLayerCompilerPrimeEnvelopeGap 11 10 2 = maximumLayerCompilerPrimeEnvelopeBound 11 10 2 ∧ maximumLayerCompilerTotalTests 11 10 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 10 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 10 2 ≤ maximumLayerCompilerTestBound 11 10 2 := by native_decide

/-- compiler_p11_r13_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 13 1 + maximumLayerCompilerPrimeEnvelopeGap 11 13 1 = maximumLayerCompilerPrimeEnvelopeBound 11 13 1 ∧ maximumLayerCompilerTotalTests 11 13 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 13 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 13 1 ≤ maximumLayerCompilerTestBound 11 13 1 := by native_decide

/-- compiler_p11_r16_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 16 0 + maximumLayerCompilerPrimeEnvelopeGap 11 16 0 = maximumLayerCompilerPrimeEnvelopeBound 11 16 0 ∧ maximumLayerCompilerTotalTests 11 16 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 16 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 16 0 ≤ maximumLayerCompilerTestBound 11 16 0 := by native_decide

/-- compiler_p11_r18_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 18 2 + maximumLayerCompilerPrimeEnvelopeGap 11 18 2 = maximumLayerCompilerPrimeEnvelopeBound 11 18 2 ∧ maximumLayerCompilerTotalTests 11 18 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 18 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 18 2 ≤ maximumLayerCompilerTestBound 11 18 2 := by native_decide

/-- compiler_p13_r1_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 1 1 + maximumLayerCompilerPrimeEnvelopeGap 13 1 1 = maximumLayerCompilerPrimeEnvelopeBound 13 1 1 ∧ maximumLayerCompilerTotalTests 13 1 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 1 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 1 1 ≤ maximumLayerCompilerTestBound 13 1 1 := by native_decide

/-- compiler_p13_r4_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 4 0 + maximumLayerCompilerPrimeEnvelopeGap 13 4 0 = maximumLayerCompilerPrimeEnvelopeBound 13 4 0 ∧ maximumLayerCompilerTotalTests 13 4 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 4 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 4 0 ≤ maximumLayerCompilerTestBound 13 4 0 := by native_decide

/-- compiler_p13_r6_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 6 2 + maximumLayerCompilerPrimeEnvelopeGap 13 6 2 = maximumLayerCompilerPrimeEnvelopeBound 13 6 2 ∧ maximumLayerCompilerTotalTests 13 6 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 6 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 6 2 ≤ maximumLayerCompilerTestBound 13 6 2 := by native_decide

/-- compiler_p13_r9_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 9 1 + maximumLayerCompilerPrimeEnvelopeGap 13 9 1 = maximumLayerCompilerPrimeEnvelopeBound 13 9 1 ∧ maximumLayerCompilerTotalTests 13 9 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 9 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 9 1 ≤ maximumLayerCompilerTestBound 13 9 1 := by native_decide

/-- compiler_p13_r12_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 12 0 + maximumLayerCompilerPrimeEnvelopeGap 13 12 0 = maximumLayerCompilerPrimeEnvelopeBound 13 12 0 ∧ maximumLayerCompilerTotalTests 13 12 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 12 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 12 0 ≤ maximumLayerCompilerTestBound 13 12 0 := by native_decide

/-- compiler_p13_r14_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 14 2 + maximumLayerCompilerPrimeEnvelopeGap 13 14 2 = maximumLayerCompilerPrimeEnvelopeBound 13 14 2 ∧ maximumLayerCompilerTotalTests 13 14 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 14 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 14 2 ≤ maximumLayerCompilerTestBound 13 14 2 := by native_decide

/-- compiler_p13_r17_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 17 1 + maximumLayerCompilerPrimeEnvelopeGap 13 17 1 = maximumLayerCompilerPrimeEnvelopeBound 13 17 1 ∧ maximumLayerCompilerTotalTests 13 17 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 17 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 17 1 ≤ maximumLayerCompilerTestBound 13 17 1 := by native_decide

/-- compiler_p13_r20_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 20 0 + maximumLayerCompilerPrimeEnvelopeGap 13 20 0 = maximumLayerCompilerPrimeEnvelopeBound 13 20 0 ∧ maximumLayerCompilerTotalTests 13 20 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 20 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 20 0 ≤ maximumLayerCompilerTestBound 13 20 0 := by native_decide

end KomorebiPadic
