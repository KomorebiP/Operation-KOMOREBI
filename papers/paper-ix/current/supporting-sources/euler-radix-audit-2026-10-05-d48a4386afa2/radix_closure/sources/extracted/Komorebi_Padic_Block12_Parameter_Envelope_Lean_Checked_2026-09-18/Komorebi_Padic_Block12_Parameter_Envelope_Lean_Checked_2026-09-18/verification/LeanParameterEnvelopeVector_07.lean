import KomorebiPadic

namespace KomorebiPadic

example : coarseK 41 31 = 1 ∧
    quotientSearchBound 4 41 31 = 1 ∧
    coarseRadixDepth 4 41 31 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 41 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 41 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 41 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 4 41 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 41 31 ≤ maximumLayerCompilerRawPrecisionBound 4 41 := by
  native_decide

example : coarseK 42 0 = 41 ∧
    quotientSearchBound 4 42 0 = 14 ∧
    coarseRadixDepth 4 42 0 = 3 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 42 0) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 42 0 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 42 0 = 56 ∧
    maximumLayerCompilerRawPrecisionBound 4 42 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 42 0 ≤ maximumLayerCompilerRawPrecisionBound 4 42 := by
  native_decide

example : coarseK 42 10 = 3 ∧
    quotientSearchBound 4 42 10 = 2 ∧
    coarseRadixDepth 4 42 10 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 42 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 42 10 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 42 10 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 42 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 42 10 ≤ maximumLayerCompilerRawPrecisionBound 4 42 := by
  native_decide

example : coarseK 42 13 = 2 ∧
    quotientSearchBound 4 42 13 = 1 ∧
    coarseRadixDepth 4 42 13 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 42 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 42 13 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 42 13 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 4 42 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 42 13 ≤ maximumLayerCompilerRawPrecisionBound 4 42 := by
  native_decide

example : coarseK 43 5 = 7 ∧
    quotientSearchBound 4 43 5 = 3 ∧
    coarseRadixDepth 4 43 5 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 43 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 43 5 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 43 5 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 43 = 58 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 43 5 ≤ maximumLayerCompilerRawPrecisionBound 4 43 := by
  native_decide

example : coarseK 44 0 = 43 ∧
    quotientSearchBound 4 44 0 = 15 ∧
    coarseRadixDepth 4 44 0 = 3 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 44 0) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 44 0 = 58 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 44 0 = 58 ∧
    maximumLayerCompilerRawPrecisionBound 4 44 = 58 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 44 0 ≤ maximumLayerCompilerRawPrecisionBound 4 44 := by
  native_decide

example : coarseK 44 10 = 3 ∧
    quotientSearchBound 4 44 10 = 2 ∧
    coarseRadixDepth 4 44 10 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 44 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 44 10 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 44 10 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 44 = 58 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 44 10 ≤ maximumLayerCompilerRawPrecisionBound 4 44 := by
  native_decide

example : coarseK 45 2 = 14 ∧
    quotientSearchBound 4 45 2 = 5 ∧
    coarseRadixDepth 4 45 2 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 45 2) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 45 2 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 45 2 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 4 45 = 58 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 45 2 ≤ maximumLayerCompilerRawPrecisionBound 4 45 := by
  native_decide

example : coarseK 45 5 = 7 ∧
    quotientSearchBound 4 45 5 = 3 ∧
    coarseRadixDepth 4 45 5 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 45 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 45 5 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 45 5 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 45 = 58 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 45 5 ≤ maximumLayerCompilerRawPrecisionBound 4 45 := by
  native_decide

example : coarseK 46 7 = 5 ∧
    quotientSearchBound 4 46 7 = 2 ∧
    coarseRadixDepth 4 46 7 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 46 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 46 7 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 46 7 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 46 = 60 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 46 7 ≤ maximumLayerCompilerRawPrecisionBound 4 46 := by
  native_decide

example : coarseK 46 10 = 4 ∧
    quotientSearchBound 4 46 10 = 2 ∧
    coarseRadixDepth 4 46 10 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 46 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 46 10 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 46 10 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 46 = 60 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 46 10 ≤ maximumLayerCompilerRawPrecisionBound 4 46 := by
  native_decide

example : coarseK 47 2 = 15 ∧
    quotientSearchBound 4 47 2 = 6 ∧
    coarseRadixDepth 4 47 2 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 47 2) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 47 2 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 47 2 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 4 47 = 60 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 47 2 ≤ maximumLayerCompilerRawPrecisionBound 4 47 := by
  native_decide

example : coarseK 48 7 = 5 ∧
    quotientSearchBound 4 48 7 = 2 ∧
    coarseRadixDepth 4 48 7 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 48 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 48 7 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 48 7 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 48 = 60 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 48 7 ≤ maximumLayerCompilerRawPrecisionBound 4 48 := by
  native_decide

example : coarseK 48 17 = 2 ∧
    quotientSearchBound 4 48 17 = 1 ∧
    coarseRadixDepth 4 48 17 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 48 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 48 17 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 48 17 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 4 48 = 60 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 48 17 ≤ maximumLayerCompilerRawPrecisionBound 4 48 := by
  native_decide

