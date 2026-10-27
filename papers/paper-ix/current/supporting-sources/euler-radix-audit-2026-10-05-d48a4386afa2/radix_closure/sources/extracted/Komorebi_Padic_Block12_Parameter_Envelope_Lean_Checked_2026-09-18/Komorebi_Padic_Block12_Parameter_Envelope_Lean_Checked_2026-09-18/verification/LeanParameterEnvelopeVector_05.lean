import KomorebiPadic

namespace KomorebiPadic

example : coarseK 0 6 = 0 ∧
    quotientSearchBound 3 0 6 = 1 ∧
    coarseRadixDepth 3 0 6 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 0 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 0 6 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 0 6 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 0 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 0 6 ≤ maximumLayerCompilerRawPrecisionBound 3 0 := by
  native_decide

example : coarseK 1 1 = 0 ∧
    quotientSearchBound 3 1 1 = 1 ∧
    coarseRadixDepth 3 1 1 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 1 1) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 1 1 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 1 1 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 1 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 1 1 ≤ maximumLayerCompilerRawPrecisionBound 3 1 := by
  native_decide

example : coarseK 2 3 = 0 ∧
    quotientSearchBound 3 2 3 = 1 ∧
    coarseRadixDepth 3 2 3 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 2 3) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 2 3 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 2 3 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 2 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 2 3 ≤ maximumLayerCompilerRawPrecisionBound 3 2 := by
  native_decide

example : coarseK 2 6 = 0 ∧
    quotientSearchBound 3 2 6 = 1 ∧
    coarseRadixDepth 3 2 6 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 2 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 2 6 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 2 6 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 2 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 2 6 ≤ maximumLayerCompilerRawPrecisionBound 3 2 := by
  native_decide

example : coarseK 3 8 = 0 ∧
    quotientSearchBound 3 3 8 = 1 ∧
    coarseRadixDepth 3 3 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 3 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 3 8 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 3 8 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 3 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 3 8 ≤ maximumLayerCompilerRawPrecisionBound 3 3 := by
  native_decide

example : coarseK 3 31 = 0 ∧
    quotientSearchBound 3 3 31 = 1 ∧
    coarseRadixDepth 3 3 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 3 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 3 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 3 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 3 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 3 31 ≤ maximumLayerCompilerRawPrecisionBound 3 3 := by
  native_decide

example : coarseK 4 3 = 0 ∧
    quotientSearchBound 3 4 3 = 1 ∧
    coarseRadixDepth 3 4 3 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 4 3) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 4 3 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 4 3 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 4 3 ≤ maximumLayerCompilerRawPrecisionBound 3 4 := by
  native_decide

example : coarseK 4 13 = 0 ∧
    quotientSearchBound 3 4 13 = 1 ∧
    coarseRadixDepth 3 4 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 4 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 4 13 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 4 13 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 4 13 ≤ maximumLayerCompilerRawPrecisionBound 3 4 := by
  native_decide

example : coarseK 5 8 = 0 ∧
    quotientSearchBound 3 5 8 = 1 ∧
    coarseRadixDepth 3 5 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 5 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 5 8 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 5 8 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 5 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 5 8 ≤ maximumLayerCompilerRawPrecisionBound 3 5 := by
  native_decide

example : coarseK 5 31 = 0 ∧
    quotientSearchBound 3 5 31 = 1 ∧
    coarseRadixDepth 3 5 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 5 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 5 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 5 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 5 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 5 31 ≤ maximumLayerCompilerRawPrecisionBound 3 5 := by
  native_decide

example : coarseK 6 0 = 5 ∧
    quotientSearchBound 3 6 0 = 3 ∧
    coarseRadixDepth 3 6 0 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 6 0) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 6 0 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 6 0 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 6 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 6 0 ≤ maximumLayerCompilerRawPrecisionBound 3 6 := by
  native_decide

example : coarseK 6 3 = 1 ∧
    quotientSearchBound 3 6 3 = 1 ∧
    coarseRadixDepth 3 6 3 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 6 3) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 6 3 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 6 3 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 6 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 6 3 ≤ maximumLayerCompilerRawPrecisionBound 3 6 := by
  native_decide

example : coarseK 6 13 = 0 ∧
    quotientSearchBound 3 6 13 = 1 ∧
    coarseRadixDepth 3 6 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 6 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 6 13 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 6 13 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 6 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 6 13 ≤ maximumLayerCompilerRawPrecisionBound 3 6 := by
  native_decide

example : coarseK 7 5 = 1 ∧
    quotientSearchBound 3 7 5 = 1 ∧
    coarseRadixDepth 3 7 5 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 7 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 7 5 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 7 5 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 7 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 7 5 ≤ maximumLayerCompilerRawPrecisionBound 3 7 := by
  native_decide

example : coarseK 7 8 = 0 ∧
    quotientSearchBound 3 7 8 = 1 ∧
    coarseRadixDepth 3 7 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 7 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 7 8 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 7 8 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 7 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 7 8 ≤ maximumLayerCompilerRawPrecisionBound 3 7 := by
  native_decide

