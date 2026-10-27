import KomorebiPadic

namespace KomorebiPadic

/-- representative_p1_B3 -/
example : radixRepresentativeBudget 1 3 + radixRepresentativeBudgetPrimeEnvelopeGap 1 3 = radixRepresentativeBudgetPrimeEnvelope 1 3 ∧ radixRepresentativeBudget 1 3 ≤ radixRepresentativeBudgetPrimeEnvelope 1 3 ∧ (radixRepresentativeBudget 1 3 = radixRepresentativeBudgetPrimeEnvelope 1 3 ↔ lastRadixBlockQuotient 1 3 = 0 ∨ lastRadixBlockRemainder 1 3 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 3 ≤ 3 * 3 := by native_decide

/-- representative_p1_B11 -/
example : radixRepresentativeBudget 1 11 + radixRepresentativeBudgetPrimeEnvelopeGap 1 11 = radixRepresentativeBudgetPrimeEnvelope 1 11 ∧ radixRepresentativeBudget 1 11 ≤ radixRepresentativeBudgetPrimeEnvelope 1 11 ∧ (radixRepresentativeBudget 1 11 = radixRepresentativeBudgetPrimeEnvelope 1 11 ↔ lastRadixBlockQuotient 1 11 = 0 ∨ lastRadixBlockRemainder 1 11 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 11 ≤ 11 * 11 := by native_decide

/-- representative_p1_B19 -/
example : radixRepresentativeBudget 1 19 + radixRepresentativeBudgetPrimeEnvelopeGap 1 19 = radixRepresentativeBudgetPrimeEnvelope 1 19 ∧ radixRepresentativeBudget 1 19 ≤ radixRepresentativeBudgetPrimeEnvelope 1 19 ∧ (radixRepresentativeBudget 1 19 = radixRepresentativeBudgetPrimeEnvelope 1 19 ↔ lastRadixBlockQuotient 1 19 = 0 ∨ lastRadixBlockRemainder 1 19 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 19 ≤ 19 * 19 := by native_decide

/-- representative_p1_B27 -/
example : radixRepresentativeBudget 1 27 + radixRepresentativeBudgetPrimeEnvelopeGap 1 27 = radixRepresentativeBudgetPrimeEnvelope 1 27 ∧ radixRepresentativeBudget 1 27 ≤ radixRepresentativeBudgetPrimeEnvelope 1 27 ∧ (radixRepresentativeBudget 1 27 = radixRepresentativeBudgetPrimeEnvelope 1 27 ↔ lastRadixBlockQuotient 1 27 = 0 ∨ lastRadixBlockRemainder 1 27 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 27 ≤ 27 * 27 := by native_decide

/-- representative_p1_B35 -/
example : radixRepresentativeBudget 1 35 + radixRepresentativeBudgetPrimeEnvelopeGap 1 35 = radixRepresentativeBudgetPrimeEnvelope 1 35 ∧ radixRepresentativeBudget 1 35 ≤ radixRepresentativeBudgetPrimeEnvelope 1 35 ∧ (radixRepresentativeBudget 1 35 = radixRepresentativeBudgetPrimeEnvelope 1 35 ↔ lastRadixBlockQuotient 1 35 = 0 ∨ lastRadixBlockRemainder 1 35 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 35 ≤ 35 * 35 := by native_decide

/-- representative_p1_B43 -/
example : radixRepresentativeBudget 1 43 + radixRepresentativeBudgetPrimeEnvelopeGap 1 43 = radixRepresentativeBudgetPrimeEnvelope 1 43 ∧ radixRepresentativeBudget 1 43 ≤ radixRepresentativeBudgetPrimeEnvelope 1 43 ∧ (radixRepresentativeBudget 1 43 = radixRepresentativeBudgetPrimeEnvelope 1 43 ↔ lastRadixBlockQuotient 1 43 = 0 ∨ lastRadixBlockRemainder 1 43 + 1 = 1) ∧ radixRepresentativeBudgetPrimeEnvelope 1 43 ≤ 43 * 43 := by native_decide

/-- representative_p2_B1 -/
example : radixRepresentativeBudget 2 1 + radixRepresentativeBudgetPrimeEnvelopeGap 2 1 = radixRepresentativeBudgetPrimeEnvelope 2 1 ∧ radixRepresentativeBudget 2 1 ≤ radixRepresentativeBudgetPrimeEnvelope 2 1 ∧ (radixRepresentativeBudget 2 1 = radixRepresentativeBudgetPrimeEnvelope 2 1 ↔ lastRadixBlockQuotient 2 1 = 0 ∨ lastRadixBlockRemainder 2 1 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 1 ≤ 1 * 1 := by native_decide

/-- representative_p2_B9 -/
example : radixRepresentativeBudget 2 9 + radixRepresentativeBudgetPrimeEnvelopeGap 2 9 = radixRepresentativeBudgetPrimeEnvelope 2 9 ∧ radixRepresentativeBudget 2 9 ≤ radixRepresentativeBudgetPrimeEnvelope 2 9 ∧ (radixRepresentativeBudget 2 9 = radixRepresentativeBudgetPrimeEnvelope 2 9 ↔ lastRadixBlockQuotient 2 9 = 0 ∨ lastRadixBlockRemainder 2 9 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 9 ≤ 9 * 9 := by native_decide

/-- representative_p2_B17 -/
example : radixRepresentativeBudget 2 17 + radixRepresentativeBudgetPrimeEnvelopeGap 2 17 = radixRepresentativeBudgetPrimeEnvelope 2 17 ∧ radixRepresentativeBudget 2 17 ≤ radixRepresentativeBudgetPrimeEnvelope 2 17 ∧ (radixRepresentativeBudget 2 17 = radixRepresentativeBudgetPrimeEnvelope 2 17 ↔ lastRadixBlockQuotient 2 17 = 0 ∨ lastRadixBlockRemainder 2 17 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 17 ≤ 17 * 17 := by native_decide

/-- representative_p2_B25 -/
example : radixRepresentativeBudget 2 25 + radixRepresentativeBudgetPrimeEnvelopeGap 2 25 = radixRepresentativeBudgetPrimeEnvelope 2 25 ∧ radixRepresentativeBudget 2 25 ≤ radixRepresentativeBudgetPrimeEnvelope 2 25 ∧ (radixRepresentativeBudget 2 25 = radixRepresentativeBudgetPrimeEnvelope 2 25 ↔ lastRadixBlockQuotient 2 25 = 0 ∨ lastRadixBlockRemainder 2 25 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 25 ≤ 25 * 25 := by native_decide

/-- representative_p2_B33 -/
example : radixRepresentativeBudget 2 33 + radixRepresentativeBudgetPrimeEnvelopeGap 2 33 = radixRepresentativeBudgetPrimeEnvelope 2 33 ∧ radixRepresentativeBudget 2 33 ≤ radixRepresentativeBudgetPrimeEnvelope 2 33 ∧ (radixRepresentativeBudget 2 33 = radixRepresentativeBudgetPrimeEnvelope 2 33 ↔ lastRadixBlockQuotient 2 33 = 0 ∨ lastRadixBlockRemainder 2 33 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 33 ≤ 33 * 33 := by native_decide

/-- representative_p2_B41 -/
example : radixRepresentativeBudget 2 41 + radixRepresentativeBudgetPrimeEnvelopeGap 2 41 = radixRepresentativeBudgetPrimeEnvelope 2 41 ∧ radixRepresentativeBudget 2 41 ≤ radixRepresentativeBudgetPrimeEnvelope 2 41 ∧ (radixRepresentativeBudget 2 41 = radixRepresentativeBudgetPrimeEnvelope 2 41 ↔ lastRadixBlockQuotient 2 41 = 0 ∨ lastRadixBlockRemainder 2 41 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 41 ≤ 41 * 41 := by native_decide

/-- representative_p2_B49 -/
example : radixRepresentativeBudget 2 49 + radixRepresentativeBudgetPrimeEnvelopeGap 2 49 = radixRepresentativeBudgetPrimeEnvelope 2 49 ∧ radixRepresentativeBudget 2 49 ≤ radixRepresentativeBudgetPrimeEnvelope 2 49 ∧ (radixRepresentativeBudget 2 49 = radixRepresentativeBudgetPrimeEnvelope 2 49 ↔ lastRadixBlockQuotient 2 49 = 0 ∨ lastRadixBlockRemainder 2 49 + 1 = 2) ∧ radixRepresentativeBudgetPrimeEnvelope 2 49 ≤ 49 * 49 := by native_decide

/-- representative_p3_B7 -/
example : radixRepresentativeBudget 3 7 + radixRepresentativeBudgetPrimeEnvelopeGap 3 7 = radixRepresentativeBudgetPrimeEnvelope 3 7 ∧ radixRepresentativeBudget 3 7 ≤ radixRepresentativeBudgetPrimeEnvelope 3 7 ∧ (radixRepresentativeBudget 3 7 = radixRepresentativeBudgetPrimeEnvelope 3 7 ↔ lastRadixBlockQuotient 3 7 = 0 ∨ lastRadixBlockRemainder 3 7 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 7 ≤ 7 * 7 := by native_decide

/-- representative_p3_B15 -/
example : radixRepresentativeBudget 3 15 + radixRepresentativeBudgetPrimeEnvelopeGap 3 15 = radixRepresentativeBudgetPrimeEnvelope 3 15 ∧ radixRepresentativeBudget 3 15 ≤ radixRepresentativeBudgetPrimeEnvelope 3 15 ∧ (radixRepresentativeBudget 3 15 = radixRepresentativeBudgetPrimeEnvelope 3 15 ↔ lastRadixBlockQuotient 3 15 = 0 ∨ lastRadixBlockRemainder 3 15 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 15 ≤ 15 * 15 := by native_decide

/-- representative_p3_B23 -/
example : radixRepresentativeBudget 3 23 + radixRepresentativeBudgetPrimeEnvelopeGap 3 23 = radixRepresentativeBudgetPrimeEnvelope 3 23 ∧ radixRepresentativeBudget 3 23 ≤ radixRepresentativeBudgetPrimeEnvelope 3 23 ∧ (radixRepresentativeBudget 3 23 = radixRepresentativeBudgetPrimeEnvelope 3 23 ↔ lastRadixBlockQuotient 3 23 = 0 ∨ lastRadixBlockRemainder 3 23 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 23 ≤ 23 * 23 := by native_decide

/-- representative_p3_B31 -/
example : radixRepresentativeBudget 3 31 + radixRepresentativeBudgetPrimeEnvelopeGap 3 31 = radixRepresentativeBudgetPrimeEnvelope 3 31 ∧ radixRepresentativeBudget 3 31 ≤ radixRepresentativeBudgetPrimeEnvelope 3 31 ∧ (radixRepresentativeBudget 3 31 = radixRepresentativeBudgetPrimeEnvelope 3 31 ↔ lastRadixBlockQuotient 3 31 = 0 ∨ lastRadixBlockRemainder 3 31 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 31 ≤ 31 * 31 := by native_decide

/-- representative_p3_B39 -/
example : radixRepresentativeBudget 3 39 + radixRepresentativeBudgetPrimeEnvelopeGap 3 39 = radixRepresentativeBudgetPrimeEnvelope 3 39 ∧ radixRepresentativeBudget 3 39 ≤ radixRepresentativeBudgetPrimeEnvelope 3 39 ∧ (radixRepresentativeBudget 3 39 = radixRepresentativeBudgetPrimeEnvelope 3 39 ↔ lastRadixBlockQuotient 3 39 = 0 ∨ lastRadixBlockRemainder 3 39 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 39 ≤ 39 * 39 := by native_decide

/-- representative_p3_B47 -/
example : radixRepresentativeBudget 3 47 + radixRepresentativeBudgetPrimeEnvelopeGap 3 47 = radixRepresentativeBudgetPrimeEnvelope 3 47 ∧ radixRepresentativeBudget 3 47 ≤ radixRepresentativeBudgetPrimeEnvelope 3 47 ∧ (radixRepresentativeBudget 3 47 = radixRepresentativeBudgetPrimeEnvelope 3 47 ↔ lastRadixBlockQuotient 3 47 = 0 ∨ lastRadixBlockRemainder 3 47 + 1 = 3) ∧ radixRepresentativeBudgetPrimeEnvelope 3 47 ≤ 47 * 47 := by native_decide

/-- representative_p4_B5 -/
example : radixRepresentativeBudget 4 5 + radixRepresentativeBudgetPrimeEnvelopeGap 4 5 = radixRepresentativeBudgetPrimeEnvelope 4 5 ∧ radixRepresentativeBudget 4 5 ≤ radixRepresentativeBudgetPrimeEnvelope 4 5 ∧ (radixRepresentativeBudget 4 5 = radixRepresentativeBudgetPrimeEnvelope 4 5 ↔ lastRadixBlockQuotient 4 5 = 0 ∨ lastRadixBlockRemainder 4 5 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 5 ≤ 5 * 5 := by native_decide

/-- representative_p4_B13 -/
example : radixRepresentativeBudget 4 13 + radixRepresentativeBudgetPrimeEnvelopeGap 4 13 = radixRepresentativeBudgetPrimeEnvelope 4 13 ∧ radixRepresentativeBudget 4 13 ≤ radixRepresentativeBudgetPrimeEnvelope 4 13 ∧ (radixRepresentativeBudget 4 13 = radixRepresentativeBudgetPrimeEnvelope 4 13 ↔ lastRadixBlockQuotient 4 13 = 0 ∨ lastRadixBlockRemainder 4 13 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 13 ≤ 13 * 13 := by native_decide

/-- representative_p4_B21 -/
example : radixRepresentativeBudget 4 21 + radixRepresentativeBudgetPrimeEnvelopeGap 4 21 = radixRepresentativeBudgetPrimeEnvelope 4 21 ∧ radixRepresentativeBudget 4 21 ≤ radixRepresentativeBudgetPrimeEnvelope 4 21 ∧ (radixRepresentativeBudget 4 21 = radixRepresentativeBudgetPrimeEnvelope 4 21 ↔ lastRadixBlockQuotient 4 21 = 0 ∨ lastRadixBlockRemainder 4 21 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 21 ≤ 21 * 21 := by native_decide

/-- representative_p4_B29 -/
example : radixRepresentativeBudget 4 29 + radixRepresentativeBudgetPrimeEnvelopeGap 4 29 = radixRepresentativeBudgetPrimeEnvelope 4 29 ∧ radixRepresentativeBudget 4 29 ≤ radixRepresentativeBudgetPrimeEnvelope 4 29 ∧ (radixRepresentativeBudget 4 29 = radixRepresentativeBudgetPrimeEnvelope 4 29 ↔ lastRadixBlockQuotient 4 29 = 0 ∨ lastRadixBlockRemainder 4 29 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 29 ≤ 29 * 29 := by native_decide

/-- representative_p4_B37 -/
example : radixRepresentativeBudget 4 37 + radixRepresentativeBudgetPrimeEnvelopeGap 4 37 = radixRepresentativeBudgetPrimeEnvelope 4 37 ∧ radixRepresentativeBudget 4 37 ≤ radixRepresentativeBudgetPrimeEnvelope 4 37 ∧ (radixRepresentativeBudget 4 37 = radixRepresentativeBudgetPrimeEnvelope 4 37 ↔ lastRadixBlockQuotient 4 37 = 0 ∨ lastRadixBlockRemainder 4 37 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 37 ≤ 37 * 37 := by native_decide

/-- representative_p4_B45 -/
example : radixRepresentativeBudget 4 45 + radixRepresentativeBudgetPrimeEnvelopeGap 4 45 = radixRepresentativeBudgetPrimeEnvelope 4 45 ∧ radixRepresentativeBudget 4 45 ≤ radixRepresentativeBudgetPrimeEnvelope 4 45 ∧ (radixRepresentativeBudget 4 45 = radixRepresentativeBudgetPrimeEnvelope 4 45 ↔ lastRadixBlockQuotient 4 45 = 0 ∨ lastRadixBlockRemainder 4 45 + 1 = 4) ∧ radixRepresentativeBudgetPrimeEnvelope 4 45 ≤ 45 * 45 := by native_decide

/-- representative_p5_B3 -/
example : radixRepresentativeBudget 5 3 + radixRepresentativeBudgetPrimeEnvelopeGap 5 3 = radixRepresentativeBudgetPrimeEnvelope 5 3 ∧ radixRepresentativeBudget 5 3 ≤ radixRepresentativeBudgetPrimeEnvelope 5 3 ∧ (radixRepresentativeBudget 5 3 = radixRepresentativeBudgetPrimeEnvelope 5 3 ↔ lastRadixBlockQuotient 5 3 = 0 ∨ lastRadixBlockRemainder 5 3 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 3 ≤ 3 * 3 := by native_decide

/-- representative_p5_B11 -/
example : radixRepresentativeBudget 5 11 + radixRepresentativeBudgetPrimeEnvelopeGap 5 11 = radixRepresentativeBudgetPrimeEnvelope 5 11 ∧ radixRepresentativeBudget 5 11 ≤ radixRepresentativeBudgetPrimeEnvelope 5 11 ∧ (radixRepresentativeBudget 5 11 = radixRepresentativeBudgetPrimeEnvelope 5 11 ↔ lastRadixBlockQuotient 5 11 = 0 ∨ lastRadixBlockRemainder 5 11 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 11 ≤ 11 * 11 := by native_decide

/-- representative_p5_B19 -/
example : radixRepresentativeBudget 5 19 + radixRepresentativeBudgetPrimeEnvelopeGap 5 19 = radixRepresentativeBudgetPrimeEnvelope 5 19 ∧ radixRepresentativeBudget 5 19 ≤ radixRepresentativeBudgetPrimeEnvelope 5 19 ∧ (radixRepresentativeBudget 5 19 = radixRepresentativeBudgetPrimeEnvelope 5 19 ↔ lastRadixBlockQuotient 5 19 = 0 ∨ lastRadixBlockRemainder 5 19 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 19 ≤ 19 * 19 := by native_decide

/-- representative_p5_B27 -/
example : radixRepresentativeBudget 5 27 + radixRepresentativeBudgetPrimeEnvelopeGap 5 27 = radixRepresentativeBudgetPrimeEnvelope 5 27 ∧ radixRepresentativeBudget 5 27 ≤ radixRepresentativeBudgetPrimeEnvelope 5 27 ∧ (radixRepresentativeBudget 5 27 = radixRepresentativeBudgetPrimeEnvelope 5 27 ↔ lastRadixBlockQuotient 5 27 = 0 ∨ lastRadixBlockRemainder 5 27 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 27 ≤ 27 * 27 := by native_decide

/-- representative_p5_B35 -/
example : radixRepresentativeBudget 5 35 + radixRepresentativeBudgetPrimeEnvelopeGap 5 35 = radixRepresentativeBudgetPrimeEnvelope 5 35 ∧ radixRepresentativeBudget 5 35 ≤ radixRepresentativeBudgetPrimeEnvelope 5 35 ∧ (radixRepresentativeBudget 5 35 = radixRepresentativeBudgetPrimeEnvelope 5 35 ↔ lastRadixBlockQuotient 5 35 = 0 ∨ lastRadixBlockRemainder 5 35 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 35 ≤ 35 * 35 := by native_decide

/-- representative_p5_B43 -/
example : radixRepresentativeBudget 5 43 + radixRepresentativeBudgetPrimeEnvelopeGap 5 43 = radixRepresentativeBudgetPrimeEnvelope 5 43 ∧ radixRepresentativeBudget 5 43 ≤ radixRepresentativeBudgetPrimeEnvelope 5 43 ∧ (radixRepresentativeBudget 5 43 = radixRepresentativeBudgetPrimeEnvelope 5 43 ↔ lastRadixBlockQuotient 5 43 = 0 ∨ lastRadixBlockRemainder 5 43 + 1 = 5) ∧ radixRepresentativeBudgetPrimeEnvelope 5 43 ≤ 43 * 43 := by native_decide

/-- representative_p6_B1 -/
example : radixRepresentativeBudget 6 1 + radixRepresentativeBudgetPrimeEnvelopeGap 6 1 = radixRepresentativeBudgetPrimeEnvelope 6 1 ∧ radixRepresentativeBudget 6 1 ≤ radixRepresentativeBudgetPrimeEnvelope 6 1 ∧ (radixRepresentativeBudget 6 1 = radixRepresentativeBudgetPrimeEnvelope 6 1 ↔ lastRadixBlockQuotient 6 1 = 0 ∨ lastRadixBlockRemainder 6 1 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 1 ≤ 1 * 1 := by native_decide

/-- representative_p6_B9 -/
example : radixRepresentativeBudget 6 9 + radixRepresentativeBudgetPrimeEnvelopeGap 6 9 = radixRepresentativeBudgetPrimeEnvelope 6 9 ∧ radixRepresentativeBudget 6 9 ≤ radixRepresentativeBudgetPrimeEnvelope 6 9 ∧ (radixRepresentativeBudget 6 9 = radixRepresentativeBudgetPrimeEnvelope 6 9 ↔ lastRadixBlockQuotient 6 9 = 0 ∨ lastRadixBlockRemainder 6 9 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 9 ≤ 9 * 9 := by native_decide

/-- representative_p6_B17 -/
example : radixRepresentativeBudget 6 17 + radixRepresentativeBudgetPrimeEnvelopeGap 6 17 = radixRepresentativeBudgetPrimeEnvelope 6 17 ∧ radixRepresentativeBudget 6 17 ≤ radixRepresentativeBudgetPrimeEnvelope 6 17 ∧ (radixRepresentativeBudget 6 17 = radixRepresentativeBudgetPrimeEnvelope 6 17 ↔ lastRadixBlockQuotient 6 17 = 0 ∨ lastRadixBlockRemainder 6 17 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 17 ≤ 17 * 17 := by native_decide

/-- representative_p6_B25 -/
example : radixRepresentativeBudget 6 25 + radixRepresentativeBudgetPrimeEnvelopeGap 6 25 = radixRepresentativeBudgetPrimeEnvelope 6 25 ∧ radixRepresentativeBudget 6 25 ≤ radixRepresentativeBudgetPrimeEnvelope 6 25 ∧ (radixRepresentativeBudget 6 25 = radixRepresentativeBudgetPrimeEnvelope 6 25 ↔ lastRadixBlockQuotient 6 25 = 0 ∨ lastRadixBlockRemainder 6 25 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 25 ≤ 25 * 25 := by native_decide

/-- representative_p6_B33 -/
example : radixRepresentativeBudget 6 33 + radixRepresentativeBudgetPrimeEnvelopeGap 6 33 = radixRepresentativeBudgetPrimeEnvelope 6 33 ∧ radixRepresentativeBudget 6 33 ≤ radixRepresentativeBudgetPrimeEnvelope 6 33 ∧ (radixRepresentativeBudget 6 33 = radixRepresentativeBudgetPrimeEnvelope 6 33 ↔ lastRadixBlockQuotient 6 33 = 0 ∨ lastRadixBlockRemainder 6 33 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 33 ≤ 33 * 33 := by native_decide

/-- representative_p6_B41 -/
example : radixRepresentativeBudget 6 41 + radixRepresentativeBudgetPrimeEnvelopeGap 6 41 = radixRepresentativeBudgetPrimeEnvelope 6 41 ∧ radixRepresentativeBudget 6 41 ≤ radixRepresentativeBudgetPrimeEnvelope 6 41 ∧ (radixRepresentativeBudget 6 41 = radixRepresentativeBudgetPrimeEnvelope 6 41 ↔ lastRadixBlockQuotient 6 41 = 0 ∨ lastRadixBlockRemainder 6 41 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 41 ≤ 41 * 41 := by native_decide

/-- representative_p6_B49 -/
example : radixRepresentativeBudget 6 49 + radixRepresentativeBudgetPrimeEnvelopeGap 6 49 = radixRepresentativeBudgetPrimeEnvelope 6 49 ∧ radixRepresentativeBudget 6 49 ≤ radixRepresentativeBudgetPrimeEnvelope 6 49 ∧ (radixRepresentativeBudget 6 49 = radixRepresentativeBudgetPrimeEnvelope 6 49 ↔ lastRadixBlockQuotient 6 49 = 0 ∨ lastRadixBlockRemainder 6 49 + 1 = 6) ∧ radixRepresentativeBudgetPrimeEnvelope 6 49 ≤ 49 * 49 := by native_decide

/-- representative_p7_B7 -/
example : radixRepresentativeBudget 7 7 + radixRepresentativeBudgetPrimeEnvelopeGap 7 7 = radixRepresentativeBudgetPrimeEnvelope 7 7 ∧ radixRepresentativeBudget 7 7 ≤ radixRepresentativeBudgetPrimeEnvelope 7 7 ∧ (radixRepresentativeBudget 7 7 = radixRepresentativeBudgetPrimeEnvelope 7 7 ↔ lastRadixBlockQuotient 7 7 = 0 ∨ lastRadixBlockRemainder 7 7 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 7 ≤ 7 * 7 := by native_decide

/-- representative_p7_B15 -/
example : radixRepresentativeBudget 7 15 + radixRepresentativeBudgetPrimeEnvelopeGap 7 15 = radixRepresentativeBudgetPrimeEnvelope 7 15 ∧ radixRepresentativeBudget 7 15 ≤ radixRepresentativeBudgetPrimeEnvelope 7 15 ∧ (radixRepresentativeBudget 7 15 = radixRepresentativeBudgetPrimeEnvelope 7 15 ↔ lastRadixBlockQuotient 7 15 = 0 ∨ lastRadixBlockRemainder 7 15 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 15 ≤ 15 * 15 := by native_decide

/-- representative_p7_B23 -/
example : radixRepresentativeBudget 7 23 + radixRepresentativeBudgetPrimeEnvelopeGap 7 23 = radixRepresentativeBudgetPrimeEnvelope 7 23 ∧ radixRepresentativeBudget 7 23 ≤ radixRepresentativeBudgetPrimeEnvelope 7 23 ∧ (radixRepresentativeBudget 7 23 = radixRepresentativeBudgetPrimeEnvelope 7 23 ↔ lastRadixBlockQuotient 7 23 = 0 ∨ lastRadixBlockRemainder 7 23 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 23 ≤ 23 * 23 := by native_decide

/-- representative_p7_B31 -/
example : radixRepresentativeBudget 7 31 + radixRepresentativeBudgetPrimeEnvelopeGap 7 31 = radixRepresentativeBudgetPrimeEnvelope 7 31 ∧ radixRepresentativeBudget 7 31 ≤ radixRepresentativeBudgetPrimeEnvelope 7 31 ∧ (radixRepresentativeBudget 7 31 = radixRepresentativeBudgetPrimeEnvelope 7 31 ↔ lastRadixBlockQuotient 7 31 = 0 ∨ lastRadixBlockRemainder 7 31 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 31 ≤ 31 * 31 := by native_decide

/-- representative_p7_B39 -/
example : radixRepresentativeBudget 7 39 + radixRepresentativeBudgetPrimeEnvelopeGap 7 39 = radixRepresentativeBudgetPrimeEnvelope 7 39 ∧ radixRepresentativeBudget 7 39 ≤ radixRepresentativeBudgetPrimeEnvelope 7 39 ∧ (radixRepresentativeBudget 7 39 = radixRepresentativeBudgetPrimeEnvelope 7 39 ↔ lastRadixBlockQuotient 7 39 = 0 ∨ lastRadixBlockRemainder 7 39 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 39 ≤ 39 * 39 := by native_decide

/-- representative_p7_B47 -/
example : radixRepresentativeBudget 7 47 + radixRepresentativeBudgetPrimeEnvelopeGap 7 47 = radixRepresentativeBudgetPrimeEnvelope 7 47 ∧ radixRepresentativeBudget 7 47 ≤ radixRepresentativeBudgetPrimeEnvelope 7 47 ∧ (radixRepresentativeBudget 7 47 = radixRepresentativeBudgetPrimeEnvelope 7 47 ↔ lastRadixBlockQuotient 7 47 = 0 ∨ lastRadixBlockRemainder 7 47 + 1 = 7) ∧ radixRepresentativeBudgetPrimeEnvelope 7 47 ≤ 47 * 47 := by native_decide

/-- representative_p8_B5 -/
example : radixRepresentativeBudget 8 5 + radixRepresentativeBudgetPrimeEnvelopeGap 8 5 = radixRepresentativeBudgetPrimeEnvelope 8 5 ∧ radixRepresentativeBudget 8 5 ≤ radixRepresentativeBudgetPrimeEnvelope 8 5 ∧ (radixRepresentativeBudget 8 5 = radixRepresentativeBudgetPrimeEnvelope 8 5 ↔ lastRadixBlockQuotient 8 5 = 0 ∨ lastRadixBlockRemainder 8 5 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 5 ≤ 5 * 5 := by native_decide

/-- representative_p8_B13 -/
example : radixRepresentativeBudget 8 13 + radixRepresentativeBudgetPrimeEnvelopeGap 8 13 = radixRepresentativeBudgetPrimeEnvelope 8 13 ∧ radixRepresentativeBudget 8 13 ≤ radixRepresentativeBudgetPrimeEnvelope 8 13 ∧ (radixRepresentativeBudget 8 13 = radixRepresentativeBudgetPrimeEnvelope 8 13 ↔ lastRadixBlockQuotient 8 13 = 0 ∨ lastRadixBlockRemainder 8 13 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 13 ≤ 13 * 13 := by native_decide

/-- representative_p8_B21 -/
example : radixRepresentativeBudget 8 21 + radixRepresentativeBudgetPrimeEnvelopeGap 8 21 = radixRepresentativeBudgetPrimeEnvelope 8 21 ∧ radixRepresentativeBudget 8 21 ≤ radixRepresentativeBudgetPrimeEnvelope 8 21 ∧ (radixRepresentativeBudget 8 21 = radixRepresentativeBudgetPrimeEnvelope 8 21 ↔ lastRadixBlockQuotient 8 21 = 0 ∨ lastRadixBlockRemainder 8 21 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 21 ≤ 21 * 21 := by native_decide

/-- representative_p8_B29 -/
example : radixRepresentativeBudget 8 29 + radixRepresentativeBudgetPrimeEnvelopeGap 8 29 = radixRepresentativeBudgetPrimeEnvelope 8 29 ∧ radixRepresentativeBudget 8 29 ≤ radixRepresentativeBudgetPrimeEnvelope 8 29 ∧ (radixRepresentativeBudget 8 29 = radixRepresentativeBudgetPrimeEnvelope 8 29 ↔ lastRadixBlockQuotient 8 29 = 0 ∨ lastRadixBlockRemainder 8 29 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 29 ≤ 29 * 29 := by native_decide

/-- representative_p8_B37 -/
example : radixRepresentativeBudget 8 37 + radixRepresentativeBudgetPrimeEnvelopeGap 8 37 = radixRepresentativeBudgetPrimeEnvelope 8 37 ∧ radixRepresentativeBudget 8 37 ≤ radixRepresentativeBudgetPrimeEnvelope 8 37 ∧ (radixRepresentativeBudget 8 37 = radixRepresentativeBudgetPrimeEnvelope 8 37 ↔ lastRadixBlockQuotient 8 37 = 0 ∨ lastRadixBlockRemainder 8 37 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 37 ≤ 37 * 37 := by native_decide

/-- representative_p8_B45 -/
example : radixRepresentativeBudget 8 45 + radixRepresentativeBudgetPrimeEnvelopeGap 8 45 = radixRepresentativeBudgetPrimeEnvelope 8 45 ∧ radixRepresentativeBudget 8 45 ≤ radixRepresentativeBudgetPrimeEnvelope 8 45 ∧ (radixRepresentativeBudget 8 45 = radixRepresentativeBudgetPrimeEnvelope 8 45 ↔ lastRadixBlockQuotient 8 45 = 0 ∨ lastRadixBlockRemainder 8 45 + 1 = 8) ∧ radixRepresentativeBudgetPrimeEnvelope 8 45 ≤ 45 * 45 := by native_decide

/-- representative_p9_B3 -/
example : radixRepresentativeBudget 9 3 + radixRepresentativeBudgetPrimeEnvelopeGap 9 3 = radixRepresentativeBudgetPrimeEnvelope 9 3 ∧ radixRepresentativeBudget 9 3 ≤ radixRepresentativeBudgetPrimeEnvelope 9 3 ∧ (radixRepresentativeBudget 9 3 = radixRepresentativeBudgetPrimeEnvelope 9 3 ↔ lastRadixBlockQuotient 9 3 = 0 ∨ lastRadixBlockRemainder 9 3 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 3 ≤ 3 * 3 := by native_decide

/-- representative_p9_B11 -/
example : radixRepresentativeBudget 9 11 + radixRepresentativeBudgetPrimeEnvelopeGap 9 11 = radixRepresentativeBudgetPrimeEnvelope 9 11 ∧ radixRepresentativeBudget 9 11 ≤ radixRepresentativeBudgetPrimeEnvelope 9 11 ∧ (radixRepresentativeBudget 9 11 = radixRepresentativeBudgetPrimeEnvelope 9 11 ↔ lastRadixBlockQuotient 9 11 = 0 ∨ lastRadixBlockRemainder 9 11 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 11 ≤ 11 * 11 := by native_decide

/-- representative_p9_B19 -/
example : radixRepresentativeBudget 9 19 + radixRepresentativeBudgetPrimeEnvelopeGap 9 19 = radixRepresentativeBudgetPrimeEnvelope 9 19 ∧ radixRepresentativeBudget 9 19 ≤ radixRepresentativeBudgetPrimeEnvelope 9 19 ∧ (radixRepresentativeBudget 9 19 = radixRepresentativeBudgetPrimeEnvelope 9 19 ↔ lastRadixBlockQuotient 9 19 = 0 ∨ lastRadixBlockRemainder 9 19 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 19 ≤ 19 * 19 := by native_decide

/-- representative_p9_B27 -/
example : radixRepresentativeBudget 9 27 + radixRepresentativeBudgetPrimeEnvelopeGap 9 27 = radixRepresentativeBudgetPrimeEnvelope 9 27 ∧ radixRepresentativeBudget 9 27 ≤ radixRepresentativeBudgetPrimeEnvelope 9 27 ∧ (radixRepresentativeBudget 9 27 = radixRepresentativeBudgetPrimeEnvelope 9 27 ↔ lastRadixBlockQuotient 9 27 = 0 ∨ lastRadixBlockRemainder 9 27 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 27 ≤ 27 * 27 := by native_decide

/-- representative_p9_B35 -/
example : radixRepresentativeBudget 9 35 + radixRepresentativeBudgetPrimeEnvelopeGap 9 35 = radixRepresentativeBudgetPrimeEnvelope 9 35 ∧ radixRepresentativeBudget 9 35 ≤ radixRepresentativeBudgetPrimeEnvelope 9 35 ∧ (radixRepresentativeBudget 9 35 = radixRepresentativeBudgetPrimeEnvelope 9 35 ↔ lastRadixBlockQuotient 9 35 = 0 ∨ lastRadixBlockRemainder 9 35 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 35 ≤ 35 * 35 := by native_decide

/-- representative_p9_B43 -/
example : radixRepresentativeBudget 9 43 + radixRepresentativeBudgetPrimeEnvelopeGap 9 43 = radixRepresentativeBudgetPrimeEnvelope 9 43 ∧ radixRepresentativeBudget 9 43 ≤ radixRepresentativeBudgetPrimeEnvelope 9 43 ∧ (radixRepresentativeBudget 9 43 = radixRepresentativeBudgetPrimeEnvelope 9 43 ↔ lastRadixBlockQuotient 9 43 = 0 ∨ lastRadixBlockRemainder 9 43 + 1 = 9) ∧ radixRepresentativeBudgetPrimeEnvelope 9 43 ≤ 43 * 43 := by native_decide

/-- representative_p10_B1 -/
example : radixRepresentativeBudget 10 1 + radixRepresentativeBudgetPrimeEnvelopeGap 10 1 = radixRepresentativeBudgetPrimeEnvelope 10 1 ∧ radixRepresentativeBudget 10 1 ≤ radixRepresentativeBudgetPrimeEnvelope 10 1 ∧ (radixRepresentativeBudget 10 1 = radixRepresentativeBudgetPrimeEnvelope 10 1 ↔ lastRadixBlockQuotient 10 1 = 0 ∨ lastRadixBlockRemainder 10 1 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 1 ≤ 1 * 1 := by native_decide

/-- representative_p10_B9 -/
example : radixRepresentativeBudget 10 9 + radixRepresentativeBudgetPrimeEnvelopeGap 10 9 = radixRepresentativeBudgetPrimeEnvelope 10 9 ∧ radixRepresentativeBudget 10 9 ≤ radixRepresentativeBudgetPrimeEnvelope 10 9 ∧ (radixRepresentativeBudget 10 9 = radixRepresentativeBudgetPrimeEnvelope 10 9 ↔ lastRadixBlockQuotient 10 9 = 0 ∨ lastRadixBlockRemainder 10 9 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 9 ≤ 9 * 9 := by native_decide

/-- representative_p10_B17 -/
example : radixRepresentativeBudget 10 17 + radixRepresentativeBudgetPrimeEnvelopeGap 10 17 = radixRepresentativeBudgetPrimeEnvelope 10 17 ∧ radixRepresentativeBudget 10 17 ≤ radixRepresentativeBudgetPrimeEnvelope 10 17 ∧ (radixRepresentativeBudget 10 17 = radixRepresentativeBudgetPrimeEnvelope 10 17 ↔ lastRadixBlockQuotient 10 17 = 0 ∨ lastRadixBlockRemainder 10 17 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 17 ≤ 17 * 17 := by native_decide

/-- representative_p10_B25 -/
example : radixRepresentativeBudget 10 25 + radixRepresentativeBudgetPrimeEnvelopeGap 10 25 = radixRepresentativeBudgetPrimeEnvelope 10 25 ∧ radixRepresentativeBudget 10 25 ≤ radixRepresentativeBudgetPrimeEnvelope 10 25 ∧ (radixRepresentativeBudget 10 25 = radixRepresentativeBudgetPrimeEnvelope 10 25 ↔ lastRadixBlockQuotient 10 25 = 0 ∨ lastRadixBlockRemainder 10 25 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 25 ≤ 25 * 25 := by native_decide

/-- representative_p10_B33 -/
example : radixRepresentativeBudget 10 33 + radixRepresentativeBudgetPrimeEnvelopeGap 10 33 = radixRepresentativeBudgetPrimeEnvelope 10 33 ∧ radixRepresentativeBudget 10 33 ≤ radixRepresentativeBudgetPrimeEnvelope 10 33 ∧ (radixRepresentativeBudget 10 33 = radixRepresentativeBudgetPrimeEnvelope 10 33 ↔ lastRadixBlockQuotient 10 33 = 0 ∨ lastRadixBlockRemainder 10 33 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 33 ≤ 33 * 33 := by native_decide

/-- representative_p10_B41 -/
example : radixRepresentativeBudget 10 41 + radixRepresentativeBudgetPrimeEnvelopeGap 10 41 = radixRepresentativeBudgetPrimeEnvelope 10 41 ∧ radixRepresentativeBudget 10 41 ≤ radixRepresentativeBudgetPrimeEnvelope 10 41 ∧ (radixRepresentativeBudget 10 41 = radixRepresentativeBudgetPrimeEnvelope 10 41 ↔ lastRadixBlockQuotient 10 41 = 0 ∨ lastRadixBlockRemainder 10 41 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 41 ≤ 41 * 41 := by native_decide

/-- representative_p10_B49 -/
example : radixRepresentativeBudget 10 49 + radixRepresentativeBudgetPrimeEnvelopeGap 10 49 = radixRepresentativeBudgetPrimeEnvelope 10 49 ∧ radixRepresentativeBudget 10 49 ≤ radixRepresentativeBudgetPrimeEnvelope 10 49 ∧ (radixRepresentativeBudget 10 49 = radixRepresentativeBudgetPrimeEnvelope 10 49 ↔ lastRadixBlockQuotient 10 49 = 0 ∨ lastRadixBlockRemainder 10 49 + 1 = 10) ∧ radixRepresentativeBudgetPrimeEnvelope 10 49 ≤ 49 * 49 := by native_decide

/-- representative_p11_B7 -/
example : radixRepresentativeBudget 11 7 + radixRepresentativeBudgetPrimeEnvelopeGap 11 7 = radixRepresentativeBudgetPrimeEnvelope 11 7 ∧ radixRepresentativeBudget 11 7 ≤ radixRepresentativeBudgetPrimeEnvelope 11 7 ∧ (radixRepresentativeBudget 11 7 = radixRepresentativeBudgetPrimeEnvelope 11 7 ↔ lastRadixBlockQuotient 11 7 = 0 ∨ lastRadixBlockRemainder 11 7 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 7 ≤ 7 * 7 := by native_decide

/-- representative_p11_B15 -/
example : radixRepresentativeBudget 11 15 + radixRepresentativeBudgetPrimeEnvelopeGap 11 15 = radixRepresentativeBudgetPrimeEnvelope 11 15 ∧ radixRepresentativeBudget 11 15 ≤ radixRepresentativeBudgetPrimeEnvelope 11 15 ∧ (radixRepresentativeBudget 11 15 = radixRepresentativeBudgetPrimeEnvelope 11 15 ↔ lastRadixBlockQuotient 11 15 = 0 ∨ lastRadixBlockRemainder 11 15 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 15 ≤ 15 * 15 := by native_decide

/-- representative_p11_B23 -/
example : radixRepresentativeBudget 11 23 + radixRepresentativeBudgetPrimeEnvelopeGap 11 23 = radixRepresentativeBudgetPrimeEnvelope 11 23 ∧ radixRepresentativeBudget 11 23 ≤ radixRepresentativeBudgetPrimeEnvelope 11 23 ∧ (radixRepresentativeBudget 11 23 = radixRepresentativeBudgetPrimeEnvelope 11 23 ↔ lastRadixBlockQuotient 11 23 = 0 ∨ lastRadixBlockRemainder 11 23 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 23 ≤ 23 * 23 := by native_decide

/-- representative_p11_B31 -/
example : radixRepresentativeBudget 11 31 + radixRepresentativeBudgetPrimeEnvelopeGap 11 31 = radixRepresentativeBudgetPrimeEnvelope 11 31 ∧ radixRepresentativeBudget 11 31 ≤ radixRepresentativeBudgetPrimeEnvelope 11 31 ∧ (radixRepresentativeBudget 11 31 = radixRepresentativeBudgetPrimeEnvelope 11 31 ↔ lastRadixBlockQuotient 11 31 = 0 ∨ lastRadixBlockRemainder 11 31 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 31 ≤ 31 * 31 := by native_decide

/-- representative_p11_B39 -/
example : radixRepresentativeBudget 11 39 + radixRepresentativeBudgetPrimeEnvelopeGap 11 39 = radixRepresentativeBudgetPrimeEnvelope 11 39 ∧ radixRepresentativeBudget 11 39 ≤ radixRepresentativeBudgetPrimeEnvelope 11 39 ∧ (radixRepresentativeBudget 11 39 = radixRepresentativeBudgetPrimeEnvelope 11 39 ↔ lastRadixBlockQuotient 11 39 = 0 ∨ lastRadixBlockRemainder 11 39 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 39 ≤ 39 * 39 := by native_decide

/-- representative_p11_B47 -/
example : radixRepresentativeBudget 11 47 + radixRepresentativeBudgetPrimeEnvelopeGap 11 47 = radixRepresentativeBudgetPrimeEnvelope 11 47 ∧ radixRepresentativeBudget 11 47 ≤ radixRepresentativeBudgetPrimeEnvelope 11 47 ∧ (radixRepresentativeBudget 11 47 = radixRepresentativeBudgetPrimeEnvelope 11 47 ↔ lastRadixBlockQuotient 11 47 = 0 ∨ lastRadixBlockRemainder 11 47 + 1 = 11) ∧ radixRepresentativeBudgetPrimeEnvelope 11 47 ≤ 47 * 47 := by native_decide

/-- representative_p12_B5 -/
example : radixRepresentativeBudget 12 5 + radixRepresentativeBudgetPrimeEnvelopeGap 12 5 = radixRepresentativeBudgetPrimeEnvelope 12 5 ∧ radixRepresentativeBudget 12 5 ≤ radixRepresentativeBudgetPrimeEnvelope 12 5 ∧ (radixRepresentativeBudget 12 5 = radixRepresentativeBudgetPrimeEnvelope 12 5 ↔ lastRadixBlockQuotient 12 5 = 0 ∨ lastRadixBlockRemainder 12 5 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 5 ≤ 5 * 5 := by native_decide

/-- representative_p12_B13 -/
example : radixRepresentativeBudget 12 13 + radixRepresentativeBudgetPrimeEnvelopeGap 12 13 = radixRepresentativeBudgetPrimeEnvelope 12 13 ∧ radixRepresentativeBudget 12 13 ≤ radixRepresentativeBudgetPrimeEnvelope 12 13 ∧ (radixRepresentativeBudget 12 13 = radixRepresentativeBudgetPrimeEnvelope 12 13 ↔ lastRadixBlockQuotient 12 13 = 0 ∨ lastRadixBlockRemainder 12 13 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 13 ≤ 13 * 13 := by native_decide

/-- representative_p12_B21 -/
example : radixRepresentativeBudget 12 21 + radixRepresentativeBudgetPrimeEnvelopeGap 12 21 = radixRepresentativeBudgetPrimeEnvelope 12 21 ∧ radixRepresentativeBudget 12 21 ≤ radixRepresentativeBudgetPrimeEnvelope 12 21 ∧ (radixRepresentativeBudget 12 21 = radixRepresentativeBudgetPrimeEnvelope 12 21 ↔ lastRadixBlockQuotient 12 21 = 0 ∨ lastRadixBlockRemainder 12 21 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 21 ≤ 21 * 21 := by native_decide

/-- representative_p12_B29 -/
example : radixRepresentativeBudget 12 29 + radixRepresentativeBudgetPrimeEnvelopeGap 12 29 = radixRepresentativeBudgetPrimeEnvelope 12 29 ∧ radixRepresentativeBudget 12 29 ≤ radixRepresentativeBudgetPrimeEnvelope 12 29 ∧ (radixRepresentativeBudget 12 29 = radixRepresentativeBudgetPrimeEnvelope 12 29 ↔ lastRadixBlockQuotient 12 29 = 0 ∨ lastRadixBlockRemainder 12 29 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 29 ≤ 29 * 29 := by native_decide

/-- representative_p12_B37 -/
example : radixRepresentativeBudget 12 37 + radixRepresentativeBudgetPrimeEnvelopeGap 12 37 = radixRepresentativeBudgetPrimeEnvelope 12 37 ∧ radixRepresentativeBudget 12 37 ≤ radixRepresentativeBudgetPrimeEnvelope 12 37 ∧ (radixRepresentativeBudget 12 37 = radixRepresentativeBudgetPrimeEnvelope 12 37 ↔ lastRadixBlockQuotient 12 37 = 0 ∨ lastRadixBlockRemainder 12 37 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 37 ≤ 37 * 37 := by native_decide

/-- representative_p12_B45 -/
example : radixRepresentativeBudget 12 45 + radixRepresentativeBudgetPrimeEnvelopeGap 12 45 = radixRepresentativeBudgetPrimeEnvelope 12 45 ∧ radixRepresentativeBudget 12 45 ≤ radixRepresentativeBudgetPrimeEnvelope 12 45 ∧ (radixRepresentativeBudget 12 45 = radixRepresentativeBudgetPrimeEnvelope 12 45 ↔ lastRadixBlockQuotient 12 45 = 0 ∨ lastRadixBlockRemainder 12 45 + 1 = 12) ∧ radixRepresentativeBudgetPrimeEnvelope 12 45 ≤ 45 * 45 := by native_decide

/-- zero_base_B3 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 3 ≤ 3 * 3 := by native_decide

/-- zero_base_B11 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 11 ≤ 11 * 11 := by native_decide

/-- zero_base_B19 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 19 ≤ 19 * 19 := by native_decide

/-- zero_base_B27 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 27 ≤ 27 * 27 := by native_decide

/-- zero_base_B35 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 35 ≤ 35 * 35 := by native_decide

/-- zero_base_B43 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 43 ≤ 43 * 43 := by native_decide

/-- zero_base_B51 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 51 ≤ 51 * 51 := by native_decide

/-- zero_base_B59 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 59 ≤ 59 * 59 := by native_decide

/-- zero_base_B67 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 67 ≤ 67 * 67 := by native_decide

/-- zero_base_B75 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 75 ≤ 75 * 75 := by native_decide

/-- zero_base_B83 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 83 ≤ 83 * 83 := by native_decide

/-- zero_base_B91 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 91 ≤ 91 * 91 := by native_decide

/-- zero_base_B99 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 99 ≤ 99 * 99 := by native_decide

/-- zero_base_B107 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 107 ≤ 107 * 107 := by native_decide

/-- zero_base_B115 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 115 ≤ 115 * 115 := by native_decide

/-- zero_base_B123 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 123 ≤ 123 * 123 := by native_decide

/-- zero_base_B131 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 131 ≤ 131 * 131 := by native_decide

/-- zero_base_B139 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 139 ≤ 139 * 139 := by native_decide

/-- zero_base_B147 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 147 ≤ 147 * 147 := by native_decide

/-- zero_base_B155 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 155 ≤ 155 * 155 := by native_decide

/-- zero_base_B163 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 163 ≤ 163 * 163 := by native_decide

/-- zero_base_B171 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 171 ≤ 171 * 171 := by native_decide

/-- zero_base_B179 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 179 ≤ 179 * 179 := by native_decide

/-- zero_base_B187 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 187 ≤ 187 * 187 := by native_decide

/-- zero_base_B195 -/
example : radixRepresentativeBudgetPrimeEnvelope 0 195 ≤ 195 * 195 := by native_decide

/-- compiler_p2_r2_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 2 0 + maximumLayerCompilerPrimeEnvelopeGap 2 2 0 = maximumLayerCompilerPrimeEnvelopeBound 2 2 0 ∧ maximumLayerCompilerTotalTests 2 2 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 2 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 2 0 ≤ maximumLayerCompilerTestBound 2 2 0 := by native_decide

/-- compiler_p2_r4_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 4 2 + maximumLayerCompilerPrimeEnvelopeGap 2 4 2 = maximumLayerCompilerPrimeEnvelopeBound 2 4 2 ∧ maximumLayerCompilerTotalTests 2 4 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 4 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 4 2 ≤ maximumLayerCompilerTestBound 2 4 2 := by native_decide

/-- compiler_p2_r7_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 7 1 + maximumLayerCompilerPrimeEnvelopeGap 2 7 1 = maximumLayerCompilerPrimeEnvelopeBound 2 7 1 ∧ maximumLayerCompilerTotalTests 2 7 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 7 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 7 1 ≤ maximumLayerCompilerTestBound 2 7 1 := by native_decide

/-- compiler_p2_r10_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 10 0 + maximumLayerCompilerPrimeEnvelopeGap 2 10 0 = maximumLayerCompilerPrimeEnvelopeBound 2 10 0 ∧ maximumLayerCompilerTotalTests 2 10 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 10 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 10 0 ≤ maximumLayerCompilerTestBound 2 10 0 := by native_decide

/-- compiler_p2_r12_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 12 2 + maximumLayerCompilerPrimeEnvelopeGap 2 12 2 = maximumLayerCompilerPrimeEnvelopeBound 2 12 2 ∧ maximumLayerCompilerTotalTests 2 12 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 12 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 12 2 ≤ maximumLayerCompilerTestBound 2 12 2 := by native_decide

/-- compiler_p2_r15_h1 -/
example : maximumLayerCompilerClosedBudgetBound 2 15 1 + maximumLayerCompilerPrimeEnvelopeGap 2 15 1 = maximumLayerCompilerPrimeEnvelopeBound 2 15 1 ∧ maximumLayerCompilerTotalTests 2 15 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 15 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 15 1 ≤ maximumLayerCompilerTestBound 2 15 1 := by native_decide

/-- compiler_p2_r18_h0 -/
example : maximumLayerCompilerClosedBudgetBound 2 18 0 + maximumLayerCompilerPrimeEnvelopeGap 2 18 0 = maximumLayerCompilerPrimeEnvelopeBound 2 18 0 ∧ maximumLayerCompilerTotalTests 2 18 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 18 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 18 0 ≤ maximumLayerCompilerTestBound 2 18 0 := by native_decide

/-- compiler_p2_r20_h2 -/
example : maximumLayerCompilerClosedBudgetBound 2 20 2 + maximumLayerCompilerPrimeEnvelopeGap 2 20 2 = maximumLayerCompilerPrimeEnvelopeBound 2 20 2 ∧ maximumLayerCompilerTotalTests 2 20 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 2 20 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 2 20 2 ≤ maximumLayerCompilerTestBound 2 20 2 := by native_decide

/-- compiler_p3_r3_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 3 1 + maximumLayerCompilerPrimeEnvelopeGap 3 3 1 = maximumLayerCompilerPrimeEnvelopeBound 3 3 1 ∧ maximumLayerCompilerTotalTests 3 3 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 3 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 3 1 ≤ maximumLayerCompilerTestBound 3 3 1 := by native_decide

/-- compiler_p3_r6_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 6 0 + maximumLayerCompilerPrimeEnvelopeGap 3 6 0 = maximumLayerCompilerPrimeEnvelopeBound 3 6 0 ∧ maximumLayerCompilerTotalTests 3 6 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 6 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 6 0 ≤ maximumLayerCompilerTestBound 3 6 0 := by native_decide

/-- compiler_p3_r8_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 8 2 + maximumLayerCompilerPrimeEnvelopeGap 3 8 2 = maximumLayerCompilerPrimeEnvelopeBound 3 8 2 ∧ maximumLayerCompilerTotalTests 3 8 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 8 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 8 2 ≤ maximumLayerCompilerTestBound 3 8 2 := by native_decide

/-- compiler_p3_r11_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 11 1 + maximumLayerCompilerPrimeEnvelopeGap 3 11 1 = maximumLayerCompilerPrimeEnvelopeBound 3 11 1 ∧ maximumLayerCompilerTotalTests 3 11 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 11 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 11 1 ≤ maximumLayerCompilerTestBound 3 11 1 := by native_decide

/-- compiler_p3_r14_h0 -/
example : maximumLayerCompilerClosedBudgetBound 3 14 0 + maximumLayerCompilerPrimeEnvelopeGap 3 14 0 = maximumLayerCompilerPrimeEnvelopeBound 3 14 0 ∧ maximumLayerCompilerTotalTests 3 14 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 14 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 14 0 ≤ maximumLayerCompilerTestBound 3 14 0 := by native_decide

/-- compiler_p3_r16_h2 -/
example : maximumLayerCompilerClosedBudgetBound 3 16 2 + maximumLayerCompilerPrimeEnvelopeGap 3 16 2 = maximumLayerCompilerPrimeEnvelopeBound 3 16 2 ∧ maximumLayerCompilerTotalTests 3 16 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 16 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 16 2 ≤ maximumLayerCompilerTestBound 3 16 2 := by native_decide

/-- compiler_p3_r19_h1 -/
example : maximumLayerCompilerClosedBudgetBound 3 19 1 + maximumLayerCompilerPrimeEnvelopeGap 3 19 1 = maximumLayerCompilerPrimeEnvelopeBound 3 19 1 ∧ maximumLayerCompilerTotalTests 3 19 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 3 19 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 3 19 1 ≤ maximumLayerCompilerTestBound 3 19 1 := by native_decide

/-- compiler_p5_r2_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 2 0 + maximumLayerCompilerPrimeEnvelopeGap 5 2 0 = maximumLayerCompilerPrimeEnvelopeBound 5 2 0 ∧ maximumLayerCompilerTotalTests 5 2 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 2 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 2 0 ≤ maximumLayerCompilerTestBound 5 2 0 := by native_decide

/-- compiler_p5_r4_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 4 2 + maximumLayerCompilerPrimeEnvelopeGap 5 4 2 = maximumLayerCompilerPrimeEnvelopeBound 5 4 2 ∧ maximumLayerCompilerTotalTests 5 4 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 4 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 4 2 ≤ maximumLayerCompilerTestBound 5 4 2 := by native_decide

/-- compiler_p5_r7_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 7 1 + maximumLayerCompilerPrimeEnvelopeGap 5 7 1 = maximumLayerCompilerPrimeEnvelopeBound 5 7 1 ∧ maximumLayerCompilerTotalTests 5 7 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 7 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 7 1 ≤ maximumLayerCompilerTestBound 5 7 1 := by native_decide

/-- compiler_p5_r10_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 10 0 + maximumLayerCompilerPrimeEnvelopeGap 5 10 0 = maximumLayerCompilerPrimeEnvelopeBound 5 10 0 ∧ maximumLayerCompilerTotalTests 5 10 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 10 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 10 0 ≤ maximumLayerCompilerTestBound 5 10 0 := by native_decide

/-- compiler_p5_r12_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 12 2 + maximumLayerCompilerPrimeEnvelopeGap 5 12 2 = maximumLayerCompilerPrimeEnvelopeBound 5 12 2 ∧ maximumLayerCompilerTotalTests 5 12 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 12 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 12 2 ≤ maximumLayerCompilerTestBound 5 12 2 := by native_decide

/-- compiler_p5_r15_h1 -/
example : maximumLayerCompilerClosedBudgetBound 5 15 1 + maximumLayerCompilerPrimeEnvelopeGap 5 15 1 = maximumLayerCompilerPrimeEnvelopeBound 5 15 1 ∧ maximumLayerCompilerTotalTests 5 15 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 15 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 15 1 ≤ maximumLayerCompilerTestBound 5 15 1 := by native_decide

/-- compiler_p5_r18_h0 -/
example : maximumLayerCompilerClosedBudgetBound 5 18 0 + maximumLayerCompilerPrimeEnvelopeGap 5 18 0 = maximumLayerCompilerPrimeEnvelopeBound 5 18 0 ∧ maximumLayerCompilerTotalTests 5 18 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 18 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 18 0 ≤ maximumLayerCompilerTestBound 5 18 0 := by native_decide

/-- compiler_p5_r20_h2 -/
example : maximumLayerCompilerClosedBudgetBound 5 20 2 + maximumLayerCompilerPrimeEnvelopeGap 5 20 2 = maximumLayerCompilerPrimeEnvelopeBound 5 20 2 ∧ maximumLayerCompilerTotalTests 5 20 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 5 20 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 5 20 2 ≤ maximumLayerCompilerTestBound 5 20 2 := by native_decide

/-- compiler_p7_r3_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 3 1 + maximumLayerCompilerPrimeEnvelopeGap 7 3 1 = maximumLayerCompilerPrimeEnvelopeBound 7 3 1 ∧ maximumLayerCompilerTotalTests 7 3 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 3 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 3 1 ≤ maximumLayerCompilerTestBound 7 3 1 := by native_decide

/-- compiler_p7_r6_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 6 0 + maximumLayerCompilerPrimeEnvelopeGap 7 6 0 = maximumLayerCompilerPrimeEnvelopeBound 7 6 0 ∧ maximumLayerCompilerTotalTests 7 6 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 6 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 6 0 ≤ maximumLayerCompilerTestBound 7 6 0 := by native_decide

/-- compiler_p7_r8_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 8 2 + maximumLayerCompilerPrimeEnvelopeGap 7 8 2 = maximumLayerCompilerPrimeEnvelopeBound 7 8 2 ∧ maximumLayerCompilerTotalTests 7 8 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 8 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 8 2 ≤ maximumLayerCompilerTestBound 7 8 2 := by native_decide

/-- compiler_p7_r11_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 11 1 + maximumLayerCompilerPrimeEnvelopeGap 7 11 1 = maximumLayerCompilerPrimeEnvelopeBound 7 11 1 ∧ maximumLayerCompilerTotalTests 7 11 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 11 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 11 1 ≤ maximumLayerCompilerTestBound 7 11 1 := by native_decide

/-- compiler_p7_r14_h0 -/
example : maximumLayerCompilerClosedBudgetBound 7 14 0 + maximumLayerCompilerPrimeEnvelopeGap 7 14 0 = maximumLayerCompilerPrimeEnvelopeBound 7 14 0 ∧ maximumLayerCompilerTotalTests 7 14 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 14 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 14 0 ≤ maximumLayerCompilerTestBound 7 14 0 := by native_decide

/-- compiler_p7_r16_h2 -/
example : maximumLayerCompilerClosedBudgetBound 7 16 2 + maximumLayerCompilerPrimeEnvelopeGap 7 16 2 = maximumLayerCompilerPrimeEnvelopeBound 7 16 2 ∧ maximumLayerCompilerTotalTests 7 16 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 16 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 16 2 ≤ maximumLayerCompilerTestBound 7 16 2 := by native_decide

/-- compiler_p7_r19_h1 -/
example : maximumLayerCompilerClosedBudgetBound 7 19 1 + maximumLayerCompilerPrimeEnvelopeGap 7 19 1 = maximumLayerCompilerPrimeEnvelopeBound 7 19 1 ∧ maximumLayerCompilerTotalTests 7 19 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 7 19 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 7 19 1 ≤ maximumLayerCompilerTestBound 7 19 1 := by native_decide

/-- compiler_p11_r2_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 2 0 + maximumLayerCompilerPrimeEnvelopeGap 11 2 0 = maximumLayerCompilerPrimeEnvelopeBound 11 2 0 ∧ maximumLayerCompilerTotalTests 11 2 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 2 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 2 0 ≤ maximumLayerCompilerTestBound 11 2 0 := by native_decide

/-- compiler_p11_r4_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 4 2 + maximumLayerCompilerPrimeEnvelopeGap 11 4 2 = maximumLayerCompilerPrimeEnvelopeBound 11 4 2 ∧ maximumLayerCompilerTotalTests 11 4 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 4 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 4 2 ≤ maximumLayerCompilerTestBound 11 4 2 := by native_decide

/-- compiler_p11_r7_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 7 1 + maximumLayerCompilerPrimeEnvelopeGap 11 7 1 = maximumLayerCompilerPrimeEnvelopeBound 11 7 1 ∧ maximumLayerCompilerTotalTests 11 7 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 7 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 7 1 ≤ maximumLayerCompilerTestBound 11 7 1 := by native_decide

/-- compiler_p11_r10_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 10 0 + maximumLayerCompilerPrimeEnvelopeGap 11 10 0 = maximumLayerCompilerPrimeEnvelopeBound 11 10 0 ∧ maximumLayerCompilerTotalTests 11 10 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 10 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 10 0 ≤ maximumLayerCompilerTestBound 11 10 0 := by native_decide

/-- compiler_p11_r12_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 12 2 + maximumLayerCompilerPrimeEnvelopeGap 11 12 2 = maximumLayerCompilerPrimeEnvelopeBound 11 12 2 ∧ maximumLayerCompilerTotalTests 11 12 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 12 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 12 2 ≤ maximumLayerCompilerTestBound 11 12 2 := by native_decide

/-- compiler_p11_r15_h1 -/
example : maximumLayerCompilerClosedBudgetBound 11 15 1 + maximumLayerCompilerPrimeEnvelopeGap 11 15 1 = maximumLayerCompilerPrimeEnvelopeBound 11 15 1 ∧ maximumLayerCompilerTotalTests 11 15 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 15 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 15 1 ≤ maximumLayerCompilerTestBound 11 15 1 := by native_decide

/-- compiler_p11_r18_h0 -/
example : maximumLayerCompilerClosedBudgetBound 11 18 0 + maximumLayerCompilerPrimeEnvelopeGap 11 18 0 = maximumLayerCompilerPrimeEnvelopeBound 11 18 0 ∧ maximumLayerCompilerTotalTests 11 18 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 18 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 18 0 ≤ maximumLayerCompilerTestBound 11 18 0 := by native_decide

/-- compiler_p11_r20_h2 -/
example : maximumLayerCompilerClosedBudgetBound 11 20 2 + maximumLayerCompilerPrimeEnvelopeGap 11 20 2 = maximumLayerCompilerPrimeEnvelopeBound 11 20 2 ∧ maximumLayerCompilerTotalTests 11 20 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 11 20 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 11 20 2 ≤ maximumLayerCompilerTestBound 11 20 2 := by native_decide

/-- compiler_p13_r3_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 3 1 + maximumLayerCompilerPrimeEnvelopeGap 13 3 1 = maximumLayerCompilerPrimeEnvelopeBound 13 3 1 ∧ maximumLayerCompilerTotalTests 13 3 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 3 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 3 1 ≤ maximumLayerCompilerTestBound 13 3 1 := by native_decide

/-- compiler_p13_r6_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 6 0 + maximumLayerCompilerPrimeEnvelopeGap 13 6 0 = maximumLayerCompilerPrimeEnvelopeBound 13 6 0 ∧ maximumLayerCompilerTotalTests 13 6 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 6 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 6 0 ≤ maximumLayerCompilerTestBound 13 6 0 := by native_decide

/-- compiler_p13_r8_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 8 2 + maximumLayerCompilerPrimeEnvelopeGap 13 8 2 = maximumLayerCompilerPrimeEnvelopeBound 13 8 2 ∧ maximumLayerCompilerTotalTests 13 8 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 8 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 8 2 ≤ maximumLayerCompilerTestBound 13 8 2 := by native_decide

/-- compiler_p13_r11_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 11 1 + maximumLayerCompilerPrimeEnvelopeGap 13 11 1 = maximumLayerCompilerPrimeEnvelopeBound 13 11 1 ∧ maximumLayerCompilerTotalTests 13 11 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 11 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 11 1 ≤ maximumLayerCompilerTestBound 13 11 1 := by native_decide

/-- compiler_p13_r14_h0 -/
example : maximumLayerCompilerClosedBudgetBound 13 14 0 + maximumLayerCompilerPrimeEnvelopeGap 13 14 0 = maximumLayerCompilerPrimeEnvelopeBound 13 14 0 ∧ maximumLayerCompilerTotalTests 13 14 0 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 14 0 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 14 0 ≤ maximumLayerCompilerTestBound 13 14 0 := by native_decide

/-- compiler_p13_r16_h2 -/
example : maximumLayerCompilerClosedBudgetBound 13 16 2 + maximumLayerCompilerPrimeEnvelopeGap 13 16 2 = maximumLayerCompilerPrimeEnvelopeBound 13 16 2 ∧ maximumLayerCompilerTotalTests 13 16 2 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 16 2 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 16 2 ≤ maximumLayerCompilerTestBound 13 16 2 := by native_decide

/-- compiler_p13_r19_h1 -/
example : maximumLayerCompilerClosedBudgetBound 13 19 1 + maximumLayerCompilerPrimeEnvelopeGap 13 19 1 = maximumLayerCompilerPrimeEnvelopeBound 13 19 1 ∧ maximumLayerCompilerTotalTests 13 19 1 ≤ maximumLayerCompilerPrimeEnvelopeBound 13 19 1 ∧ maximumLayerCompilerPrimeEnvelopeBound 13 19 1 ≤ maximumLayerCompilerTestBound 13 19 1 := by native_decide

end KomorebiPadic