example : coarseK 49 2 = 16 ∧
    quotientSearchBound 4 49 2 = 6 ∧
    coarseRadixDepth 4 49 2 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 49 2) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 49 2 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 49 2 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 4 49 = 78 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 49 2 ≤ maximumLayerCompilerRawPrecisionBound 4 49 := by
  native_decide

example : coarseK 50 4 = 9 ∧
    quotientSearchBound 4 50 4 = 4 ∧
    coarseRadixDepth 4 50 4 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 50 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 50 4 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 50 4 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 50 = 78 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 50 4 ≤ maximumLayerCompilerRawPrecisionBound 4 50 := by
  native_decide

example : coarseK 50 7 = 6 ∧
    quotientSearchBound 4 50 7 = 3 ∧
    coarseRadixDepth 4 50 7 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 50 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 50 7 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 50 7 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 50 = 78 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 50 7 ≤ maximumLayerCompilerRawPrecisionBound 4 50 := by
  native_decide

example : coarseK 50 17 = 2 ∧
    quotientSearchBound 4 50 17 = 1 ∧
    coarseRadixDepth 4 50 17 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 50 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 50 17 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 50 17 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 4 50 = 78 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 50 17 ≤ maximumLayerCompilerRawPrecisionBound 4 50 := by
  native_decide

example : coarseK 51 9 = 5 ∧
    quotientSearchBound 4 51 9 = 2 ∧
    coarseRadixDepth 4 51 9 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 51 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 51 9 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 51 9 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 51 = 78 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 51 9 ≤ maximumLayerCompilerRawPrecisionBound 4 51 := by
  native_decide

example : coarseK 52 4 = 10 ∧
    quotientSearchBound 4 52 4 = 4 ∧
    coarseRadixDepth 4 52 4 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 52 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 52 4 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 52 4 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 52 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 52 4 ≤ maximumLayerCompilerRawPrecisionBound 4 52 := by
  native_decide

example : coarseK 52 17 = 2 ∧
    quotientSearchBound 4 52 17 = 1 ∧
    coarseRadixDepth 4 52 17 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 52 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 52 17 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 52 17 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 4 52 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 52 17 ≤ maximumLayerCompilerRawPrecisionBound 4 52 := by
  native_decide

example : coarseK 53 9 = 5 ∧
    quotientSearchBound 4 53 9 = 2 ∧
    coarseRadixDepth 4 53 9 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 53 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 53 9 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 53 9 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 53 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 53 9 ≤ maximumLayerCompilerRawPrecisionBound 4 53 := by
  native_decide

example : coarseK 54 1 = 26 ∧
    quotientSearchBound 4 54 1 = 9 ∧
    coarseRadixDepth 4 54 1 = 2 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 54 1) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 54 1 = 34 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 54 1 = 34 ∧
    maximumLayerCompilerRawPrecisionBound 4 54 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 54 1 ≤ maximumLayerCompilerRawPrecisionBound 4 54 := by
  native_decide

example : coarseK 54 4 = 10 ∧
    quotientSearchBound 4 54 4 = 4 ∧
    coarseRadixDepth 4 54 4 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 54 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 54 4 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 54 4 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 54 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 54 4 ≤ maximumLayerCompilerRawPrecisionBound 4 54 := by
  native_decide

example : coarseK 55 6 = 7 ∧
    quotientSearchBound 4 55 6 = 3 ∧
    coarseRadixDepth 4 55 6 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 55 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 55 6 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 55 6 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 55 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 55 6 ≤ maximumLayerCompilerRawPrecisionBound 4 55 := by
  native_decide

example : coarseK 55 9 = 5 ∧
    quotientSearchBound 4 55 9 = 2 ∧
    coarseRadixDepth 4 55 9 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 55 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 55 9 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 55 9 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 55 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 55 9 ≤ maximumLayerCompilerRawPrecisionBound 4 55 := by
  native_decide

example : coarseK 56 1 = 27 ∧
    quotientSearchBound 4 56 1 = 10 ∧
    coarseRadixDepth 4 56 1 = 2 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 56 1) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 56 1 = 36 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 56 1 = 36 ∧
    maximumLayerCompilerRawPrecisionBound 4 56 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 56 1 ≤ maximumLayerCompilerRawPrecisionBound 4 56 := by
  native_decide

example : coarseK 57 6 = 8 ∧
    quotientSearchBound 4 57 6 = 3 ∧
    coarseRadixDepth 4 57 6 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 57 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 57 6 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 57 6 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 57 = 82 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 57 6 ≤ maximumLayerCompilerRawPrecisionBound 4 57 := by
  native_decide

example : coarseK 58 1 = 28 ∧
    quotientSearchBound 4 58 1 = 10 ∧
    coarseRadixDepth 4 58 1 = 2 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 58 1) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 58 1 = 36 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 58 1 = 36 ∧
    maximumLayerCompilerRawPrecisionBound 4 58 = 84 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 58 1 ≤ maximumLayerCompilerRawPrecisionBound 4 58 := by
  native_decide