example : coarseK 7 31 = 0 ∧
    quotientSearchBound 3 7 31 = 1 ∧
    coarseRadixDepth 3 7 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 7 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 7 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 7 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 7 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 7 31 ≤ maximumLayerCompilerRawPrecisionBound 3 7 := by
  native_decide

example : coarseK 8 0 = 7 ∧
    quotientSearchBound 3 8 0 = 4 ∧
    coarseRadixDepth 3 8 0 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 8 0) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 8 0 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 8 0 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 8 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 8 0 ≤ maximumLayerCompilerRawPrecisionBound 3 8 := by
  native_decide

example : coarseK 8 10 = 0 ∧
    quotientSearchBound 3 8 10 = 1 ∧
    coarseRadixDepth 3 8 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 8 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 8 10 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 8 10 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 8 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 8 10 ≤ maximumLayerCompilerRawPrecisionBound 3 8 := by
  native_decide

example : coarseK 8 13 = 0 ∧
    quotientSearchBound 3 8 13 = 1 ∧
    coarseRadixDepth 3 8 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 8 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 8 13 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 8 13 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 8 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 8 13 ≤ maximumLayerCompilerRawPrecisionBound 3 8 := by
  native_decide

example : coarseK 9 5 = 1 ∧
    quotientSearchBound 3 9 5 = 1 ∧
    coarseRadixDepth 3 9 5 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 9 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 9 5 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 9 5 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 9 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 9 5 ≤ maximumLayerCompilerRawPrecisionBound 3 9 := by
  native_decide

example : coarseK 10 0 = 9 ∧
    quotientSearchBound 3 10 0 = 5 ∧
    coarseRadixDepth 3 10 0 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 10 0) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 10 0 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 10 0 = 16 ∧
    maximumLayerCompilerRawPrecisionBound 3 10 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 10 0 ≤ maximumLayerCompilerRawPrecisionBound 3 10 := by
  native_decide

example : coarseK 10 10 = 0 ∧
    quotientSearchBound 3 10 10 = 1 ∧
    coarseRadixDepth 3 10 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 10 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 10 10 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 10 10 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 10 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 10 10 ≤ maximumLayerCompilerRawPrecisionBound 3 10 := by
  native_decide

example : coarseK 11 2 = 3 ∧
    quotientSearchBound 3 11 2 = 2 ∧
    coarseRadixDepth 3 11 2 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 11 2) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 11 2 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 11 2 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 11 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 11 2 ≤ maximumLayerCompilerRawPrecisionBound 3 11 := by
  native_decide

example : coarseK 11 5 = 1 ∧
    quotientSearchBound 3 11 5 = 1 ∧
    coarseRadixDepth 3 11 5 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 11 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 11 5 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 11 5 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 11 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 11 5 ≤ maximumLayerCompilerRawPrecisionBound 3 11 := by
  native_decide

example : coarseK 12 7 = 1 ∧
    quotientSearchBound 3 12 7 = 1 ∧
    coarseRadixDepth 3 12 7 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 12 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 12 7 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 12 7 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 12 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 12 7 ≤ maximumLayerCompilerRawPrecisionBound 3 12 := by
  native_decide

example : coarseK 12 10 = 1 ∧
    quotientSearchBound 3 12 10 = 1 ∧
    coarseRadixDepth 3 12 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 12 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 12 10 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 12 10 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 12 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 12 10 ≤ maximumLayerCompilerRawPrecisionBound 3 12 := by
  native_decide

example : coarseK 13 2 = 4 ∧
    quotientSearchBound 3 13 2 = 3 ∧
    coarseRadixDepth 3 13 2 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 13 2) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 13 2 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 13 2 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 13 = 26 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 13 2 ≤ maximumLayerCompilerRawPrecisionBound 3 13 := by
  native_decide

example : coarseK 14 7 = 1 ∧
    quotientSearchBound 3 14 7 = 1 ∧
    coarseRadixDepth 3 14 7 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 14 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 14 7 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 14 7 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 14 = 26 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 14 7 ≤ maximumLayerCompilerRawPrecisionBound 3 14 := by
  native_decide

example : coarseK 14 17 = 0 ∧
    quotientSearchBound 3 14 17 = 1 ∧
    coarseRadixDepth 3 14 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 14 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 14 17 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 14 17 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 14 = 26 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 14 17 ≤ maximumLayerCompilerRawPrecisionBound 3 14 := by
  native_decide

example : coarseK 15 2 = 4 ∧
    quotientSearchBound 3 15 2 = 3 ∧
    coarseRadixDepth 3 15 2 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 15 2) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 15 2 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 15 2 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 15 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 15 2 ≤ maximumLayerCompilerRawPrecisionBound 3 15 := by
  native_decide

example : coarseK 16 4 = 3 ∧
    quotientSearchBound 3 16 4 = 2 ∧
    coarseRadixDepth 3 16 4 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 16 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 16 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 16 4 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 16 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 16 4 ≤ maximumLayerCompilerRawPrecisionBound 3 16 := by
  native_decide

