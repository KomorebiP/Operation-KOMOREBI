import KomorebiPadic

namespace KomorebiPadic

/-- representative_p1_B1 -/
example : radixRepresentativeBudget 1 1 + radixRepresentativeBudgetPrimeEnvelopeGap 1 1 = radixRepresentativeBudgetPrimeEnvelope 1 1 ∧ radixRepresentativeBudget 1 1 ≤ radixRepresentativeBudgetPrimeEnvelope 1 1 ∧ (radixRepresentativeBudget 1 1 = radixRepresentativeBudgetPrimeEnvelope 1 1 ↔ lastRadixBlockQuotient 1 1 = 0 ∨ lastRadixBlockRemainder 1 1 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 1 ≤ 1 * 1 := by native_decide

/-- representative_p1_B9 -/
example : radixRepresentativeBudget 1 9 + radixRepresentativeBudgetPrimeEnvelopeGap 1 9 = radixRepresentativeBudgetPrimeEnvelope 1 9 ∧ radixRepresentativeBudget 1 9 ≤ radixRepresentativeBudgetPrimeEnvelope 1 9 ∧ (radixRepresentativeBudget 1 9 = radixRepresentativeBudgetPrimeEnvelope 1 9 ↔ lastRadixBlockQuotient 1 9 = 0 ∨ lastRadixBlockRemainder 1 9 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 9 ≤ 9 * 9 := by native_decide

/-- representative_p1_B17 -/
example : radixRepresentativeBudget 1 17 + radixRepresentativeBudgetPrimeEnvelopeGap 1 17 = radixRepresentativeBudgetPrimeEnvelope 1 17 ∧ radixRepresentativeBudget 1 17 ≤ radixRepresentativeBudgetPrimeEnvelope 1 17 ∧ (radixRepresentativeBudget 1 17 = radixRepresentativeBudgetPrimeEnvelope 1 17 ↔ lastRadixBlockQuotient 1 17 = 0 ∨ lastRadixBlockRemainder 1 17 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 17 ≤ 17 * 17 := by native_decide

/-- representative_p1_B25 -/
example : radixRepresentativeBudget 1 25 + radixRepresentativeBudgetPrimeEnvelopeGap 1 25 = radixRepresentativeBudgetPrimeEnvelope 1 25 ∧ radixRepresentativeBudget 1 25 ≤ radixRepresentativeBudgetPrimeEnvelope 1 25 ∧ (radixRepresentativeBudget 1 25 = radixRepresentativeBudgetPrimeEnvelope 1 25 ↔ lastRadixBlockQuotient 1 25 = 0 ∨ lastRadixBlockRemainder 1 25 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 25 ≤ 25 * 25 := by native_decide

/-- representative_p1_B33 -/
example : radixRepresentativeBudget 1 33 + radixRepresentativeBudgetPrimeEnvelopeGap 1 33 = radixRepresentativeBudgetPrimeEnvelope 1 33 ∧ radixRepresentativeBudget 1 33 ≤ radixRepresentativeBudgetPrimeEnvelope 1 33 ∧ (radixRepresentativeBudget 1 33 = radixRepresentativeBudgetPrimeEnvelope 1 33 ↔ lastRadixBlockQuotient 1 33 = 0 ∨ lastRadixBlockRemainder 1 33 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 33 ≤ 33 * 33 := by native_decide

/-- representative_p1_B41 -/
example : radixRepresentativeBudget 1 41 + radixRepresentativeBudgetPrimeEnvelopeGap 1 41 = radixRepresentativeBudgetPrimeEnvelope 1 41 ∧ radixRepresentativeBudget 1 41 ≤ radixRepresentativeBudgetPrimeEnvelope 1 41 ∧ (radixRepresentativeBudget 1 41 = radixRepresentativeBudgetPrimeEnvelope 1 41 ↔ lastRadixBlockQuotient 1 41 = 0 ∨ lastRadixBlockRemainder 1 41 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 41 ≤ 41 * 41 := by native_decide

/-- representative_p1_B49 -/
example : radixRepresentativeBudget 1 49 + radixRepresentativeBudgetPrimeEnvelopeGap 1 49 = radixRepresentativeBudgetPrimeEnvelope 1 49 ∧ radixRepresentativeBudget 1 49 ≤ radixRepresentativeBudgetPrimeEnvelope 1 49 ∧ (radixRepresentativeBudget 1 49 = radixRepresentativeBudgetPrimeEnvelope 1 49 ↔ lastRadixBlockQuotient 1 49 = 0 ∨ lastRadixBlockRemainder 1 49 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 49 ≤ 49 * 49 := by native_decide

/-- representative_p2_B7 -/
example : radixRepresentativeBudget 2 7 + radixRepresentativeBudgetPrimeEnvelopeGap 2 7 = radixRepresentativeBudgetPrimeEnvelope 2 7 ∧ radixRepresentativeBudget 2 7 ≤ radixRepresentativeBudgetPrimeEnvelope 2 7 ∧ (radixRepresentativeBudget 2 7 = radixRepresentativeBudgetPrimeEnvelope 2 7 ↔ lastRadixBlockQuotient 2 7 = 0 ∨ lastRadixBlockRemainder 2 7 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 7 ≤ 7 * 7 := by native_decide

/-- representative_p2_B15 -/
example : radixRepresentativeBudget 2 15 + radixRepresentativeBudgetPrimeEnvelopeGap 2 15 = radixRepresentativeBudgetPrimeEnvelope 2 15 ∧ radixRepresentativeBudget 2 15 ≤ radixRepresentativeBudgetPrimeEnvelope 2 15 ∧ (radixRepresentativeBudget 2 15 = radixRepresentativeBudgetPrimeEnvelope 2 15 ↔ lastRadixBlockQuotient 2 15 = 0 ∨ lastRadixBlockRemainder 2 15 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 15 ≤ 15 * 15 := by native_decide

/-- representative_p2_B23 -/
example : radixRepresentativeBudget 2 23 + radixRepresentativeBudgetPrimeEnvelopeGap 2 23 = radixRepresentativeBudgetPrimeEnvelope 2 23 ∧ radixRepresentativeBudget 2 23 ≤ radixRepresentativeBudgetPrimeEnvelope 2 23 ∧ (radixRepresentativeBudget 2 23 = radixRepresentativeBudgetPrimeEnvelope 2 23 ↔ lastRadixBlockQuotient 2 23 = 0 ∨ lastRadixBlockRemainder 2 23 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 23 ≤ 23 * 23 := by native_decide

/-- representative_p2_B31 -/
example : radixRepresentativeBudget 2 31 + radixRepresentativeBudgetPrimeEnvelopeGap 2 31 = radixRepresentativeBudgetPrimeEnvelope 2 31 ∧ radixRepresentativeBudget 2 31 ≤ radixRepresentativeBudgetPrimeEnvelope 2 31 ∧ (radixRepresentativeBudget 2 31 = radixRepresentativeBudgetPrimeEnvelope 2 31 ↔ lastRadixBlockQuotient 2 31 = 0 ∨ lastRadixBlockRemainder 2 31 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 31 ≤ 31 * 31 := by native_decide

/-- representative_p2_B39 -/
example : radixRepresentativeBudget 2 39 + radixRepresentativeBudgetPrimeEnvelopeGap 2 39 = radixRepresentativeBudgetPrimeEnvelope 2 39 ∧ radixRepresentativeBudget 2 39 ≤ radixRepresentativeBudgetPrimeEnvelope 2 39 ∧ (radixRepresentativeBudget 2 39 = radixRepresentativeBudgetPrimeEnvelope 2 39 ↔ lastRadixBlockQuotient 2 39 = 0 ∨ lastRadixBlockRemainder 2 39 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 39 ≤ 39 * 39 := by native_decide

/-- representative_p2_B47 -/
example : radixRepresentativeBudget 2 47 + radixRepresentativeBudgetPrimeEnvelopeGap 2 47 = radixRepresentativeBudgetPrimeEnvelope 2 47 ∧ radixRepresentativeBudget 2 47 ≤ radixRepresentativeBudgetPrimeEnvelope 2 47 ∧ (radixRepresentativeBudget 2 47 = radixRepresentativeBudgetPrimeEnvelope 2 47 ↔ lastRadixBlockQuotient 2 47 = 0 ∨ lastRadixBlockRemainder 2 47 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 47 ≤ 47 * 47 := by native_decide

/-- representative_p3_B5 -/
example : radixRepresentativeBudget 3 5 + radixRepresentativeBudgetPrimeEnvelopeGap 3 5 = radixRepresentativeBudgetPrimeEnvelope 3 5 ∧ radixRepresentativeBudget 3 5 ≤ radixRepresentativeBudgetPrimeEnvelope 3 5 ∧ (radixRepresentativeBudget 3 5 = radixRepresentativeBudgetPrimeEnvelope 3 5 ↔ lastRadixBlockQuotient 3 5 = 0 ∨ lastRadixBlockRemainder 3 5 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 5 ≤ 5 * 5 := by native_decide

/-- representative_p3_B13 -/
example : radixRepresentativeBudget 3 13 + radixRepresentativeBudgetPrimeEnvelopeGap 3 13 = radixRepresentativeBudgetPrimeEnvelope 3 13 ∧ radixRepresentativeBudget 3 13 ≤ radixRepresentativeBudgetPrimeEnvelope 3 13 ∧ (radixRepresentativeBudget 3 13 = radixRepresentativeBudgetPrimeEnvelope 3 13 ↔ lastRadixBlockQuotient 3 13 = 0 ∨ lastRadixBlockRemainder 3 13 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 13 ≤ 13 * 13 := by native_decide

/-- representative_p3_B21 -/
example : radixRepresentativeBudget 3 21 + radixRepresentativeBudgetPrimeEnvelopeGap 3 21 = radixRepresentativeBudgetPrimeEnvelope 3 21 ∧ radixRepresentativeBudget 3 21 ≤ radixRepresentativeBudgetPrimeEnvelope 3 21 ∧ (radixRepresentativeBudget 3 21 = radixRepresentativeBudgetPrimeEnvelope 3 21 ↔ lastRadixBlockQuotient 3 21 = 0 ∨ lastRadixBlockRemainder 3 21 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 21 ≤ 21 * 21 := by native_decide

/-- representative_p3_B29 -/
example : radixRepresentativeBudget 3 29 + radixRepresentativeBudgetPrimeEnvelopeGap 3 29 = radixRepresentativeBudgetPrimeEnvelope 3 29 ∧ radixRepresentativeBudget 3 29 ≤ radixRepresentativeBudgetPrimeEnvelope 3 29 ∧ (radixRepresentativeBudget 3 29 = radixRepresentativeBudgetPrimeEnvelope 3 29 ↔ lastRadixBlockQuotient 3 29 = 0 ∨ lastRadixBlockRemainder 3 29 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 29 ≤ 29 * 29 := by native_decide

/-- representative_p3_B37 -/
example : radixRepresentativeBudget 3 37 + radixRepresentativeBudgetPrimeEnvelopeGap 3 37 = radixRepresentativeBudgetPrimeEnvelope 3 37 ∧ radixRepresentativeBudget 3 37 ≤ radixRepresentativeBudgetPrimeEnvelope 3 37 ∧ (radixRepresentativeBudget 3 37 = radixRepresentativeBudgetPrimeEnvelope 3 37 ↔ lastRadixBlockQuotient 3 37 = 0 ∨ lastRadixBlockRemainder 3 37 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 37 ≤ 37 * 37 := by native_decide

/-- representative_p3_B45 -/
example : radixRepresentativeBudget 3 45 + radixRepresentativeBudgetPrimeEnvelopeGap 3 45 = radixRepresentativeBudgetPrimeEnvelope 3 45 ∧ radixRepresentativeBudget 3 45 ≤ radixRepresentativeBudgetPrimeEnvelope 3 45 ∧ (radixRepresentativeBudget 3 45 = radixRepresentativeBudgetPrimeEnvelope 3 45 ↔ lastRadixBlockQuotient 3 45 = 0 ∨ lastRadixBlockRemainder 3 45 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 45 ≤ 45 * 45 := by native_decide

/-- representative_p4_B3 -/
example : radixRepresentativeBudget 4 3 + radixRepresentativeBudgetPrimeEnvelopeGap 4 3 = radixRepresentativeBudgetPrimeEnvelope 4 3 ∧ radixRepresentativeBudget 4 3 ≤ radixRepresentativeBudgetPrimeEnvelope 4 3 ∧ (radixRepresentativeBudget 4 3 = radixRepresentativeBudgetPrimeEnvelope 4 3 ↔ lastRadixBlockQuotient 4 3 = 0 ∨ lastRadixBlockRemainder 4 3 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 3 ≤ 3 * 3 := by native_decide

/-- representative_p4_B11 -/
example : radixRepresentativeBudget 4 11 + radixRepresentativeBudgetPrimeEnvelopeGap 4 11 = radixRepresentativeBudgetPrimeEnvelope 4 11 ∧ radixRepresentativeBudget 4 11 ≤ radixRepresentativeBudgetPrimeEnvelope 4 11 ∧ (radixRepresentativeBudget 4 11 = radixRepresentativeBudgetPrimeEnvelope 4 11 ↔ lastRadixBlockQuotient 4 11 = 0 ∨ lastRadixBlockRemainder 4 11 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 11 ≤ 11 * 11 := by native_decide

/-- representative_p4_B19 -/
example : radixRepresentativeBudget 4 19 + radixRepresentativeBudgetPrimeEnvelopeGap 4 19 = radixRepresentativeBudgetPrimeEnvelope 4 19 ∧ radixRepresentativeBudget 4 19 ≤ radixRepresentativeBudgetPrimeEnvelope 4 19 ∧ (radixRepresentativeBudget 4 19 = radixRepresentativeBudgetPrimeEnvelope 4 19 ↔ lastRadixBlockQuotient 4 19 = 0 ∨ lastRadixBlockRemainder 4 19 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 19 ≤ 19 * 19 := by native_decide

/-- representative_p4_B27 -/
example : radixRepresentativeBudget 4 27 + radixRepresentativeBudgetPrimeEnvelopeGap 4 27 = radixRepresentativeBudgetPrimeEnvelope 4 27 ∧ radixRepresentativeBudget 4 27 ≤ radixRepresentativeBudgetPrimeEnvelope 4 27 ∧ (radixRepresentativeBudget 4 27 = radixRepresentativeBudgetPrimeEnvelope 4 27 ↔ lastRadixBlockQuotient 4 27 = 0 ∨ lastRadixBlockRemainder 4 27 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 27 ≤ 27 * 27 := by native_decide

/-- representative_p4_B35 -/
example : radixRepresentativeBudget 4 35 + radixRepresentativeBudgetPrimeEnvelopeGap 4 35 = radixRepresentativeBudgetPrimeEnvelope 4 35 ∧ radixRepresentativeBudget 4 35 ≤ radixRepresentativeBudgetPrimeEnvelope 4 35 ∧ (radixRepresentativeBudget 4 35 = radixRepresentativeBudgetPrimeEnvelope 4 35 ↔ lastRadixBlockQuotient 4 35 = 0 ∨ lastRadixBlockRemainder 4 35 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 35 ≤ 35 * 35 := by native_decide

/-- representative_p4_B43 -/
example : radixRepresentativeBudget 4 43 + radixRepresentativeBudgetPrimeEnvelopeGap 4 43 = radixRepresentativeBudgetPrimeEnvelope 4 43 ∧ radixRepresentativeBudget 4 43 ≤ radixRepresentativeBudgetPrimeEnvelope 4 43 ∧ (radixRepresentativeBudget 4 43 = radixRepresentativeBudgetPrimeEnvelope 4 43 ↔ lastRadixBlockQuotient 4 43 = 0 ∨ lastRadixBlockRemainder 4 43 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 43 ≤ 43 * 43 := by native_decide

/-- representative_p5_B1 -/
example : radixRepresentativeBudget 5 1 + radixRepresentativeBudgetPrimeEnvelopeGap 5 1 = radixRepresentativeBudgetPrimeEnvelope 5 1 ∧ radixRepresentativeBudget 5 1 ≤ radixRepresentativeBudgetPrimeEnvelope 5 1 ∧ (radixRepresentativeBudget 5 1 = radixRepresentativeBudgetPrimeEnvelope 5 1 ↔ lastRadixBlockQuotient 5 1 = 0 ∨ lastRadixBlockRemainder 5 1 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 1 ≤ 1 * 1 := by native_decide

/-- representative_p5_B9 -/
example : radixRepresentativeBudget 5 9 + radixRepresentativeBudgetPrimeEnvelopeGap 5 9 = radixRepresentativeBudgetPrimeEnvelope 5 9 ∧ radixRepresentativeBudget 5 9 ≤ radixRepresentativeBudgetPrimeEnvelope 5 9 ∧ (radixRepresentativeBudget 5 9 = radixRepresentativeBudgetPrimeEnvelope 5 9 ↔ lastRadixBlockQuotient 5 9 = 0 ∨ lastRadixBlockRemainder 5 9 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 9 ≤ 9 * 9 := by native_decide

/-- representative_p5_B17 -/
example : radixRepresentativeBudget 5 17 + radixRepresentativeBudgetPrimeEnvelopeGap 5 17 = radixRepresentativeBudgetPrimeEnvelope 5 17 ∧ radixRepresentativeBudget 5 17 ≤ radixRepresentativeBudgetPrimeEnvelope 5 17 ∧ (radixRepresentativeBudget 5 17 = radixRepresentativeBudgetPrimeEnvelope 5 17 ↔ lastRadixBlockQuotient 5 17 = 0 ∨ lastRadixBlockRemainder 5 17 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 17 ≤ 17 * 17 := by native_decide

/-- representative_p5_B25 -/
example : radixRepresentativeBudget 5 25 + radixRepresentativeBudgetPrimeEnvelopeGap 5 25 = radixRepresentativeBudgetPrimeEnvelope 5 25 ∧ radixRepresentativeBudget 5 25 ≤ radixRepresentativeBudgetPrimeEnvelope 5 25 ∧ (radixRepresentativeBudget 5 25 = radixRepresentativeBudgetPrimeEnvelope 5 25 ↔ lastRadixBlockQuotient 5 25 = 0 ∨ lastRadixBlockRemainder 5 25 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 25 ≤ 25 * 25 := by native_decide

/-- representative_p5_B33 -/
example : radixRepresentativeBudget 5 33 + radixRepresentativeBudgetPrimeEnvelopeGap 5 33 = radixRepresentativeBudgetPrimeEnvelope 5 33 ∧ radixRepresentativeBudget 5 33 ≤ radixRepresentativeBudgetPrimeEnvelope 5 33 ∧ (radixRepresentativeBudget 5 33 = radixRepresentativeBudgetPrimeEnvelope 5 33 ↔ lastRadixBlockQuotient 5 33 = 0 ∨ lastRadixBlockRemainder 5 33 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 33 ≤ 33 * 33 := by native_decide

/-- representative_p5_B41 -/
example : radixRepresentativeBudget 5 41 + radixRepresentativeBudgetPrimeEnvelopeGap 5 41 = radixRepresentativeBudgetPrimeEnvelope 5 41 ∧ radixRepresentativeBudget 5 41 ≤ radixRepresentativeBudgetPrimeEnvelope 5 41 ∧ (radixRepresentativeBudget 5 41 = radixRepresentativeBudgetPrimeEnvelope 5 41 ↔ lastRadixBlockQuotient 5 41 = 0 ∨ lastRadixBlockRemainder 5 41 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 41 ≤ 41 * 41 := by native_decide

/-- representative_p5_B49 -/
example : radixRepresentativeBudget 5 49 + radixRepresentativeBudgetPrimeEnvelopeGap 5 49 = radixRepresentativeBudgetPrimeEnvelope 5 49 ∧ radixRepresentativeBudget 5 49 ≤ radixRepresentativeBudgetPrimeEnvelope 5 49 ∧ (radixRepresentativeBudget 5 49 = radixRepresentativeBudgetPrimeEnvelope 5 49 ↔ lastRadixBlockQuotient 5 49 = 0 ∨ lastRadixBlockRemainder 5 49 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 49 ≤ 49 * 49 := by native_decide

/-- representative_p6_B7 -/
example : radixRepresentativeBudget 6 7 + radixRepresentativeBudgetPrimeEnvelopeGap 6 7 = radixRepresentativeBudgetPrimeEnvelope 6 7 ∧ radixRepresentativeBudget 6 7 ≤ radixRepresentativeBudgetPrimeEnvelope 6 7 ∧ (radixRepresentativeBudget 6 7 = radixRepresentativeBudgetPrimeEnvelope 6 7 ↔ lastRadixBlockQuotient 6 7 = 0 ∨ lastRadixBlockRemainder 6 7 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 7 ≤ 7 * 7 := by native_decide

/-- representative_p6_B15 -/
example : radixRepresentativeBudget 6 15 + radixRepresentativeBudgetPrimeEnvelopeGap 6 15 = radixRepresentativeBudgetPrimeEnvelope 6 15 ∧ radixRepresentativeBudget 6 15 ≤ radixRepresentativeBudgetPrimeEnvelope 6 15 ∧ (radixRepresentativeBudget 6 15 = radixRepresentativeBudgetPrimeEnvelope 6 15 ↔ lastRadixBlockQuotient 6 15 = 0 ∨ lastRadixBlockRemainder 6 15 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 15 ≤ 15 * 15 := by native_decide

/-- representative_p6_B23 -/
example : radixRepresentativeBudget 6 23 + radixRepresentativeBudgetPrimeEnvelopeGap 6 23 = radixRepresentativeBudgetPrimeEnvelope 6 23 ∧ radixRepresentativeBudget 6 23 ≤ radixRepresentativeBudgetPrimeEnvelope 6 23 ∧ (radixRepresentativeBudget 6 23 = radixRepresentativeBudgetPrimeEnvelope 6 23 ↔ lastRadixBlockQuotient 6 23 = 0 ∨ lastRadixBlockRemainder 6 23 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 23 ≤ 23 * 23 := by native_decide

/-- representative_p6_B31 -/
example : radixRepresentativeBudget 6 31 + radixRepresentativeBudgetPrimeEnvelopeGap 6 31 = radixRepresentativeBudgetPrimeEnvelope 6 31 ∧ radixRepresentativeBudget 6 31 ≤ radixRepresentativeBudgetPrimeEnvelope 6 31 ∧ (radixRepresentativeBudget 6 31 = radixRepresentativeBudgetPrimeEnvelope 6 31 ↔ lastRadixBlockQuotient 6 31 = 0 ∨ lastRadixBlockRemainder 6 31 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 31 ≤ 31 * 31 := by native_decide

/-- representative_p6_B39 -/
example : radixRepresentativeBudget 6 39 + radixRepresentativeBudgetPrimeEnvelopeGap 6 39 = radixRepresentativeBudgetPrimeEnvelope 6 39 ∧ radixRepresentativeBudget 6 39 ≤ radixRepresentativeBudgetPrimeEnvelope 6 39 ∧ (radixRepresentativeBudget 6 39 = radixRepresentativeBudgetPrimeEnvelope 6 39 ↔ lastRadixBlockQuotient 6 39 = 0 ∨ lastRadixBlockRemainder 6 39 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 39 ≤ 39 * 39 := by native_decide

/-- representative_p6_B47 -/
example : radixRepresentativeBudget 6 47 + radixRepresentativeBudgetPrimeEnvelopeGap 6 47 = radixRepresentativeBudgetPrimeEnvelope 6 47 ∧ radixRepresentativeBudget 6 47 ≤ radixRepresentativeBudgetPrimeEnvelope 6 47 ∧ (radixRepresentativeBudget 6 47 = radixRepresentativeBudgetPrimeEnvelope 6 47 ↔ lastRadixBlockQuotient 6 47 = 0 ∨ lastRadixBlockRemainder 6 47 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 47 ≤ 47 * 47 := by native_decide

/-- representative_p7_B5 -/
example : radixRepresentativeBudget 7 5 + radixRepresentativeBudgetPrimeEnvelopeGap 7 5 = radixRepresentativeBudgetPrimeEnvelope 7 5 ∧ radixRepresentativeBudget 7 5 ≤ radixRepresentativeBudgetPrimeEnvelope 7 5 ∧ (radixRepresentativeBudget 7 5 = radixRepresentativeBudgetPrimeEnvelope 7 5 ↔ lastRadixBlockQuotient 7 5 = 0 ∨ lastRadixBlockRemainder 7 5 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 5 ≤ 5 * 5 := by native_decide

/-- representative_p7_B13 -/
example : radixRepresentativeBudget 7 13 + radixRepresentativeBudgetPrimeEnvelopeGap 7 13 = radixRepresentativeBudgetPrimeEnvelope 7 13 ∧ radixRepresentativeBudget 7 13 ≤ radixRepresentativeBudgetPrimeEnvelope 7 13 ∧ (radixRepresentativeBudget 7 13 = radixRepresentativeBudgetPrimeEnvelope 7 13 ↔ lastRadixBlockQuotient 7 13 = 0 ∨ lastRadixBlockRemainder 7 13 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 13 ≤ 13 * 13 := by native_decide

/-- representative_p7_B21 -/
example : radixRepresentativeBudget 7 21 + radixRepresentativeBudgetPrimeEnvelopeGap 7 21 = radixRepresentativeBudgetPrimeEnvelope 7 21 ∧ radixRepresentativeBudget 7 21 ≤ radixRepresentativeBudgetPrimeEnvelope 7 21 ∧ (radixRepresentativeBudget 7 21 = radixRepresentativeBudgetPrimeEnvelope 7 21 ↔ lastRadixBlockQuotient 7 21 = 0 ∨ lastRadixBlockRemainder 7 21 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 21 ≤ 21 * 21 := by native_decide

/-- representative_p7_B29 -/
example : radixRepresentativeBudget 7 29 + radixRepresentativeBudgetPrimeEnvelopeGap 7 29 = radixRepresentativeBudgetPrimeEnvelope 7 29 ∧ radixRepresentativeBudget 7 29 ≤ radixRepresentativeBudgetPrimeEnvelope 7 29 ∧ (radixRepresentativeBudget 7 29 = radixRepresentativeBudgetPrimeEnvelope 7 29 ↔ lastRadixBlockQuotient 7 29 = 0 ∨ lastRadixBlockRemainder 7 29 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 29 ≤ 29 * 29 := by native_decide

/-- representative_p7_B37 -/
example : radixRepresentativeBudget 7 37 + radixRepresentativeBudgetPrimeEnvelopeGap 7 37 = radixRepresentativeBudgetPrimeEnvelope 7 37 ∧ radixRepresentativeBudget 7 37 ≤ radixRepresentativeBudgetPrimeEnvelope 7 37 ∧ (radixRepresentativeBudget 7 37 = radixRepresentativeBudgetPrimeEnvelope 7 37 ↔ lastRadixBlockQuotient 7 37 = 0 ∨ lastRadixBlockRemainder 7 37 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 37 ≤ 37 * 37 := by native_decide

/-- representative_p7_B45 -/
example : radixRepresentativeBudget 7 45 + radixRepresentativeBudgetPrimeEnvelopeGap 7 45 = radixRepresentativeBudgetPrimeEnvelope 7 45 ∧ radixRepresentativeBudget 7 45 ≤ radixRepresentativeBudgetPrimeEnvelope 7 45 ∧ (radixRepresentativeBudget 7 45 = radixRepresentativeBudgetPrimeEnvelope 7 45 ↔ lastRadixBlockQuotient 7 45 = 0 ∨ lastRadixBlockRemainder 7 45 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 45 ≤ 45 * 45 := by native_decide

/-- representative_p8_B3 -/
example : radixRepresentativeBudget 8 3 + radixRepresentativeBudgetPrimeEnvelopeGap 8 3 = radixRepresentativeBudgetPrimeEnvelope 8 3 ∧ radixRepresentativeBudget 8 3 ≤ radixRepresentativeBudgetPrimeEnvelope 8 3 ∧ (radixRepresentativeBudget 8 3 = radixRepresentativeBudgetPrimeEnvelope 8 3 ↔ lastRadixBlockQuotient 8 3 = 0 ∨ lastRadixBlockRemainder 8 3 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 3 ≤ 3 * 3 := by native_decide

/-- representative_p8_B11 -/
example : radixRepresentativeBudget 8 11 + radixRepresentativeBudgetPrimeEnvelopeGap 8 11 = radixRepresentativeBudgetPrimeEnvelope 8 11 ∧ radixRepresentativeBudget 8 11 ≤ radixRepresentativeBudgetPrimeEnvelope 8 11 ∧ (radixRepresentativeBudget 8 11 = radixRepresentativeBudgetPrimeEnvelope 8 11 ↔ lastRadixBlockQuotient 8 11 = 0 ∨ lastRadixBlockRemainder 8 11 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 11 ≤ 11 * 11 := by native_decide

/-- representative_p8_B19 -/
example : radixRepresentativeBudget 8 19 + radixRepresentativeBudgetPrimeEnvelopeGap 8 19 = radixRepresentativeBudgetPrimeEnvelope 8 19 ∧ radixRepresentativeBudget 8 19 ≤ radixRepresentativeBudgetPrimeEnvelope 8 19 ∧ (radixRepresentativeBudget 8 19 = radixRepresentativeBudgetPrimeEnvelope 8 19 ↔ lastRadixBlockQuotient 8 19 = 0 ∨ lastRadixBlockRemainder 8 19 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 19 ≤ 19 * 19 := by native_decide

/-- representative_p8_B27 -/
example : radixRepresentativeBudget 8 27 + radixRepresentativeBudgetPrimeEnvelopeGap 8 27 = radixRepresentativeBudgetPrimeEnvelope 8 27 ∧ radixRepresentativeBudget 8 27 ≤ radixRepresentativeBudgetPrimeEnvelope 8 27 ∧ (radixRepresentativeBudget 8 27 = radixRepresentativeBudgetPrimeEnvelope 8 27 ↔ lastRadixBlockQuotient 8 27 = 0 ∨ lastRadixBlockRemainder 8 27 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 27 ≤ 27 * 27 := by native_decide

/-- representative_p8_B35 -/
example : radixRepresentativeBudget 8 35 + radixRepresentativeBudgetPrimeEnvelopeGap 8 35 = radixRepresentativeBudgetPrimeEnvelope 8 35 ∧ radixRepresentativeBudget 8 35 ≤ radixRepresentativeBudgetPrimeEnvelope 8 35 ∧ (radixRepresentativeBudget 8 35 = radixRepresentativeBudgetPrimeEnvelope 8 35 ↔ lastRadixBlockQuotient 8 35 = 0 ∨ lastRadixBlockRemainder 8 35 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 35 ≤ 35 * 35 := by native_decide

/-- representative_p8_B43 -/
example : radixRepresentativeBudget 8 43 + radixRepresentativeBudgetPrimeEnvelopeGap 8 43 = radixRepresentativeBudgetPrimeEnvelope 8 43 ∧ radixRepresentativeBudget 8 43 ≤ radixRepresentativeBudgetPrimeEnvelope 8 43 ∧ (radixRepresentativeBudget 8 43 = radixRepresentativeBudgetPrimeEnvelope 8 43 ↔ lastRadixBlockQuotient 8 43 = 0 ∨ lastRadixBlockRemainder 8 43 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 43 ≤ 43 * 43 := by native_decide

/-- representative_p9_B1 -/
example : radixRepresentativeBudget 9 1 + radixRepresentativeBudgetPrimeEnvelopeGap 9 1 = radixRepresentativeBudgetPrimeEnvelope 9 1 ∧ radixRepresentativeBudget 9 1 ≤ radixRepresentativeBudgetPrimeEnvelope 9 1 ∧ (radixRepresentativeBudget 9 1 = radixRepresentativeBudgetPrimeEnvelope 9 1 ↔ lastRadixBlockQuotient 9 1 = 0 ∨ lastRadixBlockRemainder 9 1 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 1 ≤ 1 * 1 := by native_decide

/-- representative_p9_B9 -/
example : radixRepresentativeBudget 9 9 + radixRepresentativeBudgetPrimeEnvelopeGap 9 9 = radixRepresentativeBudgetPrimeEnvelope 9 9 ∧ radixRepresentativeBudget 9 9 ≤ radixRepresentativeBudgetPrimeEnvelope 9 9 ∧ (radixRepresentativeBudget 9 9 = radixRepresentativeBudgetPrimeEnvelope 9 9 ↔ lastRadixBlockQuotient 9 9 = 0 ∨ lastRadixBlockRemainder 9 9 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 9 ≤ 9 * 9 := by native_decide

/-- representative_p9_B17 -/
example : radixRepresentativeBudget 9 17 + radixRepresentativeBudgetPrimeEnvelopeGap 9 17 = radixRepresentativeBudgetPrimeEnvelope 9 17 ∧ radixRepresentativeBudget 9 17 ≤ radixRepresentativeBudgetPrimeEnvelope 9 17 ∧ (radixRepresentativeBudget 9 17 = radixRepresentativeBudgetPrimeEnvelope 9 17 ↔ lastRadixBlockQuotient 9 17 = 0 ∨ lastRadixBlockRemainder 9 17 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 17 ≤ 17 * 17 := by native_decide

/-- representative_p9_B25 -/
example : radixRepresentativeBudget 9 25 + radixRepresentativeBudgetPrimeEnvelopeGap 9 25 = radixRepresentativeBudgetPrimeEnvelope 9 25 ∧ radixRepresentativeBudget 9 25 ≤ radixRepresentativeBudgetPrimeEnvelope 9 25 ∧ (radixRepresentativeBudget 9 25 = radixRepresentativeBudgetPrimeEnvelope 9 25 ↔ lastRadixBlockQuotient 9 25 = 0 ∨ lastRadixBlockRemainder 9 25 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 25 ≤ 25 * 25 := by native_decide

/-- representative_p9_B33 -/
example : radixRepresentativeBudget 9 33 + radixRepresentativeBudgetPrimeEnvelopeGap 9 33 = radixRepresentativeBudgetPrimeEnvelope 9 33 ∧ radixRepresentativeBudget 9 33 ≤ radixRepresentativeBudgetPrimeEnvelope 9 33 ∧ (radixRepresentativeBudget 9 33 = radixRepresentativeBudgetPrimeEnvelope 9 33 ↔ lastRadixBlockQuotient 9 33 = 0 ∨ lastRadixBlockRemainder 9 33 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 33 ≤ 33 * 33 := by native_decide

/-- representative_p9_B41 -/
example : radixRepresentativeBudget 9 41 + radixRepresentativeBudgetPrimeEnvelopeGap 9 41 = radixRepresentativeBudgetPrimeEnvelope 9 41 ∧ radixRepresentativeBudget 9 41 ≤ radixRepresentativeBudgetPrimeEnvelope 9 41 ∧ (radixRepresentativeBudget 9 41 = radixRepresentativeBudgetPrimeEnvelope 9 41 ↔ lastRadixBlockQuotient 9 41 = 0 ∨ lastRadixBlockRemainder 9 41 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 41 ≤ 41 * 41 := by native_decide

/-- representative_p9_B49 -/
example : radixRepresentativeBudget 9 49 + radixRepresentativeBudgetPrimeEnvelopeGap 9 49 = radixRepresentativeBudgetPrimeEnvelope 9 49 ∧ radixRepresentativeBudget 9 49 ≤ radixRepresentativeBudgetPrimeEnvelope 9 49 ∧ (radixRepresentativeBudget 9 49 = radixRepresentativeBudgetPrimeEnvelope 9 49 ↔ lastRadixBlockQuotient 9 49 = 0 ∨ lastRadixBlockRemainder 9 49 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 49 ≤ 49 * 49 := by native_decide

/-- representative_p10_B7 -/
example : radixRepresentativeBudget 10 7 + radixRepresentativeBudgetPrimeEnvelopeGap 10 7 = radixRepresentativeBudgetPrimeEnvelope 10 7 ∧ radixRepresentativeBudget 10 7 ≤ radixRepresentativeBudgetPrimeEnvelope 10 7 ∧ (radixRepresentativeBudget 10 7 = radixRepresentativeBudgetPrimeEnvelope 10 7 ↔ lastRadixBlockQuotient 10 7 = 0 ∨ lastRadixBlockRemainder 10 7 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 7 ≤ 7 * 7 := by native_decide

/-- representative_p10_B15 -/
example : radixRepresentativeBudget 10 15 + radixRepresentativeBudgetPrimeEnvelopeGap 10 15 = radixRepresentativeBudgetPrimeEnvelope 10 15 ∧ radixRepresentativeBudget 10 15 ≤ radixRepresentativeBudgetPrimeEnvelope 10 15 ∧ (radixRepresentativeBudget 10 15 = radixRepresentativeBudgetPrimeEnvelope 10 15 ↔ lastRadixBlockQuotient 10 15 = 0 ∨ lastRadixBlockRemainder 10 15 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 15 ≤ 15 * 15 := by native_decide

/-- representative_p10_B23 -/
example : radixRepresentativeBudget 10 23 + radixRepresentativeBudgetPrimeEnvelopeGap 10 23 = radixRepresentativeBudgetPrimeEnvelope 10 23 ∧ radixRepresentativeBudget 10 23 ≤ radixRepresentativeBudgetPrimeEnvelope 10 23 ∧ (radixRepresentativeBudget 10 23 = radixRepresentativeBudgetPrimeEnvelope 10 23 ↔ lastRadixBlockQuotient 10 23 = 0 ∨ lastRadixBlockRemainder 10 23 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 23 ≤ 23 * 23 := by native_decide

/-- representative_p10_B31 -/
example : radixRepresentativeBudget 10 31 + radixRepresentativeBudgetPrimeEnvelopeGap 10 31 = radixRepresentativeBudgetPrimeEnvelope 10 31 ∧ radixRepresentativeBudget 10 31 ≤ radixRepresentativeBudgetPrimeEnvelope 10 31 ∧ (radixRepresentativeBudget 10 31 = radixRepresentativeBudgetPrimeEnvelope 10 31 ↔ lastRadixBlockQuotient 10 31 = 0 ∨ lastRadixBlockRemainder 10 31 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 31 ≤ 31 * 31 := by native_decide

/-- representative_p10_B39 -/
example : radixRepresentativeBudget 10 39 + radixRepresentativeBudgetPrimeEnvelopeGap 10 39 = radixRepresentativeBudgetPrimeEnvelope 10 39 ∧ radixRepresentativeBudget 10 39 ≤ radixRepresentativeBudgetPrimeEnvelope 10 39 ∧ (radixRepresentativeBudget 10 39 = radixRepresentativeBudgetPrimeEnvelope 10 39 ↔ lastRadixBlockQuotient 10 39 = 0 ∨ lastRadixBlockRemainder 10 39 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 39 ≤ 39 * 39 := by native_decide

/-- representative_p10_B47 -/
example : radixRepresentativeBudget 10 47 + radixRepresentativeBudgetPrimeEnvelopeGap 10 47 = radixRepresentativeBudgetPrimeEnvelope 10 47 ∧ radixRepresentativeBudget 10 47 ≤ radixRepresentativeBudgetPrimeEnvelope 10 47 ∧ (radixRepresentativeBudget 10 47 = radixRepresentativeBudgetPrimeEnvelope 10 47 ↔ lastRadixBlockQuotient 10 47 = 0 ∨ lastRadixBlockRemainder 10 47 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 47 ≤ 47 * 47 := by native_decide

/-- representative_p11_B5 -/
example : radixRepresentativeBudget 11 5 + radixRepresentativeBudgetPrimeEnvelopeGap 11 5 = radixRepresentativeBudgetPrimeEnvelope 11 5 ∧ radixRepresentativeBudget 11 5 ≤ radixRepresentativeBudgetPrimeEnvelope 11 5 ∧ (radixRepresentativeBudget 11 5 = radixRepresentativeBudgetPrimeEnvelope 11 5 ↔ lastRadixBlockQuotient 11 5 = 0 ∨ lastRadixBlockRemainder 11 5 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 5 ≤ 5 * 5 := by native_decide

/-- representative_p11_B13 -/
example : radixRepresentativeBudget 11 13 + radixRepresentativeBudgetPrimeEnvelopeGap 11 13 = radixRepresentativeBudgetPrimeEnvelope 11 13 ∧ radixRepresentativeBudget 11 13 ≤ radixRepresentativeBudgetPrimeEnvelope 11 13 ∧ (radixRepresentativeBudget 11 13 = radixRepresentativeBudgetPrimeEnvelope 11 13 ↔ lastRadixBlockQuotient 11 13 = 0 ∨ lastRadixBlockRemainder 11 13 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 13 ≤ 13 * 13 := by native_decide

/-- representative_p11_B21 -/
example : radixRepresentativeBudget 11 21 + radixRepresentativeBudgetPrimeEnvelopeGap 11 21 = radixRepresentativeBudgetPrimeEnvelope 11 21 ∧ radixRepresentativeBudget 11 21 ≤ radixRepresentativeBudgetPrimeEnvelope 11 21 ∧ (radixRepresentativeBudget 11 21 = radixRepresentativeBudgetPrimeEnvelope 11 21 ↔ lastRadixBlockQuotient 11 21 = 0 ∨ lastRadixBlockRemainder 11 21 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 21 ≤ 21 * 21 := by native_decide

/-- representative_p11_B29 -/
example : radixRepresentativeBudget 11 29 + radixRepresentativeBudgetPrimeEnvelopeGap 11 29 = radixRepresentativeBudgetPrimeEnvelope 11 29 ∧ radixRepresentativeBudget 11 29 ≤ radixRepresentativeBudgetPrimeEnvelope 11 29 ∧ (radixRepresentativeBudget 11 29 = radixRepresentativeBudgetPrimeEnvelope 11 29 ↔ lastRadixBlockQuotient 11 29 = 0 ∨ lastRadixBlockRemainder 11 29 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 29 ≤ 29 * 29 := by native_decide

/-- representative_p11_B37 -/
example : radixRepresentativeBudget 11 37 + radixRepresentativeBudgetPrimeEnvelopeGap 11 37 = radixRepresentativeBudgetPrimeEnvelope 11 37 ∧ radixRepresentativeBudget 11 37 ≤ radixRepresentativeBudgetPrimeEnvelope 11 37 ∧ (radixRepresentativeBudget 11 37 = radixRepresentativeBudgetPrimeEnvelope 11 37 ↔ lastRadixBlockQuotient 11 37 = 0 ∨ lastRadixBlockRemainder 11 37 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 37 ≤ 37 * 37 := by native_decide

/-- representative_p11_B45 -/
example : radixRepresentativeBudget 11 45 + radixRepresentativeBudgetPrimeEnvelopeGap 11 45 = radixRepresentativeBudgetPrimeEnvelope 11 45 ∧ radixRepresentativeBudget 11 45 ≤ radixRepresentativeBudgetPrimeEnvelope 11 45 ∧ (radixRepresentativeBudget 11 45 = radixRepresentativeBudgetPrimeEnvelope 11 45 ↔ lastRadixBlockQuotient 11 45 = 0 ∨ lastRadixBlockRemainder 11 45 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 45 ≤ 45 * 45 := by native_decide

/-- representative_p12_B3 -/
example : radixRepresentativeBudget 12 3 + radixRepresentativeBudgetPrimeEnvelopeGap 12 3 = radixRepresentativeBudgetPrimeEnvelope 12 3 ∧ radixRepresentativeBudget 12 3 ≤ radixRepresentativeBudgetPrimeEnvelope 12 3 ∧ (radixRepresentativeBudget 12 3 = radixRepresentativeBudgetPrimeEnvelope 12 3 ↔ lastRadixBlockQuotient 12 3 = 0 ∨ lastRadixBlockRemainder 12 3 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 3 ≤ 3 * 3 := by native_decide

/-- representative_p12_B11 -/
example : radixRepresentativeBudget 12 11 + radixRepresentativeBudgetPrimeEnvelopeGap 12 11 = radixRepresentativeBudgetPrimeEnvelope 12 11 ∧ radixRepresentativeBudget 12 11 ≤ radixRepresentativeBudgetPrimeEnvelope 12 11 ∧ (radixRepresentativeBudget 12 11 = radixRepresentativeBudgetPrimeEnvelope 12 11 ↔ lastRadixBlockQuotient 12 11 = 0 ∨ lastRadixBlockRemainder 12 11 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 11 ≤ 11 * 11 := by native_decide

/-- representative_p12_B19 -/
example : radixRepresentativeBudget 12 19 + radixRepresentativeBudgetPrimeEnvelopeGap 12 19 = radixRepresentativeBudgetPrimeEnvelope 12 19 ∧ radixRepresentativeBudget 12 19 ≤ radixRepresentativeBudgetPrimeEnvelope 12 19 ∧ (radixRepresentativeBudget 12 19 = radixRepresentativeBudgetPrimeEnvelope 12 19 ↔ lastRadixBlockQuotient 12 19 = 0 ∨ lastRadixBlockRemainder 12 19 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 19 ≤ 19 * 19 := by native_decide

/-- representative_p12_B27 -/
example : radixRepresentativeBudget 12 27 + radixRepresentativeBudgetPrimeEnvelopeGap 12 27 = radixRepresentativeBudgetPrimeEnvelope 12 27 ∧ radixRepresentativeBudget 12 27 ≤ radixRepresentativeBudgetPrimeEnvelope 12 27 ∧ (radixRepresentativeBudget 12 27 = radixRepresentativeBudgetPrimeEnvelope 12 27 ↔ lastRadixBlockQuotient 12 27 = 0 ∨ lastRadixBlockRemainder 12 27 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 27 ≤ 27 * 27 := by native_decide

/-- representative_p12_B35 -/
example : radixRepresentativeBudget 12 35 + radixRepresentativeBudgetPrimeEnvelopeGap 12 35 = radixRepresentativeBudgetPrimeEnvelope 12 35 ∧ radixRepresentativeBudget 12 35 ≤ radixRepresentativeBudgetPrimeEnvelope 12 35 ∧ (radixRepresentativeBudget 12 35 = radixRepresentativeBudgetPrimeEnvelope 12 35 ↔ lastRadixBlockQuotient 12 35 = 0 ∨ lastRadixBlockRemainder 12 35 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 35 ≤ 35 * 35 := by native_decide

/-- representative_p12_B43 -/
example : radixRepresentativeBudget 12 43 + radixRepresentativeBudgetPrimeEnvelopeGap 12 43 = radixRepresentativeBudgetPrimeEnvelope 12 43 ∧ radixRepresentativeBudget 12 43 ≤ radixRepresentativeBudgetPrimeEnvelope 12 43 ∧ (radixRepresentativeBudget 12 43 = radixRepresentativeBudgetPrimeEnvelope 12 43 ↔ lastRadixBlockQuotient 12 43 = 0 ∨ lastRadixBlockRemainder 12 43 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 43 ≤ 43 * 43 := by native_decide

/-- zero_base_B1 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 1 ≤ 1 * 1 := by native_decide

/-- zero_base_B9 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 9 ≤ 9 * 9 := by native_decide

/-- zero_base_B17 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 17 ≤ 17 * 17 := by native_decide

/-- zero_base_B25 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 25 ≤ 25 * 25 := by native_decide

/-- zero_base_B33 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 33 ≤ 33 * 33 := by native_decide

/-- zero_base_B41 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 41 ≤ 41 * 41 := by native_decide

/-- zero_base_B49 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 49 ≤ 49 * 49 := by native_decide

/-- zero_base_B57 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 57 ≤ 57 * 57 := by native_decide

/-- zero_base_B65 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 65 ≤ 65 * 65 := by native_decide

/-- zero_base_B73 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 73 ≤ 73 * 73 := by native_decide

/-- zero_base_B81 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 81 ≤ 81 * 81 := by native_decide

/-- zero_base_B89 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 89 ≤ 89 * 89 := by native_decide

/-- zero_base_B97 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 97 ≤ 97 * 97 := by native_decide

/-- zero_base_B105 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 105 ≤ 105 * 105 := by native_decide

/-- zero_base_B113 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 113 ≤ 113 * 113 := by native_decide

/-- zero_base_B121 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 121 ≤ 121 * 121 := by native_decide

/-- zero_base_B129 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 129 ≤ 129 * 129 := by native_decide

/-- zero_base_B137 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 137 ≤ 137 * 137 := by native_decide

/-- zero_base_B145 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 145 ≤ 145 * 145 := by native_decide

/-- zero_base_B153 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 153 ≤ 153 * 153 := by native_decide

/-- zero_base_B161 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 161 ≤ 161 * 161 := by native_decide

/-- zero_base_B169 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 169 ≤ 169 * 169 := by native_decide

/-- zero_base_B177 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 177 ≤ 177 * 177 := by native_decide

/-- zero_base_B185 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 185 ≤ 185 * 185 := by native_decide

/-- zero_base_B193 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 193 ≤ 193 * 193 := by native_decide

/-- compiler_p2_r1_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 1 1 + maximumLayerCompilerPrimeEnvelopeGap 2 1 1 = maximumLayerCompilerPrimeEnvelopeBound 2 1 1 ∧ maximumLayerCompilerTotalTests 2 1 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 1 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 1 1 ≤ maximumLayerCompilerTestBound 2 1 1 := by native_decide

/-- compiler_p2_r4_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 4 0 + maximumLayerCompilerPrimeEnvelopeGap 2 4 0 = maximumLayerCompilerPrimeEnvelopeBound 2 4 0 ∧ maximumLayerCompilerTotalTests 2 4 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 4 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 4 0 ≤ maximumLayerCompilerTestBound 2 4 0 := by native_decide

/-- compiler_p2_r6_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 6 2 + maximumLayerCompilerPrimeEnvelopeGap 2 6 2 = maximumLayerCompilerPrimeEnvelopeBound 2 6 2 ∧ maximumLayerCompilerTotalTests 2 6 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 6 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 6 2 ≤ maximumLayerCompilerTestBound 2 6 2 := by native_decide

/-- compiler_p2_r9_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 9 1 + maximumLayerCompilerPrimeEnvelopeGap 2 9 1 = maximumLayerCompilerPrimeEnvelopeBound 2 9 1 ∧ maximumLayerCompilerTotalTests 2 9 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 9 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 9 1 ≤ maximumLayerCompilerTestBound 2 9 1 := by native_decide

/-- compiler_p2_r12_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 12 0 + maximumLayerCompilerPrimeEnvelopeGap 2 12 0 = maximumLayerCompilerPrimeEnvelopeBound 2 12 0 ∧ maximumLayerCompilerTotalTests 2 12 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 12 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 12 0 ≤ maximumLayerCompilerTestBound 2 12 0 := by native_decide

/-- compiler_p2_r14_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 14 2 + maximumLayerCompilerPrimeEnvelopeGap 2 14 2 = maximumLayerCompilerPrimeEnvelopeBound 2 14 2 ∧ maximumLayerCompilerTotalTests 2 14 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 14 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 14 2 ≤ maximumLayerCompilerTestBound 2 14 2 := by native_decide

/-- compiler_p2_r17_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 17 1 + maximumLayerCompilerPrimeEnvelopeGap 2 17 1 = maximumLayerCompilerPrimeEnvelopeBound 2 17 1 ∧ maximumLayerCompilerTotalTests 2 17 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 17 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 17 1 ≤ maximumLayerCompilerTestBound 2 17 1 := by native_decide

/-- compiler_p2_r20_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 20 0 + maximumLayerCompilerPrimeEnvelopeGap 2 20 0 = maximumLayerCompilerPrimeEnvelopeBound 2 20 0 ∧ maximumLayerCompilerTotalTests 2 20 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 20 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 20 0 ≤ maximumLayerCompilerTestBound 2 20 0 := by native_decide

/-- compiler_p3_r2_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 2 2 + maximumLayerCompilerPrimeEnvelopeGap 3 2 2 = maximumLayerCompilerPrimeEnvelopeBound 3 2 2 ∧ maximumLayerCompilerTotalTests 3 2 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 2 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 2 2 ≤ maximumLayerCompilerTestBound 3 2 2 := by native_decide

/-- compiler_p3_r5_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 5 1 + maximumLayerCompilerPrimeEnvelopeGap 3 5 1 = maximumLayerCompilerPrimeEnvelopeBound 3 5 1 ∧ maximumLayerCompilerTotalTests 3 5 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 5 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 5 1 ≤ maximumLayerCompilerTestBound 3 5 1 := by native_decide

/-- compiler_p3_r8_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 8 0 + maximumLayerCompilerPrimeEnvelopeGap 3 8 0 = maximumLayerCompilerPrimeEnvelopeBound 3 8 0 ∧ maximumLayerCompilerTotalTests 3 8 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 8 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 8 0 ≤ maximumLayerCompilerTestBound 3 8 0 := by native_decide

/-- compiler_p3_r10_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 10 2 + maximumLayerCompilerPrimeEnvelopeGap 3 10 2 = maximumLayerCompilerPrimeEnvelopeBound 3 10 2 ∧ maximumLayerCompilerTotalTests 3 10 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 10 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 10 2 ≤ maximumLayerCompilerTestBound 3 10 2 := by native_decide

/-- compiler_p3_r13_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 13 1 + maximumLayerCompilerPrimeEnvelopeGap 3 13 1 = maximumLayerCompilerPrimeEnvelopeBound 3 13 1 ∧ maximumLayerCompilerTotalTests 3 13 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 13 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 13 1 ≤ maximumLayerCompilerTestBound 3 13 1 := by native_decide

/-- compiler_p3_r16_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 16 0 + maximumLayerCompilerPrimeEnvelopeGap 3 16 0 = maximumLayerCompilerPrimeEnvelopeBound 3 16 0 ∧ maximumLayerCompilerTotalTests 3 16 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 16 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 16 0 ≤ maximumLayerCompilerTestBound 3 16 0 := by native_decide

/-- compiler_p3_r18_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 18 2 + maximumLayerCompilerPrimeEnvelopeGap 3 18 2 = maximumLayerCompilerPrimeEnvelopeBound 3 18 2 ∧ maximumLayerCompilerTotalTests 3 18 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 18 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 18 2 ≤ maximumLayerCompilerTestBound 3 18 2 := by native_decide

/-- compiler_p5_r1_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 1 1 + maximumLayerCompilerPrimeEnvelopeGap 5 1 1 = maximumLayerCompilerPrimeEnvelopeBound 5 1 1 ∧ maximumLayerCompilerTotalTests 5 1 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 1 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 1 1 ≤ maximumLayerCompilerTestBound 5 1 1 := by native_decide

/-- compiler_p5_r4_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 4 0 + maximumLayerCompilerPrimeEnvelopeGap 5 4 0 = maximumLayerCompilerPrimeEnvelopeBound 5 4 0 ∧ maximumLayerCompilerTotalTests 5 4 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 4 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 4 0 ≤ maximumLayerCompilerTestBound 5 4 0 := by native_decide

/-- compiler_p5_r6_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 6 2 + maximumLayerCompilerPrimeEnvelopeGap 5 6 2 = maximumLayerCompilerPrimeEnvelopeBound 5 6 2 ∧ maximumLayerCompilerTotalTests 5 6 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 6 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 6 2 ≤ maximumLayerCompilerTestBound 5 6 2 := by native_decide

/-- compiler_p5_r9_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 9 1 + maximumLayerCompilerPrimeEnvelopeGap 5 9 1 = maximumLayerCompilerPrimeEnvelopeBound 5 9 1 ∧ maximumLayerCompilerTotalTests 5 9 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 9 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 9 1 ≤ maximumLayerCompilerTestBound 5 9 1 := by native_decide

/-- compiler_p5_r12_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 12 0 + maximumLayerCompilerPrimeEnvelopeGap 5 12 0 = maximumLayerCompilerPrimeEnvelopeBound 5 12 0 ∧ maximumLayerCompilerTotalTests 5 12 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 12 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 12 0 ≤ maximumLayerCompilerTestBound 5 12 0 := by native_decide

/-- compiler_p5_r14_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 14 2 + maximumLayerCompilerPrimeEnvelopeGap 5 14 2 = maximumLayerCompilerPrimeEnvelopeBound 5 14 2 ∧ maximumLayerCompilerTotalTests 5 14 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 14 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 14 2 ≤ maximumLayerCompilerTestBound 5 14 2 := by native_decide

/-- compiler_p5_r17_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 17 1 + maximumLayerCompilerPrimeEnvelopeGap 5 17 1 = maximumLayerCompilerPrimeEnvelopeBound 5 17 1 ∧ maximumLayerCompilerTotalTests 5 17 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 17 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 17 1 ≤ maximumLayerCompilerTestBound 5 17 1 := by native_decide

/-- compiler_p5_r20_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 20 0 + maximumLayerCompilerPrimeEnvelopeGap 5 20 0 = maximumLayerCompilerPrimeEnvelopeBound 5 20 0 ∧ maximumLayerCompilerTotalTests 5 20 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 20 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 20 0 ≤ maximumLayerCompilerTestBound 5 20 0 := by native_decide

/-- compiler_p7_r2_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 2 2 + maximumLayerCompilerPrimeEnvelopeGap 7 2 2 = maximumLayerCompilerPrimeEnvelopeBound 7 2 2 ∧ maximumLayerCompilerTotalTests 7 2 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 2 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 2 2 ≤ maximumLayerCompilerTestBound 7 2 2 := by native_decide

/-- compiler_p7_r5_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 5 1 + maximumLayerCompilerPrimeEnvelopeGap 7 5 1 = maximumLayerCompilerPrimeEnvelopeBound 7 5 1 ∧ maximumLayerCompilerTotalTests 7 5 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 5 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 5 1 ≤ maximumLayerCompilerTestBound 7 5 1 := by native_decide

/-- compiler_p7_r8_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 8 0 + maximumLayerCompilerPrimeEnvelopeGap 7 8 0 = maximumLayerCompilerPrimeEnvelopeBound 7 8 0 ∧ maximumLayerCompilerTotalTests 7 8 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 8 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 8 0 ≤ maximumLayerCompilerTestBound 7 8 0 := by native_decide

/-- compiler_p7_r10_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 10 2 + maximumLayerCompilerPrimeEnvelopeGap 7 10 2 = maximumLayerCompilerPrimeEnvelopeBound 7 10 2 ∧ maximumLayerCompilerTotalTests 7 10 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 10 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 10 2 ≤ maximumLayerCompilerTestBound 7 10 2 := by native_decide

/-- compiler_p7_r13_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 13 1 + maximumLayerCompilerPrimeEnvelopeGap 7 13 1 = maximumLayerCompilerPrimeEnvelopeBound 7 13 1 ∧ maximumLayerCompilerTotalTests 7 13 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 13 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 13 1 ≤ maximumLayerCompilerTestBound 7 13 1 := by native_decide

/-- compiler_p7_r16_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 16 0 + maximumLayerCompilerPrimeEnvelopeGap 7 16 0 = maximumLayerCompilerPrimeEnvelopeBound 7 16 0 ∧ maximumLayerCompilerTotalTests 7 16 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 16 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 16 0 ≤ maximumLayerCompilerTestBound 7 16 0 := by native_decide

/-- compiler_p7_r18_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 18 2 + maximumLayerCompilerPrimeEnvelopeGap 7 18 2 = maximumLayerCompilerPrimeEnvelopeBound 7 18 2 ∧ maximumLayerCompilerTotalTests 7 18 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 18 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 18 2 ≤ maximumLayerCompilerTestBound 7 18 2 := by native_decide

/-- compiler_p11_r1_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 1 1 + maximumLayerCompilerPrimeEnvelopeGap 11 1 1 = maximumLayerCompilerPrimeEnvelopeBound 11 1 1 ∧ maximumLayerCompilerTotalTests 11 1 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 1 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 1 1 ≤ maximumLayerCompilerTestBound 11 1 1 := by native_decide

/-- compiler_p11_r4_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 4 0 + maximumLayerCompilerPrimeEnvelopeGap 11 4 0 = maximumLayerCompilerPrimeEnvelopeBound 11 4 0 ∧ maximumLayerCompilerTotalTests 11 4 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 4 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 4 0 ≤ maximumLayerCompilerTestBound 11 4 0 := by native_decide

/-- compiler_p11_r6_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 6 2 + maximumLayerCompilerPrimeEnvelopeGap 11 6 2 = maximumLayerCompilerPrimeEnvelopeBound 11 6 2 ∧ maximumLayerCompilerTotalTests 11 6 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 6 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 6 2 ≤ maximumLayerCompilerTestBound 11 6 2 := by native_decide

/-- compiler_p11_r9_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 9 1 + maximumLayerCompilerPrimeEnvelopeGap 11 9 1 = maximumLayerCompilerPrimeEnvelopeBound 11 9 1 ∧ maximumLayerCompilerTotalTests 11 9 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 9 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 9 1 ≤ maximumLayerCompilerTestBound 11 9 1 := by native_decide

/-- compiler_p11_r12_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 12 0 + maximumLayerCompilerPrimeEnvelopeGap 11 12 0 = maximumLayerCompilerPrimeEnvelopeBound 11 12 0 ∧ maximumLayerCompilerTotalTests 11 12 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 12 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 12 0 ≤ maximumLayerCompilerTestBound 11 12 0 := by native_decide

/-- compiler_p11_r14_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 14 2 + maximumLayerCompilerPrimeEnvelopeGap 11 14 2 = maximumLayerCompilerPrimeEnvelopeBound 11 14 2 ∧ maximumLayerCompilerTotalTests 11 14 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 14 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 14 2 ≤ maximumLayerCompilerTestBound 11 14 2 := by native_decide

/-- compiler_p11_r17_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 17 1 + maximumLayerCompilerPrimeEnvelopeGap 11 17 1 = maximumLayerCompilerPrimeEnvelopeBound 11 17 1 ∧ maximumLayerCompilerTotalTests 11 17 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 17 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 17 1 ≤ maximumLayerCompilerTestBound 11 17 1 := by native_decide

/-- compiler_p11_r20_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 20 0 + maximumLayerCompilerPrimeEnvelopeGap 11 20 0 = maximumLayerCompilerPrimeEnvelopeBound 11 20 0 ∧ maximumLayerCompilerTotalTests 11 20 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 20 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 20 0 ≤ maximumLayerCompilerTestBound 11 20 0 := by native_decide

/-- compiler_p13_r2_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 2 2 + maximumLayerCompilerPrimeEnvelopeGap 13 2 2 = maximumLayerCompilerPrimeEnvelopeBound 13 2 2 ∧ maximumLayerCompilerTotalTests 13 2 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 2 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 2 2 ≤ maximumLayerCompilerTestBound 13 2 2 := by native_decide

/-- compiler_p13_r5_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 5 1 + maximumLayerCompilerPrimeEnvelopeGap 13 5 1 = maximumLayerCompilerPrimeEnvelopeBound 13 5 1 ∧ maximumLayerCompilerTotalTests 13 5 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 5 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 5 1 ≤ maximumLayerCompilerTestBound 13 5 1 := by native_decide

/-- compiler_p13_r8_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 8 0 + maximumLayerCompilerPrimeEnvelopeGap 13 8 0 = maximumLayerCompilerPrimeEnvelopeBound 13 8 0 ∧ maximumLayerCompilerTotalTests 13 8 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 8 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 8 0 ≤ maximumLayerCompilerTestBound 13 8 0 := by native_decide

/-- compiler_p13_r10_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 10 2 + maximumLayerCompilerPrimeEnvelopeGap 13 10 2 = maximumLayerCompilerPrimeEnvelopeBound 13 10 2 ∧ maximumLayerCompilerTotalTests 13 10 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 10 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 10 2 ≤ maximumLayerCompilerTestBound 13 10 2 := by native_decide

/-- compiler_p13_r13_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 13 1 + maximumLayerCompilerPrimeEnvelopeGap 13 13 1 = maximumLayerCompilerPrimeEnvelopeBound 13 13 1 ∧ maximumLayerCompilerTotalTests 13 13 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 13 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 13 1 ≤ maximumLayerCompilerTestBound 13 13 1 := by native_decide

/-- compiler_p13_r16_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 16 0 + maximumLayerCompilerPrimeEnvelopeGap 13 16 0 = maximumLayerCompilerPrimeEnvelopeBound 13 16 0 ∧ maximumLayerCompilerTotalTests 13 16 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 16 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 16 0 ≤ maximumLayerCompilerTestBound 13 16 0 := by native_decide

/-- compiler_p13_r18_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 18 2 + maximumLayerCompilerPrimeEnvelopeGap 13 18 2 = maximumLayerCompilerPrimeEnvelopeBound 13 18 2 ∧ maximumLayerCompilerTotalTests 13 18 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 18 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 18 2 ≤ maximumLayerCompilerTestBound 13 18 2 := by native_decide

end KomorebiPadic