example : coarseK 59 3 = 14 ∧
    quotientSearchBound 4 59 3 = 5 ∧
    coarseRadixDepth 4 59 3 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 59 3) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 59 3 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 59 3 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 4 59 = 84 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 59 3 ≤ maximumLayerCompilerRawPrecisionBound 4 59 := by
  native_decide

example : coarseK 59 6 = 8 ∧
    quotientSearchBound 4 59 6 = 3 ∧
    coarseRadixDepth 4 59 6 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 59 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 59 6 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 59 6 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 59 = 84 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 59 6 ≤ maximumLayerCompilerRawPrecisionBound 4 59 := by
  native_decide

example : coarseK 60 8 = 6 ∧
    quotientSearchBound 4 60 8 = 3 ∧
    coarseRadixDepth 4 60 8 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 60 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 60 8 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 60 8 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 60 = 84 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 60 8 ≤ maximumLayerCompilerRawPrecisionBound 4 60 := by
  native_decide

example : coarseK 60 31 = 1 ∧
    quotientSearchBound 4 60 31 = 1 ∧
    coarseRadixDepth 4 60 31 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 60 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 60 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 60 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 4 60 = 84 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 60 31 ≤ maximumLayerCompilerRawPrecisionBound 4 60 := by
  native_decide

example : coarseK 61 3 = 15 ∧
    quotientSearchBound 4 61 3 = 6 ∧
    coarseRadixDepth 4 61 3 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 61 3) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 61 3 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 61 3 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 4 61 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 61 3 ≤ maximumLayerCompilerRawPrecisionBound 4 61 := by
  native_decide

example : coarseK 61 13 = 4 ∧
    quotientSearchBound 4 61 13 = 2 ∧
    coarseRadixDepth 4 61 13 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 61 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 61 13 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 61 13 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 61 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 61 13 ≤ maximumLayerCompilerRawPrecisionBound 4 61 := by
  native_decide

example : coarseK 62 8 = 6 ∧
    quotientSearchBound 4 62 8 = 3 ∧
    coarseRadixDepth 4 62 8 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 62 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 62 8 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 62 8 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 62 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 62 8 ≤ maximumLayerCompilerRawPrecisionBound 4 62 := by
  native_decide

example : coarseK 62 31 = 1 ∧
    quotientSearchBound 4 62 31 = 1 ∧
    coarseRadixDepth 4 62 31 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 62 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 62 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 62 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 4 62 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 62 31 ≤ maximumLayerCompilerRawPrecisionBound 4 62 := by
  native_decide

example : coarseK 63 0 = 62 ∧
    quotientSearchBound 4 63 0 = 21 ∧
    coarseRadixDepth 4 63 0 = 5 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 63 0) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 63 0 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 63 0 = 106 ∧
    maximumLayerCompilerRawPrecisionBound 4 63 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 63 0 ≤ maximumLayerCompilerRawPrecisionBound 4 63 := by
  native_decide

example : coarseK 63 3 = 15 ∧
    quotientSearchBound 4 63 3 = 6 ∧
    coarseRadixDepth 4 63 3 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 63 3) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 63 3 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 63 3 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 4 63 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 63 3 ≤ maximumLayerCompilerRawPrecisionBound 4 63 := by
  native_decide

example : coarseK 63 13 = 4 ∧
    quotientSearchBound 4 63 13 = 2 ∧
    coarseRadixDepth 4 63 13 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 63 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 63 13 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 63 13 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 63 = 106 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 63 13 ≤ maximumLayerCompilerRawPrecisionBound 4 63 := by
  native_decide

example : coarseK 64 5 = 10 ∧
    quotientSearchBound 4 64 5 = 4 ∧
    coarseRadixDepth 4 64 5 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 64 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 64 5 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 64 5 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 64 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 64 5 ≤ maximumLayerCompilerRawPrecisionBound 4 64 := by
  native_decide

example : coarseK 64 8 = 7 ∧
    quotientSearchBound 4 64 8 = 3 ∧
    coarseRadixDepth 4 64 8 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 64 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 64 8 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 64 8 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 64 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 64 8 ≤ maximumLayerCompilerRawPrecisionBound 4 64 := by
  native_decide

example : coarseK 64 31 = 1 ∧
    quotientSearchBound 4 64 31 = 1 ∧
    coarseRadixDepth 4 64 31 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 64 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 64 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 64 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 4 64 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 64 31 ≤ maximumLayerCompilerRawPrecisionBound 4 64 := by
  native_decide

example : coarseK 65 0 = 64 ∧
    quotientSearchBound 4 65 0 = 22 ∧
    coarseRadixDepth 4 65 0 = 5 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 65 0) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 65 0 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 65 0 = 108 ∧
    maximumLayerCompilerRawPrecisionBound 4 65 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 65 0 ≤ maximumLayerCompilerRawPrecisionBound 4 65 := by
  native_decide

example : coarseK 65 10 = 5 ∧
    quotientSearchBound 4 65 10 = 2 ∧
    coarseRadixDepth 4 65 10 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 65 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 65 10 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 65 10 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 65 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 65 10 ≤ maximumLayerCompilerRawPrecisionBound 4 65 := by
  native_decide