example : coarseK 16 7 = 1 ∧
    quotientSearchBound 3 16 7 = 1 ∧
    coarseRadixDepth 3 16 7 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 16 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 16 7 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 16 7 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 16 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 16 7 ≤ maximumLayerCompilerRawPrecisionBound 3 16 := by
  native_decide

example : coarseK 16 17 = 0 ∧
    quotientSearchBound 3 16 17 = 1 ∧
    coarseRadixDepth 3 16 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 16 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 16 17 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 16 17 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 16 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 16 17 ≤ maximumLayerCompilerRawPrecisionBound 3 16 := by
  native_decide

example : coarseK 17 9 = 1 ∧
    quotientSearchBound 3 17 9 = 1 ∧
    coarseRadixDepth 3 17 9 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 17 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 17 9 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 17 9 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 17 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 17 9 ≤ maximumLayerCompilerRawPrecisionBound 3 17 := by
  native_decide

example : coarseK 18 4 = 3 ∧
    quotientSearchBound 3 18 4 = 2 ∧
    coarseRadixDepth 3 18 4 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 18 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 18 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 18 4 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 18 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 18 4 ≤ maximumLayerCompilerRawPrecisionBound 3 18 := by
  native_decide

example : coarseK 18 17 = 0 ∧
    quotientSearchBound 3 18 17 = 1 ∧
    coarseRadixDepth 3 18 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 18 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 18 17 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 18 17 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 18 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 18 17 ≤ maximumLayerCompilerRawPrecisionBound 3 18 := by
  native_decide

example : coarseK 19 9 = 1 ∧
    quotientSearchBound 3 19 9 = 1 ∧
    coarseRadixDepth 3 19 9 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 19 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 19 9 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 19 9 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 19 = 41 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 19 9 ≤ maximumLayerCompilerRawPrecisionBound 3 19 := by
  native_decide

example : coarseK 20 1 = 9 ∧
    quotientSearchBound 3 20 1 = 5 ∧
    coarseRadixDepth 3 20 1 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 20 1) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 20 1 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 20 1 = 16 ∧
    maximumLayerCompilerRawPrecisionBound 3 20 = 41 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 20 1 ≤ maximumLayerCompilerRawPrecisionBound 3 20 := by
  native_decide

example : coarseK 20 4 = 3 ∧
    quotientSearchBound 3 20 4 = 2 ∧
    coarseRadixDepth 3 20 4 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 20 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 20 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 20 4 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 20 = 41 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 20 4 ≤ maximumLayerCompilerRawPrecisionBound 3 20 := by
  native_decide

example : coarseK 21 6 = 2 ∧
    quotientSearchBound 3 21 6 = 2 ∧
    coarseRadixDepth 3 21 6 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 21 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 21 6 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 21 6 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 21 = 43 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 21 6 ≤ maximumLayerCompilerRawPrecisionBound 3 21 := by
  native_decide

example : coarseK 21 9 = 2 ∧
    quotientSearchBound 3 21 9 = 2 ∧
    coarseRadixDepth 3 21 9 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 21 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 21 9 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 21 9 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 21 = 43 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 21 9 ≤ maximumLayerCompilerRawPrecisionBound 3 21 := by
  native_decide

example : coarseK 22 1 = 10 ∧
    quotientSearchBound 3 22 1 = 6 ∧
    coarseRadixDepth 3 22 1 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 22 1) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 22 1 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 22 1 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 3 22 = 43 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 22 1 ≤ maximumLayerCompilerRawPrecisionBound 3 22 := by
  native_decide

example : coarseK 23 6 = 3 ∧
    quotientSearchBound 3 23 6 = 2 ∧
    coarseRadixDepth 3 23 6 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 23 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 23 6 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 23 6 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 23 = 45 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 23 6 ≤ maximumLayerCompilerRawPrecisionBound 3 23 := by
  native_decide

example : coarseK 24 1 = 11 ∧
    quotientSearchBound 3 24 1 = 6 ∧
    coarseRadixDepth 3 24 1 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 24 1) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 24 1 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 24 1 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 3 24 = 45 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 24 1 ≤ maximumLayerCompilerRawPrecisionBound 3 24 := by
  native_decide

example : coarseK 25 3 = 6 ∧
    quotientSearchBound 3 25 3 = 4 ∧
    coarseRadixDepth 3 25 3 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 25 3) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 25 3 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 25 3 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 25 = 59 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 25 3 ≤ maximumLayerCompilerRawPrecisionBound 3 25 := by
  native_decide

example : coarseK 25 6 = 3 ∧
    quotientSearchBound 3 25 6 = 2 ∧
    coarseRadixDepth 3 25 6 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 25 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 25 6 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 25 6 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 25 = 59 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 25 6 ≤ maximumLayerCompilerRawPrecisionBound 3 25 := by
  native_decide

example : coarseK 26 8 = 2 ∧
    quotientSearchBound 3 26 8 = 2 ∧
    coarseRadixDepth 3 26 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 26 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 26 8 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 26 8 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 26 = 59 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 26 8 ≤ maximumLayerCompilerRawPrecisionBound 3 26 := by
  native_decide