example : coarseK 65 13 = 4 ∧
    quotientSearchBound 4 65 13 = 2 ∧
    coarseRadixDepth 4 65 13 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 65 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 65 13 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 65 13 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 65 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 65 13 ≤ maximumLayerCompilerRawPrecisionBound 4 65 := by
  native_decide

example : coarseK 66 5 = 10 ∧
    quotientSearchBound 4 66 5 = 4 ∧
    coarseRadixDepth 4 66 5 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 66 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 66 5 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 66 5 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 66 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 66 5 ≤ maximumLayerCompilerRawPrecisionBound 4 66 := by
  native_decide

example : coarseK 67 0 = 66 ∧
    quotientSearchBound 4 67 0 = 23 ∧
    coarseRadixDepth 4 67 0 = 5 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 67 0) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 67 0 = 110 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 67 0 = 110 ∧
    maximumLayerCompilerRawPrecisionBound 4 67 = 110 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 67 0 ≤ maximumLayerCompilerRawPrecisionBound 4 67 := by
  native_decide

example : coarseK 67 10 = 6 ∧
    quotientSearchBound 4 67 10 = 3 ∧
    coarseRadixDepth 4 67 10 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 67 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 67 10 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 67 10 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 67 = 110 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 67 10 ≤ maximumLayerCompilerRawPrecisionBound 4 67 := by
  native_decide

example : coarseK 68 2 = 22 ∧
    quotientSearchBound 4 68 2 = 8 ∧
    coarseRadixDepth 4 68 2 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 68 2) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 68 2 = 24 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 68 2 = 24 ∧
    maximumLayerCompilerRawPrecisionBound 4 68 = 110 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 68 2 ≤ maximumLayerCompilerRawPrecisionBound 4 68 := by
  native_decide

example : coarseK 68 5 = 11 ∧
    quotientSearchBound 4 68 5 = 4 ∧
    coarseRadixDepth 4 68 5 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 68 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 68 5 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 68 5 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 68 = 110 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 68 5 ≤ maximumLayerCompilerRawPrecisionBound 4 68 := by
  native_decide

example : coarseK 69 7 = 8 ∧
    quotientSearchBound 4 69 7 = 3 ∧
    coarseRadixDepth 4 69 7 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 69 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 69 7 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 69 7 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 69 = 110 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 69 7 ≤ maximumLayerCompilerRawPrecisionBound 4 69 := by
  native_decide

example : coarseK 69 10 = 6 ∧
    quotientSearchBound 4 69 10 = 3 ∧
    coarseRadixDepth 4 69 10 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 69 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 69 10 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 69 10 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 69 = 110 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 69 10 ≤ maximumLayerCompilerRawPrecisionBound 4 69 := by
  native_decide

example : coarseK 70 2 = 23 ∧
    quotientSearchBound 4 70 2 = 8 ∧
    coarseRadixDepth 4 70 2 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 70 2) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 70 2 = 24 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 70 2 = 24 ∧
    maximumLayerCompilerRawPrecisionBound 4 70 = 112 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 70 2 ≤ maximumLayerCompilerRawPrecisionBound 4 70 := by
  native_decide

example : coarseK 71 7 = 8 ∧
    quotientSearchBound 4 71 7 = 3 ∧
    coarseRadixDepth 4 71 7 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 71 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 71 7 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 71 7 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 71 = 112 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 71 7 ≤ maximumLayerCompilerRawPrecisionBound 4 71 := by
  native_decide

example : coarseK 71 17 = 3 ∧
    quotientSearchBound 4 71 17 = 2 ∧
    coarseRadixDepth 4 71 17 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 71 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 71 17 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 71 17 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 71 = 112 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 71 17 ≤ maximumLayerCompilerRawPrecisionBound 4 71 := by
  native_decide

example : coarseK 72 2 = 23 ∧
    quotientSearchBound 4 72 2 = 8 ∧
    coarseRadixDepth 4 72 2 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 72 2) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 72 2 = 24 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 72 2 = 24 ∧
    maximumLayerCompilerRawPrecisionBound 4 72 = 112 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 72 2 ≤ maximumLayerCompilerRawPrecisionBound 4 72 := by
  native_decide

example : coarseK 73 4 = 14 ∧
    quotientSearchBound 4 73 4 = 5 ∧
    coarseRadixDepth 4 73 4 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 73 4) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 73 4 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 73 4 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 4 73 = 138 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 73 4 ≤ maximumLayerCompilerRawPrecisionBound 4 73 := by
  native_decide

example : coarseK 73 7 = 9 ∧
    quotientSearchBound 4 73 7 = 4 ∧
    coarseRadixDepth 4 73 7 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 73 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 73 7 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 73 7 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 73 = 138 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 73 7 ≤ maximumLayerCompilerRawPrecisionBound 4 73 := by
  native_decide

example : coarseK 73 17 = 4 ∧
    quotientSearchBound 4 73 17 = 2 ∧
    coarseRadixDepth 4 73 17 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 73 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 73 17 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 73 17 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 73 = 138 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 73 17 ≤ maximumLayerCompilerRawPrecisionBound 4 73 := by
  native_decide

example : coarseK 74 9 = 7 ∧
    quotientSearchBound 4 74 9 = 3 ∧
    coarseRadixDepth 4 74 9 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 74 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 74 9 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 74 9 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 74 = 138 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 74 9 ≤ maximumLayerCompilerRawPrecisionBound 4 74 := by
  native_decide

example : coarseK 75 4 = 14 ∧
    quotientSearchBound 4 75 4 = 5 ∧
    coarseRadixDepth 4 75 4 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 75 4) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 75 4 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 75 4 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 4 75 = 138 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 75 4 ≤ maximumLayerCompilerRawPrecisionBound 4 75 := by
  native_decide

example : coarseK 75 17 = 4 ∧
    quotientSearchBound 4 75 17 = 2 ∧
    coarseRadixDepth 4 75 17 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 75 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 75 17 = 8 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 75 17 = 8 ∧
    maximumLayerCompilerRawPrecisionBound 4 75 = 138 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 75 17 ≤ maximumLayerCompilerRawPrecisionBound 4 75 := by
  native_decide

example : coarseK 76 9 = 7 ∧
    quotientSearchBound 4 76 9 = 3 ∧
    coarseRadixDepth 4 76 9 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 76 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 76 9 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 76 9 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 76 = 140 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 76 9 ≤ maximumLayerCompilerRawPrecisionBound 4 76 := by
  native_decide

example : coarseK 77 1 = 38 ∧
    quotientSearchBound 4 77 1 = 13 ∧
    coarseRadixDepth 4 77 1 = 3 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 77 1) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 77 1 = 54 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 77 1 = 54 ∧
    maximumLayerCompilerRawPrecisionBound 4 77 = 140 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 77 1 ≤ maximumLayerCompilerRawPrecisionBound 4 77 := by
  native_decide

example : coarseK 77 4 = 15 ∧
    quotientSearchBound 4 77 4 = 6 ∧
    coarseRadixDepth 4 77 4 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 77 4) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 77 4 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 77 4 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 4 77 = 140 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 77 4 ≤ maximumLayerCompilerRawPrecisionBound 4 77 := by
  native_decide

example : coarseK 78 6 = 11 ∧
    quotientSearchBound 4 78 6 = 4 ∧
    coarseRadixDepth 4 78 6 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 78 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 78 6 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 78 6 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 78 = 140 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 78 6 ≤ maximumLayerCompilerRawPrecisionBound 4 78 := by
  native_decide

example : coarseK 78 9 = 7 ∧
    quotientSearchBound 4 78 9 = 3 ∧
    coarseRadixDepth 4 78 9 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 78 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 78 9 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 78 9 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 4 78 = 140 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 78 9 ≤ maximumLayerCompilerRawPrecisionBound 4 78 := by
  native_decide

example : coarseK 79 1 = 39 ∧
    quotientSearchBound 4 79 1 = 14 ∧
    coarseRadixDepth 4 79 1 = 3 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 79 1) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 79 1 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 79 1 = 56 ∧
    maximumLayerCompilerRawPrecisionBound 4 79 = 142 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 79 1 ≤ maximumLayerCompilerRawPrecisionBound 4 79 := by
  native_decide

example : coarseK 80 6 = 11 ∧
    quotientSearchBound 4 80 6 = 4 ∧
    coarseRadixDepth 4 80 6 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 80 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 80 6 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 80 6 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 80 = 142 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 80 6 ≤ maximumLayerCompilerRawPrecisionBound 4 80 := by
  native_decide

example : coarseK 97 9 = 9 ∧
    quotientSearchBound 4 97 9 = 4 ∧
    coarseRadixDepth 4 97 9 = 0 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 97 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 97 9 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 97 9 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 4 97 = 214 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 97 9 ≤ maximumLayerCompilerRawPrecisionBound 4 97 := by
  native_decide

example : coarseK 127 1 = 63 ∧
    quotientSearchBound 4 127 1 = 22 ∧
    coarseRadixDepth 4 127 1 = 5 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 127 1) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 127 1 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 127 1 = 108 ∧
    maximumLayerCompilerRawPrecisionBound 4 127 = 310 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 127 1 ≤ maximumLayerCompilerRawPrecisionBound 4 127 := by
  native_decide

example : coarseK 128 3 = 31 ∧
    quotientSearchBound 4 128 3 = 11 ∧
    coarseRadixDepth 4 128 3 = 2 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 128 3) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 128 3 = 38 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 128 3 = 38 ∧
    maximumLayerCompilerRawPrecisionBound 4 128 = 310 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 128 3 ≤ maximumLayerCompilerRawPrecisionBound 4 128 := by
  native_decide

example : coarseK 128 6 = 18 ∧
    quotientSearchBound 4 128 6 = 7 ∧
    coarseRadixDepth 4 128 6 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 128 6) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 128 6 = 22 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 128 6 = 22 ∧
    maximumLayerCompilerRawPrecisionBound 4 128 = 310 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 128 6 ≤ maximumLayerCompilerRawPrecisionBound 4 128 := by
  native_decide

example : coarseK 255 7 = 31 ∧
    quotientSearchBound 4 255 7 = 11 ∧
    coarseRadixDepth 4 255 7 = 2 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 255 7) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 255 7 = 38 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 255 7 = 38 ∧
    maximumLayerCompilerRawPrecisionBound 4 255 = 1098 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 255 7 ≤ maximumLayerCompilerRawPrecisionBound 4 255 := by
  native_decide