example : coarseK 26 31 = 0 ∧
    quotientSearchBound 3 26 31 = 1 ∧
    coarseRadixDepth 3 26 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 26 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 26 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 26 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 26 = 59 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 26 31 ≤ maximumLayerCompilerRawPrecisionBound 3 26 := by
  native_decide

example : coarseK 27 3 = 6 ∧
    quotientSearchBound 3 27 3 = 4 ∧
    coarseRadixDepth 3 27 3 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 27 3) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 27 3 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 27 3 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 27 = 61 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 27 3 ≤ maximumLayerCompilerRawPrecisionBound 3 27 := by
  native_decide

example : coarseK 27 13 = 1 ∧
    quotientSearchBound 3 27 13 = 1 ∧
    coarseRadixDepth 3 27 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 27 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 27 13 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 27 13 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 27 = 61 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 27 13 ≤ maximumLayerCompilerRawPrecisionBound 3 27 := by
  native_decide

example : coarseK 28 8 = 3 ∧
    quotientSearchBound 3 28 8 = 2 ∧
    coarseRadixDepth 3 28 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 28 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 28 8 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 28 8 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 28 = 61 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 28 8 ≤ maximumLayerCompilerRawPrecisionBound 3 28 := by
  native_decide

example : coarseK 28 31 = 0 ∧
    quotientSearchBound 3 28 31 = 1 ∧
    coarseRadixDepth 3 28 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 28 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 28 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 28 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 28 = 61 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 28 31 ≤ maximumLayerCompilerRawPrecisionBound 3 28 := by
  native_decide

example : coarseK 29 0 = 28 ∧
    quotientSearchBound 3 29 0 = 15 ∧
    coarseRadixDepth 3 29 0 = 4 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 29 0) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 29 0 = 63 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 29 0 = 63 ∧
    maximumLayerCompilerRawPrecisionBound 3 29 = 63 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 29 0 ≤ maximumLayerCompilerRawPrecisionBound 3 29 := by
  native_decide

example : coarseK 29 3 = 7 ∧
    quotientSearchBound 3 29 3 = 4 ∧
    coarseRadixDepth 3 29 3 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 29 3) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 29 3 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 29 3 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 29 = 63 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 29 3 ≤ maximumLayerCompilerRawPrecisionBound 3 29 := by
  native_decide

example : coarseK 29 13 = 2 ∧
    quotientSearchBound 3 29 13 = 2 ∧
    coarseRadixDepth 3 29 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 29 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 29 13 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 29 13 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 29 = 63 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 29 13 ≤ maximumLayerCompilerRawPrecisionBound 3 29 := by
  native_decide

example : coarseK 30 5 = 4 ∧
    quotientSearchBound 3 30 5 = 3 ∧
    coarseRadixDepth 3 30 5 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 30 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 30 5 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 30 5 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 30 = 63 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 30 5 ≤ maximumLayerCompilerRawPrecisionBound 3 30 := by
  native_decide

example : coarseK 30 8 = 3 ∧
    quotientSearchBound 3 30 8 = 2 ∧
    coarseRadixDepth 3 30 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 30 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 30 8 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 30 8 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 30 = 63 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 30 8 ≤ maximumLayerCompilerRawPrecisionBound 3 30 := by
  native_decide

example : coarseK 30 31 = 0 ∧
    quotientSearchBound 3 30 31 = 1 ∧
    coarseRadixDepth 3 30 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 30 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 30 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 30 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 30 = 63 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 30 31 ≤ maximumLayerCompilerRawPrecisionBound 3 30 := by
  native_decide

example : coarseK 31 0 = 30 ∧
    quotientSearchBound 3 31 0 = 16 ∧
    coarseRadixDepth 3 31 0 = 5 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 31 0) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 31 0 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 31 0 = 80 ∧
    maximumLayerCompilerRawPrecisionBound 3 31 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 31 0 ≤ maximumLayerCompilerRawPrecisionBound 3 31 := by
  native_decide

example : coarseK 31 10 = 2 ∧
    quotientSearchBound 3 31 10 = 2 ∧
    coarseRadixDepth 3 31 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 31 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 31 10 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 31 10 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 31 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 31 10 ≤ maximumLayerCompilerRawPrecisionBound 3 31 := by
  native_decide

example : coarseK 31 13 = 2 ∧
    quotientSearchBound 3 31 13 = 2 ∧
    coarseRadixDepth 3 31 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 31 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 31 13 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 31 13 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 31 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 31 13 ≤ maximumLayerCompilerRawPrecisionBound 3 31 := by
  native_decide

example : coarseK 32 5 = 5 ∧
    quotientSearchBound 3 32 5 = 3 ∧
    coarseRadixDepth 3 32 5 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 32 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 32 5 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 32 5 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 32 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 32 5 ≤ maximumLayerCompilerRawPrecisionBound 3 32 := by
  native_decide