example : coarseK 255 17 = 14 ∧
    quotientSearchBound 4 255 17 = 5 ∧
    coarseRadixDepth 4 255 17 = 1 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 255 17) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 255 17 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 255 17 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 4 255 = 1098 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 255 17 ≤ maximumLayerCompilerRawPrecisionBound 4 255 := by
  native_decide

example : coarseK 256 2 = 85 ∧
    quotientSearchBound 4 256 2 = 29 ∧
    coarseRadixDepth 4 256 2 = 7 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 256 2) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 256 2 = 174 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 256 2 = 174 ∧
    maximumLayerCompilerRawPrecisionBound 4 256 = 1100 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 256 2 ≤ maximumLayerCompilerRawPrecisionBound 4 256 := by
  native_decide

example : coarseK 511 9 = 51 ∧
    quotientSearchBound 4 511 9 = 18 ∧
    coarseRadixDepth 4 511 9 = 4 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 511 9) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 511 9 = 80 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 511 9 = 80 ∧
    maximumLayerCompilerRawPrecisionBound 4 511 = 3958 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 511 9 ≤ maximumLayerCompilerRawPrecisionBound 4 511 := by
  native_decide

example : coarseK 1024 1 = 511 ∧
    quotientSearchBound 4 1024 1 = 171 ∧
    coarseRadixDepth 4 1024 1 = 42 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 1024 1) = 42 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 1024 1 = 3958 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 1024 1 = 3958 ∧
    maximumLayerCompilerRawPrecisionBound 4 1024 = 15308 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 1024 1 ≤ maximumLayerCompilerRawPrecisionBound 4 1024 := by
  native_decide

example : coarseK 4097 2 = 1365 ∧
    quotientSearchBound 4 4097 2 = 456 ∧
    coarseRadixDepth 4 4097 2 = 113 ∧
    lastRadixBlockQuotient 4 (quotientSearchBound 4 4097 2) = 113 ∧
    maximumLayerCompilerPrimeEnvelopeBound 4 4097 2 = 26680 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 4097 2 = 26680 ∧
    maximumLayerCompilerRawPrecisionBound 4 4097 = 235980 ∧
    maximumLayerCompilerParameterEnvelopeBound 4 4097 2 ≤ maximumLayerCompilerRawPrecisionBound 4 4097 := by
  native_decide

example : coarseK 0 1 = 0 ∧
    quotientSearchBound 5 0 1 = 1 ∧
    coarseRadixDepth 5 0 1 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 0 1) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 0 1 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 0 1 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 0 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 0 1 ≤ maximumLayerCompilerRawPrecisionBound 5 0 := by
  native_decide

example : coarseK 1 3 = 0 ∧
    quotientSearchBound 5 1 3 = 1 ∧
    coarseRadixDepth 5 1 3 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 1 3) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 1 3 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 1 3 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 1 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 1 3 ≤ maximumLayerCompilerRawPrecisionBound 5 1 := by
  native_decide

example : coarseK 1 6 = 0 ∧
    quotientSearchBound 5 1 6 = 1 ∧
    coarseRadixDepth 5 1 6 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 1 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 1 6 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 1 6 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 1 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 1 6 ≤ maximumLayerCompilerRawPrecisionBound 5 1 := by
  native_decide

example : coarseK 2 8 = 0 ∧
    quotientSearchBound 5 2 8 = 1 ∧
    coarseRadixDepth 5 2 8 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 2 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 2 8 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 2 8 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 2 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 2 8 ≤ maximumLayerCompilerRawPrecisionBound 5 2 := by
  native_decide

example : coarseK 2 31 = 0 ∧
    quotientSearchBound 5 2 31 = 1 ∧
    coarseRadixDepth 5 2 31 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 2 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 2 31 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 2 31 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 2 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 2 31 ≤ maximumLayerCompilerRawPrecisionBound 5 2 := by
  native_decide

example : coarseK 3 3 = 0 ∧
    quotientSearchBound 5 3 3 = 1 ∧
    coarseRadixDepth 5 3 3 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 3 3) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 3 3 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 3 3 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 3 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 3 3 ≤ maximumLayerCompilerRawPrecisionBound 5 3 := by
  native_decide

example : coarseK 3 13 = 0 ∧
    quotientSearchBound 5 3 13 = 1 ∧
    coarseRadixDepth 5 3 13 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 3 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 3 13 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 3 13 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 3 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 3 13 ≤ maximumLayerCompilerRawPrecisionBound 5 3 := by
  native_decide

example : coarseK 4 8 = 0 ∧
    quotientSearchBound 5 4 8 = 1 ∧
    coarseRadixDepth 5 4 8 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 4 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 4 8 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 4 8 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 4 8 ≤ maximumLayerCompilerRawPrecisionBound 5 4 := by
  native_decide

example : coarseK 4 31 = 0 ∧
    quotientSearchBound 5 4 31 = 1 ∧
    coarseRadixDepth 5 4 31 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 4 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 4 31 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 4 31 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 4 31 ≤ maximumLayerCompilerRawPrecisionBound 5 4 := by
  native_decide