example : coarseK 33 0 = 32 ∧
    quotientSearchBound 3 33 0 = 17 ∧
    coarseRadixDepth 3 33 0 = 5 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 33 0) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 33 0 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 33 0 = 82 ∧
    maximumLayerCompilerRawPrecisionBound 3 33 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 33 0 ≤ maximumLayerCompilerRawPrecisionBound 3 33 := by
  native_decide

example : coarseK 33 10 = 2 ∧
    quotientSearchBound 3 33 10 = 2 ∧
    coarseRadixDepth 3 33 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 33 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 33 10 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 33 10 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 33 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 33 10 ≤ maximumLayerCompilerRawPrecisionBound 3 33 := by
  native_decide

example : coarseK 34 2 = 11 ∧
    quotientSearchBound 3 34 2 = 6 ∧
    coarseRadixDepth 3 34 2 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 34 2) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 34 2 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 34 2 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 3 34 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 34 2 ≤ maximumLayerCompilerRawPrecisionBound 3 34 := by
  native_decide

example : coarseK 34 5 = 5 ∧
    quotientSearchBound 3 34 5 = 3 ∧
    coarseRadixDepth 3 34 5 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 34 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 34 5 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 34 5 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 34 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 34 5 ≤ maximumLayerCompilerRawPrecisionBound 3 34 := by
  native_decide

example : coarseK 35 7 = 4 ∧
    quotientSearchBound 3 35 7 = 3 ∧
    coarseRadixDepth 3 35 7 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 35 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 35 7 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 35 7 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 35 = 84 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 35 7 ≤ maximumLayerCompilerRawPrecisionBound 3 35 := by
  native_decide

example : coarseK 35 10 = 3 ∧
    quotientSearchBound 3 35 10 = 2 ∧
    coarseRadixDepth 3 35 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 35 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 35 10 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 35 10 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 35 = 84 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 35 10 ≤ maximumLayerCompilerRawPrecisionBound 3 35 := by
  native_decide

example : coarseK 36 2 = 11 ∧
    quotientSearchBound 3 36 2 = 6 ∧
    coarseRadixDepth 3 36 2 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 36 2) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 36 2 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 36 2 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 3 36 = 84 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 36 2 ≤ maximumLayerCompilerRawPrecisionBound 3 36 := by
  native_decide

example : coarseK 37 7 = 4 ∧
    quotientSearchBound 3 37 7 = 3 ∧
    coarseRadixDepth 3 37 7 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 37 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 37 7 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 37 7 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 37 = 104 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 37 7 ≤ maximumLayerCompilerRawPrecisionBound 3 37 := by
  native_decide

example : coarseK 37 17 = 2 ∧
    quotientSearchBound 3 37 17 = 2 ∧
    coarseRadixDepth 3 37 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 37 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 37 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 37 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 37 = 104 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 37 17 ≤ maximumLayerCompilerRawPrecisionBound 3 37 := by
  native_decide

example : coarseK 38 2 = 12 ∧
    quotientSearchBound 3 38 2 = 7 ∧
    coarseRadixDepth 3 38 2 = 2 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 38 2) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 38 2 = 26 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 38 2 = 26 ∧
    maximumLayerCompilerRawPrecisionBound 3 38 = 104 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 38 2 ≤ maximumLayerCompilerRawPrecisionBound 3 38 := by
  native_decide

example : coarseK 39 4 = 7 ∧
    quotientSearchBound 3 39 4 = 4 ∧
    coarseRadixDepth 3 39 4 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 39 4) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 39 4 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 39 4 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 39 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 39 4 ≤ maximumLayerCompilerRawPrecisionBound 3 39 := by
  native_decide

example : coarseK 39 7 = 4 ∧
    quotientSearchBound 3 39 7 = 3 ∧
    coarseRadixDepth 3 39 7 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 39 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 39 7 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 39 7 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 39 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 39 7 ≤ maximumLayerCompilerRawPrecisionBound 3 39 := by
  native_decide

example : coarseK 39 17 = 2 ∧
    quotientSearchBound 3 39 17 = 2 ∧
    coarseRadixDepth 3 39 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 39 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 39 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 39 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 39 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 39 17 ≤ maximumLayerCompilerRawPrecisionBound 3 39 := by
  native_decide

example : coarseK 40 9 = 3 ∧
    quotientSearchBound 3 40 9 = 2 ∧
    coarseRadixDepth 3 40 9 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 40 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 40 9 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 40 9 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 40 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 40 9 ≤ maximumLayerCompilerRawPrecisionBound 3 40 := by
  native_decide

example : coarseK 41 4 = 8 ∧
    quotientSearchBound 3 41 4 = 5 ∧
    coarseRadixDepth 3 41 4 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 41 4) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 41 4 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 41 4 = 16 ∧
    maximumLayerCompilerRawPrecisionBound 3 41 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 41 4 ≤ maximumLayerCompilerRawPrecisionBound 3 41 := by
  native_decide

example : coarseK 41 17 = 2 ∧
    quotientSearchBound 3 41 17 = 2 ∧
    coarseRadixDepth 3 41 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 41 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 41 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 41 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 41 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 41 17 ≤ maximumLayerCompilerRawPrecisionBound 3 41 := by
  native_decide

example : coarseK 42 9 = 4 ∧
    quotientSearchBound 3 42 9 = 3 ∧
    coarseRadixDepth 3 42 9 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 42 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 42 9 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 42 9 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 42 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 42 9 ≤ maximumLayerCompilerRawPrecisionBound 3 42 := by
  native_decide

example : coarseK 43 1 = 21 ∧
    quotientSearchBound 3 43 1 = 11 ∧
    coarseRadixDepth 3 43 1 = 3 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 43 1) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 43 1 = 43 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 43 1 = 43 ∧
    maximumLayerCompilerRawPrecisionBound 3 43 = 131 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 43 1 ≤ maximumLayerCompilerRawPrecisionBound 3 43 := by
  native_decide

example : coarseK 43 4 = 8 ∧
    quotientSearchBound 3 43 4 = 5 ∧
    coarseRadixDepth 3 43 4 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 43 4) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 43 4 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 43 4 = 16 ∧
    maximumLayerCompilerRawPrecisionBound 3 43 = 131 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 43 4 ≤ maximumLayerCompilerRawPrecisionBound 3 43 := by
  native_decide

example : coarseK 44 6 = 6 ∧
    quotientSearchBound 3 44 6 = 4 ∧
    coarseRadixDepth 3 44 6 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 44 6) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 44 6 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 44 6 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 44 = 131 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 44 6 ≤ maximumLayerCompilerRawPrecisionBound 3 44 := by
  native_decide

example : coarseK 44 9 = 4 ∧
    quotientSearchBound 3 44 9 = 3 ∧
    coarseRadixDepth 3 44 9 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 44 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 44 9 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 44 9 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 44 = 131 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 44 9 ≤ maximumLayerCompilerRawPrecisionBound 3 44 := by
  native_decide

example : coarseK 45 1 = 22 ∧
    quotientSearchBound 3 45 1 = 12 ∧
    coarseRadixDepth 3 45 1 = 3 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 45 1) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 45 1 = 45 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 45 1 = 45 ∧
    maximumLayerCompilerRawPrecisionBound 3 45 = 133 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 45 1 ≤ maximumLayerCompilerRawPrecisionBound 3 45 := by
  native_decide

example : coarseK 46 6 = 6 ∧
    quotientSearchBound 3 46 6 = 4 ∧
    coarseRadixDepth 3 46 6 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 46 6) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 46 6 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 46 6 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 46 = 133 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 46 6 ≤ maximumLayerCompilerRawPrecisionBound 3 46 := by
  native_decide

example : coarseK 47 1 = 23 ∧
    quotientSearchBound 3 47 1 = 12 ∧
    coarseRadixDepth 3 47 1 = 3 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 47 1) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 47 1 = 45 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 47 1 = 45 ∧
    maximumLayerCompilerRawPrecisionBound 3 47 = 135 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 47 1 ≤ maximumLayerCompilerRawPrecisionBound 3 47 := by
  native_decide

example : coarseK 48 3 = 11 ∧
    quotientSearchBound 3 48 3 = 6 ∧
    coarseRadixDepth 3 48 3 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 48 3) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 48 3 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 48 3 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 3 48 = 135 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 48 3 ≤ maximumLayerCompilerRawPrecisionBound 3 48 := by
  native_decide

example : coarseK 48 6 = 6 ∧
    quotientSearchBound 3 48 6 = 4 ∧
    coarseRadixDepth 3 48 6 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 48 6) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 48 6 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 48 6 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 48 = 135 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 48 6 ≤ maximumLayerCompilerRawPrecisionBound 3 48 := by
  native_decide

example : coarseK 49 8 = 5 ∧
    quotientSearchBound 3 49 8 = 3 ∧
    coarseRadixDepth 3 49 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 49 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 49 8 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 49 8 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 49 = 161 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 49 8 ≤ maximumLayerCompilerRawPrecisionBound 3 49 := by
  native_decide

example : coarseK 49 31 = 1 ∧
    quotientSearchBound 3 49 31 = 1 ∧
    coarseRadixDepth 3 49 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 49 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 49 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 49 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 49 = 161 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 49 31 ≤ maximumLayerCompilerRawPrecisionBound 3 49 := by
  native_decide

example : coarseK 50 3 = 12 ∧
    quotientSearchBound 3 50 3 = 7 ∧
    coarseRadixDepth 3 50 3 = 2 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 50 3) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 50 3 = 26 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 50 3 = 26 ∧
    maximumLayerCompilerRawPrecisionBound 3 50 = 161 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 50 3 ≤ maximumLayerCompilerRawPrecisionBound 3 50 := by
  native_decide

example : coarseK 50 13 = 3 ∧
    quotientSearchBound 3 50 13 = 2 ∧
    coarseRadixDepth 3 50 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 50 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 50 13 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 50 13 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 50 = 161 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 50 13 ≤ maximumLayerCompilerRawPrecisionBound 3 50 := by
  native_decide