example : coarseK 5 0 = 4 ∧
    quotientSearchBound 5 5 0 = 2 ∧
    coarseRadixDepth 5 5 0 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 5 0) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 5 0 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 5 0 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 5 5 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 5 0 ≤ maximumLayerCompilerRawPrecisionBound 5 5 := by
  native_decide

example : coarseK 5 3 = 1 ∧
    quotientSearchBound 5 5 3 = 1 ∧
    coarseRadixDepth 5 5 3 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 5 3) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 5 3 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 5 3 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 5 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 5 3 ≤ maximumLayerCompilerRawPrecisionBound 5 5 := by
  native_decide

example : coarseK 5 13 = 0 ∧
    quotientSearchBound 5 5 13 = 1 ∧
    coarseRadixDepth 5 5 13 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 5 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 5 13 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 5 13 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 5 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 5 13 ≤ maximumLayerCompilerRawPrecisionBound 5 5 := by
  native_decide

example : coarseK 6 5 = 0 ∧
    quotientSearchBound 5 6 5 = 1 ∧
    coarseRadixDepth 5 6 5 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 6 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 6 5 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 6 5 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 6 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 6 5 ≤ maximumLayerCompilerRawPrecisionBound 5 6 := by
  native_decide

example : coarseK 6 8 = 0 ∧
    quotientSearchBound 5 6 8 = 1 ∧
    coarseRadixDepth 5 6 8 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 6 8) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 6 8 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 6 8 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 6 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 6 8 ≤ maximumLayerCompilerRawPrecisionBound 5 6 := by
  native_decide

example : coarseK 6 31 = 0 ∧
    quotientSearchBound 5 6 31 = 1 ∧
    coarseRadixDepth 5 6 31 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 6 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 6 31 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 6 31 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 6 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 6 31 ≤ maximumLayerCompilerRawPrecisionBound 5 6 := by
  native_decide

example : coarseK 7 0 = 6 ∧
    quotientSearchBound 5 7 0 = 2 ∧
    coarseRadixDepth 5 7 0 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 7 0) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 7 0 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 7 0 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 5 7 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 7 0 ≤ maximumLayerCompilerRawPrecisionBound 5 7 := by
  native_decide

example : coarseK 7 10 = 0 ∧
    quotientSearchBound 5 7 10 = 1 ∧
    coarseRadixDepth 5 7 10 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 7 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 7 10 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 7 10 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 7 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 7 10 ≤ maximumLayerCompilerRawPrecisionBound 5 7 := by
  native_decide

example : coarseK 7 13 = 0 ∧
    quotientSearchBound 5 7 13 = 1 ∧
    coarseRadixDepth 5 7 13 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 7 13) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 7 13 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 7 13 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 7 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 7 13 ≤ maximumLayerCompilerRawPrecisionBound 5 7 := by
  native_decide

example : coarseK 8 5 = 1 ∧
    quotientSearchBound 5 8 5 = 1 ∧
    coarseRadixDepth 5 8 5 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 8 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 8 5 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 8 5 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 8 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 8 5 ≤ maximumLayerCompilerRawPrecisionBound 5 8 := by
  native_decide

example : coarseK 9 0 = 8 ∧
    quotientSearchBound 5 9 0 = 3 ∧
    coarseRadixDepth 5 9 0 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 9 0) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 9 0 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 9 0 = 11 ∧
    maximumLayerCompilerRawPrecisionBound 5 9 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 9 0 ≤ maximumLayerCompilerRawPrecisionBound 5 9 := by
  native_decide

example : coarseK 9 10 = 0 ∧
    quotientSearchBound 5 9 10 = 1 ∧
    coarseRadixDepth 5 9 10 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 9 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 9 10 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 9 10 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 9 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 9 10 ≤ maximumLayerCompilerRawPrecisionBound 5 9 := by
  native_decide

example : coarseK 10 2 = 3 ∧
    quotientSearchBound 5 10 2 = 1 ∧
    coarseRadixDepth 5 10 2 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 10 2) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 10 2 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 10 2 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 10 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 10 2 ≤ maximumLayerCompilerRawPrecisionBound 5 10 := by
  native_decide

example : coarseK 10 5 = 1 ∧
    quotientSearchBound 5 10 5 = 1 ∧
    coarseRadixDepth 5 10 5 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 10 5) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 10 5 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 10 5 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 10 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 10 5 ≤ maximumLayerCompilerRawPrecisionBound 5 10 := by
  native_decide

example : coarseK 11 7 = 1 ∧
    quotientSearchBound 5 11 7 = 1 ∧
    coarseRadixDepth 5 11 7 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 11 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 11 7 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 11 7 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 11 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 11 7 ≤ maximumLayerCompilerRawPrecisionBound 5 11 := by
  native_decide

example : coarseK 11 10 = 0 ∧
    quotientSearchBound 5 11 10 = 1 ∧
    coarseRadixDepth 5 11 10 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 11 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 11 10 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 11 10 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 11 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 11 10 ≤ maximumLayerCompilerRawPrecisionBound 5 11 := by
  native_decide