example : coarseK 51 8 = 5 ∧
    quotientSearchBound 3 51 8 = 3 ∧
    coarseRadixDepth 3 51 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 51 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 51 8 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 51 8 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 51 = 163 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 51 8 ≤ maximumLayerCompilerRawPrecisionBound 3 51 := by
  native_decide

example : coarseK 51 31 = 1 ∧
    quotientSearchBound 3 51 31 = 1 ∧
    coarseRadixDepth 3 51 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 51 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 51 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 51 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 51 = 163 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 51 31 ≤ maximumLayerCompilerRawPrecisionBound 3 51 := by
  native_decide

example : coarseK 52 0 = 51 ∧
    quotientSearchBound 3 52 0 = 26 ∧
    coarseRadixDepth 3 52 0 = 8 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 52 0) = 8 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 52 0 = 163 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 52 0 = 163 ∧
    maximumLayerCompilerRawPrecisionBound 3 52 = 163 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 52 0 ≤ maximumLayerCompilerRawPrecisionBound 3 52 := by
  native_decide

example : coarseK 52 3 = 12 ∧
    quotientSearchBound 3 52 3 = 7 ∧
    coarseRadixDepth 3 52 3 = 2 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 52 3) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 52 3 = 26 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 52 3 = 26 ∧
    maximumLayerCompilerRawPrecisionBound 3 52 = 163 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 52 3 ≤ maximumLayerCompilerRawPrecisionBound 3 52 := by
  native_decide

example : coarseK 52 13 = 3 ∧
    quotientSearchBound 3 52 13 = 2 ∧
    coarseRadixDepth 3 52 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 52 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 52 13 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 52 13 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 52 = 163 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 52 13 ≤ maximumLayerCompilerRawPrecisionBound 3 52 := by
  native_decide

example : coarseK 53 5 = 8 ∧
    quotientSearchBound 3 53 5 = 5 ∧
    coarseRadixDepth 3 53 5 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 53 5) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 53 5 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 53 5 = 16 ∧
    maximumLayerCompilerRawPrecisionBound 3 53 = 165 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 53 5 ≤ maximumLayerCompilerRawPrecisionBound 3 53 := by
  native_decide

example : coarseK 53 8 = 5 ∧
    quotientSearchBound 3 53 8 = 3 ∧
    coarseRadixDepth 3 53 8 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 53 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 53 8 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 53 8 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 53 = 165 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 53 8 ≤ maximumLayerCompilerRawPrecisionBound 3 53 := by
  native_decide

example : coarseK 53 31 = 1 ∧
    quotientSearchBound 3 53 31 = 1 ∧
    coarseRadixDepth 3 53 31 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 53 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 53 31 = 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 53 31 = 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 53 = 165 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 53 31 ≤ maximumLayerCompilerRawPrecisionBound 3 53 := by
  native_decide

example : coarseK 54 0 = 53 ∧
    quotientSearchBound 3 54 0 = 27 ∧
    coarseRadixDepth 3 54 0 = 8 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 54 0) = 8 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 54 0 = 165 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 54 0 = 165 ∧
    maximumLayerCompilerRawPrecisionBound 3 54 = 165 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 54 0 ≤ maximumLayerCompilerRawPrecisionBound 3 54 := by
  native_decide

example : coarseK 54 10 = 4 ∧
    quotientSearchBound 3 54 10 = 3 ∧
    coarseRadixDepth 3 54 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 54 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 54 10 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 54 10 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 54 = 165 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 54 10 ≤ maximumLayerCompilerRawPrecisionBound 3 54 := by
  native_decide

example : coarseK 54 13 = 3 ∧
    quotientSearchBound 3 54 13 = 2 ∧
    coarseRadixDepth 3 54 13 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 54 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 54 13 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 54 13 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 54 = 165 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 54 13 ≤ maximumLayerCompilerRawPrecisionBound 3 54 := by
  native_decide

example : coarseK 55 5 = 9 ∧
    quotientSearchBound 3 55 5 = 5 ∧
    coarseRadixDepth 3 55 5 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 55 5) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 55 5 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 55 5 = 16 ∧
    maximumLayerCompilerRawPrecisionBound 3 55 = 194 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 55 5 ≤ maximumLayerCompilerRawPrecisionBound 3 55 := by
  native_decide

example : coarseK 56 0 = 55 ∧
    quotientSearchBound 3 56 0 = 28 ∧
    coarseRadixDepth 3 56 0 = 9 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 56 0) = 9 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 56 0 = 194 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 56 0 = 194 ∧
    maximumLayerCompilerRawPrecisionBound 3 56 = 194 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 56 0 ≤ maximumLayerCompilerRawPrecisionBound 3 56 := by
  native_decide

example : coarseK 56 10 = 5 ∧
    quotientSearchBound 3 56 10 = 3 ∧
    coarseRadixDepth 3 56 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 56 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 56 10 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 56 10 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 56 = 194 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 56 10 ≤ maximumLayerCompilerRawPrecisionBound 3 56 := by
  native_decide

example : coarseK 57 2 = 18 ∧
    quotientSearchBound 3 57 2 = 10 ∧
    coarseRadixDepth 3 57 2 = 3 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 57 2) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 57 2 = 41 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 57 2 = 41 ∧
    maximumLayerCompilerRawPrecisionBound 3 57 = 196 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 57 2 ≤ maximumLayerCompilerRawPrecisionBound 3 57 := by
  native_decide

example : coarseK 57 5 = 9 ∧
    quotientSearchBound 3 57 5 = 5 ∧
    coarseRadixDepth 3 57 5 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 57 5) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 57 5 = 16 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 57 5 = 16 ∧
    maximumLayerCompilerRawPrecisionBound 3 57 = 196 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 57 5 ≤ maximumLayerCompilerRawPrecisionBound 3 57 := by
  native_decide

example : coarseK 58 7 = 7 ∧
    quotientSearchBound 3 58 7 = 4 ∧
    coarseRadixDepth 3 58 7 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 58 7) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 58 7 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 58 7 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 58 = 196 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 58 7 ≤ maximumLayerCompilerRawPrecisionBound 3 58 := by
  native_decide

example : coarseK 58 10 = 5 ∧
    quotientSearchBound 3 58 10 = 3 ∧
    coarseRadixDepth 3 58 10 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 58 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 58 10 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 58 10 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 3 58 = 196 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 58 10 ≤ maximumLayerCompilerRawPrecisionBound 3 58 := by
  native_decide

example : coarseK 59 2 = 19 ∧
    quotientSearchBound 3 59 2 = 10 ∧
    coarseRadixDepth 3 59 2 = 3 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 59 2) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 59 2 = 41 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 59 2 = 41 ∧
    maximumLayerCompilerRawPrecisionBound 3 59 = 198 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 59 2 ≤ maximumLayerCompilerRawPrecisionBound 3 59 := by
  native_decide

example : coarseK 60 7 = 7 ∧
    quotientSearchBound 3 60 7 = 4 ∧
    coarseRadixDepth 3 60 7 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 60 7) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 60 7 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 60 7 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 60 = 198 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 60 7 ≤ maximumLayerCompilerRawPrecisionBound 3 60 := by
  native_decide

example : coarseK 60 17 = 3 ∧
    quotientSearchBound 3 60 17 = 2 ∧
    coarseRadixDepth 3 60 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 60 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 60 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 60 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 60 = 198 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 60 17 ≤ maximumLayerCompilerRawPrecisionBound 3 60 := by
  native_decide

example : coarseK 61 2 = 20 ∧
    quotientSearchBound 3 61 2 = 11 ∧
    coarseRadixDepth 3 61 2 = 3 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 61 2) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 61 2 = 43 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 61 2 = 43 ∧
    maximumLayerCompilerRawPrecisionBound 3 61 = 230 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 61 2 ≤ maximumLayerCompilerRawPrecisionBound 3 61 := by
  native_decide

example : coarseK 62 4 = 12 ∧
    quotientSearchBound 3 62 4 = 7 ∧
    coarseRadixDepth 3 62 4 = 2 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 62 4) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 62 4 = 26 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 62 4 = 26 ∧
    maximumLayerCompilerRawPrecisionBound 3 62 = 230 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 62 4 ≤ maximumLayerCompilerRawPrecisionBound 3 62 := by
  native_decide

example : coarseK 62 7 = 7 ∧
    quotientSearchBound 3 62 7 = 4 ∧
    coarseRadixDepth 3 62 7 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 62 7) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 62 7 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 62 7 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 62 = 230 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 62 7 ≤ maximumLayerCompilerRawPrecisionBound 3 62 := by
  native_decide

example : coarseK 62 17 = 3 ∧
    quotientSearchBound 3 62 17 = 2 ∧
    coarseRadixDepth 3 62 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 62 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 62 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 62 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 62 = 230 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 62 17 ≤ maximumLayerCompilerRawPrecisionBound 3 62 := by
  native_decide

example : coarseK 63 9 = 6 ∧
    quotientSearchBound 3 63 9 = 4 ∧
    coarseRadixDepth 3 63 9 = 1 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 63 9) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 63 9 = 14 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 63 9 = 14 ∧
    maximumLayerCompilerRawPrecisionBound 3 63 = 232 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 63 9 ≤ maximumLayerCompilerRawPrecisionBound 3 63 := by
  native_decide

example : coarseK 64 4 = 12 ∧
    quotientSearchBound 3 64 4 = 7 ∧
    coarseRadixDepth 3 64 4 = 2 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 64 4) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 64 4 = 26 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 64 4 = 26 ∧
    maximumLayerCompilerRawPrecisionBound 3 64 = 232 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 64 4 ≤ maximumLayerCompilerRawPrecisionBound 3 64 := by
  native_decide

example : coarseK 64 17 = 3 ∧
    quotientSearchBound 3 64 17 = 2 ∧
    coarseRadixDepth 3 64 17 = 0 ∧
    lastRadixBlockQuotient 3 (quotientSearchBound 3 64 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 3 64 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 64 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 3 64 = 232 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 64 17 ≤ maximumLayerCompilerRawPrecisionBound 3 64 := by
  native_decide

end KomorebiPadic