example : coarseK 12 2 = 3 ∧
    quotientSearchBound 5 12 2 = 1 ∧
    coarseRadixDepth 5 12 2 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 12 2) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 12 2 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 12 2 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 12 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 12 2 ≤ maximumLayerCompilerRawPrecisionBound 5 12 := by
  native_decide

example : coarseK 13 7 = 1 ∧
    quotientSearchBound 5 13 7 = 1 ∧
    coarseRadixDepth 5 13 7 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 13 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 13 7 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 13 7 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 13 = 13 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 13 7 ≤ maximumLayerCompilerRawPrecisionBound 5 13 := by
  native_decide

example : coarseK 13 17 = 0 ∧
    quotientSearchBound 5 13 17 = 1 ∧
    coarseRadixDepth 5 13 17 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 13 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 13 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 13 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 13 = 13 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 13 17 ≤ maximumLayerCompilerRawPrecisionBound 5 13 := by
  native_decide

example : coarseK 14 2 = 4 ∧
    quotientSearchBound 5 14 2 = 2 ∧
    coarseRadixDepth 5 14 2 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 14 2) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 14 2 = 9 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 14 2 = 9 ∧
    maximumLayerCompilerRawPrecisionBound 5 14 = 13 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 14 2 ≤ maximumLayerCompilerRawPrecisionBound 5 14 := by
  native_decide

example : coarseK 15 4 = 2 ∧
    quotientSearchBound 5 15 4 = 1 ∧
    coarseRadixDepth 5 15 4 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 15 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 15 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 15 4 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 15 = 13 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 15 4 ≤ maximumLayerCompilerRawPrecisionBound 5 15 := by
  native_decide

example : coarseK 15 7 = 1 ∧
    quotientSearchBound 5 15 7 = 1 ∧
    coarseRadixDepth 5 15 7 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 15 7) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 15 7 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 15 7 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 15 = 13 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 15 7 ≤ maximumLayerCompilerRawPrecisionBound 5 15 := by
  native_decide

example : coarseK 15 17 = 0 ∧
    quotientSearchBound 5 15 17 = 1 ∧
    coarseRadixDepth 5 15 17 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 15 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 15 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 15 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 15 = 13 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 15 17 ≤ maximumLayerCompilerRawPrecisionBound 5 15 := by
  native_decide

example : coarseK 16 9 = 1 ∧
    quotientSearchBound 5 16 9 = 1 ∧
    coarseRadixDepth 5 16 9 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 16 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 16 9 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 16 9 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 16 = 13 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 16 9 ≤ maximumLayerCompilerRawPrecisionBound 5 16 := by
  native_decide

example : coarseK 17 4 = 3 ∧
    quotientSearchBound 5 17 4 = 1 ∧
    coarseRadixDepth 5 17 4 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 17 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 17 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 17 4 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 17 = 15 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 17 4 ≤ maximumLayerCompilerRawPrecisionBound 5 17 := by
  native_decide

example : coarseK 17 17 = 0 ∧
    quotientSearchBound 5 17 17 = 1 ∧
    coarseRadixDepth 5 17 17 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 17 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 17 17 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 17 17 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 17 = 15 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 17 17 ≤ maximumLayerCompilerRawPrecisionBound 5 17 := by
  native_decide

example : coarseK 18 9 = 1 ∧
    quotientSearchBound 5 18 9 = 1 ∧
    coarseRadixDepth 5 18 9 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 18 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 18 9 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 18 9 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 18 = 15 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 18 9 ≤ maximumLayerCompilerRawPrecisionBound 5 18 := by
  native_decide

example : coarseK 19 1 = 9 ∧
    quotientSearchBound 5 19 1 = 3 ∧
    coarseRadixDepth 5 19 1 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 19 1) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 19 1 = 11 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 19 1 = 11 ∧
    maximumLayerCompilerRawPrecisionBound 5 19 = 15 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 19 1 ≤ maximumLayerCompilerRawPrecisionBound 5 19 := by
  native_decide

example : coarseK 19 4 = 3 ∧
    quotientSearchBound 5 19 4 = 1 ∧
    coarseRadixDepth 5 19 4 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 19 4) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 19 4 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 19 4 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 19 = 15 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 19 4 ≤ maximumLayerCompilerRawPrecisionBound 5 19 := by
  native_decide

example : coarseK 20 6 = 2 ∧
    quotientSearchBound 5 20 6 = 1 ∧
    coarseRadixDepth 5 20 6 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 20 6) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 20 6 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 20 6 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 20 = 15 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 20 6 ≤ maximumLayerCompilerRawPrecisionBound 5 20 := by
  native_decide

example : coarseK 20 9 = 1 ∧
    quotientSearchBound 5 20 9 = 1 ∧
    coarseRadixDepth 5 20 9 = 0 ∧
    lastRadixBlockQuotient 5 (quotientSearchBound 5 20 9) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 5 20 9 = 7 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 20 9 = 7 ∧
    maximumLayerCompilerRawPrecisionBound 5 20 = 15 ∧
    maximumLayerCompilerParameterEnvelopeBound 5 20 9 ≤ maximumLayerCompilerRawPrecisionBound 5 20 := by
  native_decide

end KomorebiPadic
