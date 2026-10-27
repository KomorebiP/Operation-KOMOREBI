import KomorebiPadic

namespace KomorebiPadic

example : coarseK 22 0 = 21 ∧
    quotientSearchBound 2 22 0 = 22 ∧
    coarseRadixDepth 2 22 0 = 10 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 22 0) = 10 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 22 0 = 156 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 22 0 = 156 ∧
    maximumLayerCompilerRawPrecisionBound 2 22 = 156 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 22 0 ≤ maximumLayerCompilerRawPrecisionBound 2 22 := by
  native_decide

example : coarseK 22 10 = 1 ∧
    quotientSearchBound 2 22 10 = 2 ∧
    coarseRadixDepth 2 22 10 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 22 10) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 22 10 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 22 10 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 22 = 156 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 22 10 ≤ maximumLayerCompilerRawPrecisionBound 2 22 := by
  native_decide

example : coarseK 23 2 = 7 ∧
    quotientSearchBound 2 23 2 = 8 ∧
    coarseRadixDepth 2 23 2 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 23 2) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 23 2 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 23 2 = 30 ∧
    maximumLayerCompilerRawPrecisionBound 2 23 = 180 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 23 2 ≤ maximumLayerCompilerRawPrecisionBound 2 23 := by
  native_decide

example : coarseK 23 5 = 3 ∧
    quotientSearchBound 2 23 5 = 4 ∧
    coarseRadixDepth 2 23 5 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 23 5) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 23 5 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 23 5 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 23 = 180 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 23 5 ≤ maximumLayerCompilerRawPrecisionBound 2 23 := by
  native_decide

example : coarseK 24 7 = 2 ∧
    quotientSearchBound 2 24 7 = 3 ∧
    coarseRadixDepth 2 24 7 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 24 7) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 24 7 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 24 7 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 24 = 182 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 24 7 ≤ maximumLayerCompilerRawPrecisionBound 2 24 := by
  native_decide

example : coarseK 24 10 = 2 ∧
    quotientSearchBound 2 24 10 = 3 ∧
    coarseRadixDepth 2 24 10 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 24 10) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 24 10 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 24 10 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 24 = 182 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 24 10 ≤ maximumLayerCompilerRawPrecisionBound 2 24 := by
  native_decide

example : coarseK 25 2 = 8 ∧
    quotientSearchBound 2 25 2 = 9 ∧
    coarseRadixDepth 2 25 2 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 25 2) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 25 2 = 40 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 25 2 = 40 ∧
    maximumLayerCompilerRawPrecisionBound 2 25 = 208 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 25 2 ≤ maximumLayerCompilerRawPrecisionBound 2 25 := by
  native_decide

example : coarseK 26 7 = 3 ∧
    quotientSearchBound 2 26 7 = 4 ∧
    coarseRadixDepth 2 26 7 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 26 7) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 26 7 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 26 7 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 26 = 210 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 26 7 ≤ maximumLayerCompilerRawPrecisionBound 2 26 := by
  native_decide

example : coarseK 26 17 = 1 ∧
    quotientSearchBound 2 26 17 = 2 ∧
    coarseRadixDepth 2 26 17 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 26 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 26 17 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 26 17 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 26 = 210 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 26 17 ≤ maximumLayerCompilerRawPrecisionBound 2 26 := by
  native_decide

example : coarseK 27 2 = 8 ∧
    quotientSearchBound 2 27 2 = 9 ∧
    coarseRadixDepth 2 27 2 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 27 2) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 27 2 = 40 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 27 2 = 40 ∧
    maximumLayerCompilerRawPrecisionBound 2 27 = 238 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 27 2 ≤ maximumLayerCompilerRawPrecisionBound 2 27 := by
  native_decide

example : coarseK 28 4 = 5 ∧
    quotientSearchBound 2 28 4 = 6 ∧
    coarseRadixDepth 2 28 4 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 28 4) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 28 4 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 28 4 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 28 = 240 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 28 4 ≤ maximumLayerCompilerRawPrecisionBound 2 28 := by
  native_decide

example : coarseK 28 7 = 3 ∧
    quotientSearchBound 2 28 7 = 4 ∧
    coarseRadixDepth 2 28 7 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 28 7) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 28 7 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 28 7 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 28 = 240 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 28 7 ≤ maximumLayerCompilerRawPrecisionBound 2 28 := by
  native_decide

example : coarseK 28 17 = 1 ∧
    quotientSearchBound 2 28 17 = 2 ∧
    coarseRadixDepth 2 28 17 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 28 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 28 17 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 28 17 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 28 = 240 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 28 17 ≤ maximumLayerCompilerRawPrecisionBound 2 28 := by
  native_decide

example : coarseK 29 9 = 2 ∧
    quotientSearchBound 2 29 9 = 3 ∧
    coarseRadixDepth 2 29 9 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 29 9) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 29 9 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 29 9 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 29 = 270 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 29 9 ≤ maximumLayerCompilerRawPrecisionBound 2 29 := by
  native_decide

example : coarseK 30 4 = 5 ∧
    quotientSearchBound 2 30 4 = 6 ∧
    coarseRadixDepth 2 30 4 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 30 4) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 30 4 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 30 4 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 30 = 272 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 30 4 ≤ maximumLayerCompilerRawPrecisionBound 2 30 := by
  native_decide

example : coarseK 30 17 = 1 ∧
    quotientSearchBound 2 30 17 = 2 ∧
    coarseRadixDepth 2 30 17 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 30 17) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 30 17 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 30 17 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 30 = 272 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 30 17 ≤ maximumLayerCompilerRawPrecisionBound 2 30 := by
  native_decide

example : coarseK 31 9 = 3 ∧
    quotientSearchBound 2 31 9 = 4 ∧
    coarseRadixDepth 2 31 9 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 31 9) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 31 9 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 31 9 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 31 = 304 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 31 9 ≤ maximumLayerCompilerRawPrecisionBound 2 31 := by
  native_decide

example : coarseK 32 1 = 15 ∧
    quotientSearchBound 2 32 1 = 16 ∧
    coarseRadixDepth 2 32 1 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 32 1) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 32 1 = 90 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 32 1 = 90 ∧
    maximumLayerCompilerRawPrecisionBound 2 32 = 306 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 32 1 ≤ maximumLayerCompilerRawPrecisionBound 2 32 := by
  native_decide

example : coarseK 32 4 = 6 ∧
    quotientSearchBound 2 32 4 = 7 ∧
    coarseRadixDepth 2 32 4 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 32 4) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 32 4 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 32 4 = 28 ∧
    maximumLayerCompilerRawPrecisionBound 2 32 = 306 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 32 4 ≤ maximumLayerCompilerRawPrecisionBound 2 32 := by
  native_decide

example : coarseK 33 6 = 4 ∧
    quotientSearchBound 2 33 6 = 5 ∧
    coarseRadixDepth 2 33 6 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 33 6) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 33 6 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 33 6 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 33 = 340 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 33 6 ≤ maximumLayerCompilerRawPrecisionBound 2 33 := by
  native_decide

example : coarseK 33 9 = 3 ∧
    quotientSearchBound 2 33 9 = 4 ∧
    coarseRadixDepth 2 33 9 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 33 9) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 33 9 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 33 9 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 33 = 340 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 33 9 ≤ maximumLayerCompilerRawPrecisionBound 2 33 := by
  native_decide

example : coarseK 34 1 = 16 ∧
    quotientSearchBound 2 34 1 = 17 ∧
    coarseRadixDepth 2 34 1 = 8 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 34 1) = 8 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 34 1 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 34 1 = 108 ∧
    maximumLayerCompilerRawPrecisionBound 2 34 = 342 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 34 1 ≤ maximumLayerCompilerRawPrecisionBound 2 34 := by
  native_decide

example : coarseK 35 6 = 4 ∧
    quotientSearchBound 2 35 6 = 5 ∧
    coarseRadixDepth 2 35 6 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 35 6) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 35 6 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 35 6 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 35 = 378 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 35 6 ≤ maximumLayerCompilerRawPrecisionBound 2 35 := by
  native_decide

example : coarseK 36 1 = 17 ∧
    quotientSearchBound 2 36 1 = 18 ∧
    coarseRadixDepth 2 36 1 = 8 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 36 1) = 8 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 36 1 = 110 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 36 1 = 110 ∧
    maximumLayerCompilerRawPrecisionBound 2 36 = 380 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 36 1 ≤ maximumLayerCompilerRawPrecisionBound 2 36 := by
  native_decide

example : coarseK 37 3 = 9 ∧
    quotientSearchBound 2 37 3 = 10 ∧
    coarseRadixDepth 2 37 3 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 37 3) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 37 3 = 42 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 37 3 = 42 ∧
    maximumLayerCompilerRawPrecisionBound 2 37 = 418 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 37 3 ≤ maximumLayerCompilerRawPrecisionBound 2 37 := by
  native_decide

example : coarseK 37 6 = 5 ∧
    quotientSearchBound 2 37 6 = 6 ∧
    coarseRadixDepth 2 37 6 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 37 6) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 37 6 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 37 6 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 37 = 418 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 37 6 ≤ maximumLayerCompilerRawPrecisionBound 2 37 := by
  native_decide

example : coarseK 38 8 = 4 ∧
    quotientSearchBound 2 38 8 = 5 ∧
    coarseRadixDepth 2 38 8 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 38 8) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 38 8 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 38 8 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 38 = 420 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 38 8 ≤ maximumLayerCompilerRawPrecisionBound 2 38 := by
  native_decide

example : coarseK 38 31 = 1 ∧
    quotientSearchBound 2 38 31 = 2 ∧
    coarseRadixDepth 2 38 31 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 38 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 38 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 38 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 38 = 420 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 38 31 ≤ maximumLayerCompilerRawPrecisionBound 2 38 := by
  native_decide

example : coarseK 39 3 = 9 ∧
    quotientSearchBound 2 39 3 = 10 ∧
    coarseRadixDepth 2 39 3 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 39 3) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 39 3 = 42 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 39 3 = 42 ∧
    maximumLayerCompilerRawPrecisionBound 2 39 = 460 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 39 3 ≤ maximumLayerCompilerRawPrecisionBound 2 39 := by
  native_decide

example : coarseK 39 13 = 2 ∧
    quotientSearchBound 2 39 13 = 3 ∧
    coarseRadixDepth 2 39 13 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 39 13) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 39 13 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 39 13 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 39 = 460 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 39 13 ≤ maximumLayerCompilerRawPrecisionBound 2 39 := by
  native_decide

example : coarseK 40 8 = 4 ∧
    quotientSearchBound 2 40 8 = 5 ∧
    coarseRadixDepth 2 40 8 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 40 8) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 40 8 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 40 8 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 40 = 462 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 40 8 ≤ maximumLayerCompilerRawPrecisionBound 2 40 := by
  native_decide

example : coarseK 40 31 = 1 ∧
    quotientSearchBound 2 40 31 = 2 ∧
    coarseRadixDepth 2 40 31 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 40 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 40 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 40 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 40 = 462 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 40 31 ≤ maximumLayerCompilerRawPrecisionBound 2 40 := by
  native_decide

example : coarseK 41 0 = 40 ∧
    quotientSearchBound 2 41 0 = 41 ∧
    coarseRadixDepth 2 41 0 = 20 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 41 0) = 20 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 41 0 = 504 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 41 0 = 504 ∧
    maximumLayerCompilerRawPrecisionBound 2 41 = 504 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 41 0 ≤ maximumLayerCompilerRawPrecisionBound 2 41 := by
  native_decide

example : coarseK 41 3 = 10 ∧
    quotientSearchBound 2 41 3 = 11 ∧
    coarseRadixDepth 2 41 3 = 5 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 41 3) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 41 3 = 54 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 41 3 = 54 ∧
    maximumLayerCompilerRawPrecisionBound 2 41 = 504 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 41 3 ≤ maximumLayerCompilerRawPrecisionBound 2 41 := by
  native_decide

example : coarseK 41 13 = 2 ∧
    quotientSearchBound 2 41 13 = 3 ∧
    coarseRadixDepth 2 41 13 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 41 13) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 41 13 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 41 13 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 41 = 504 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 41 13 ≤ maximumLayerCompilerRawPrecisionBound 2 41 := by
  native_decide

example : coarseK 42 5 = 6 ∧
    quotientSearchBound 2 42 5 = 7 ∧
    coarseRadixDepth 2 42 5 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 42 5) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 42 5 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 42 5 = 28 ∧
    maximumLayerCompilerRawPrecisionBound 2 42 = 506 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 42 5 ≤ maximumLayerCompilerRawPrecisionBound 2 42 := by
  native_decide

example : coarseK 42 8 = 4 ∧
    quotientSearchBound 2 42 8 = 5 ∧
    coarseRadixDepth 2 42 8 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 42 8) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 42 8 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 42 8 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 42 = 506 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 42 8 ≤ maximumLayerCompilerRawPrecisionBound 2 42 := by
  native_decide

example : coarseK 42 31 = 1 ∧
    quotientSearchBound 2 42 31 = 2 ∧
    coarseRadixDepth 2 42 31 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 42 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 42 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 42 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 42 = 506 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 42 31 ≤ maximumLayerCompilerRawPrecisionBound 2 42 := by
  native_decide

example : coarseK 43 0 = 42 ∧
    quotientSearchBound 2 43 0 = 43 ∧
    coarseRadixDepth 2 43 0 = 21 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 43 0) = 21 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 43 0 = 550 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 43 0 = 550 ∧
    maximumLayerCompilerRawPrecisionBound 2 43 = 550 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 43 0 ≤ maximumLayerCompilerRawPrecisionBound 2 43 := by
  native_decide

example : coarseK 43 10 = 3 ∧
    quotientSearchBound 2 43 10 = 4 ∧
    coarseRadixDepth 2 43 10 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 43 10) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 43 10 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 43 10 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 43 = 550 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 43 10 ≤ maximumLayerCompilerRawPrecisionBound 2 43 := by
  native_decide

example : coarseK 43 13 = 3 ∧
    quotientSearchBound 2 43 13 = 4 ∧
    coarseRadixDepth 2 43 13 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 43 13) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 43 13 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 43 13 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 43 = 550 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 43 13 ≤ maximumLayerCompilerRawPrecisionBound 2 43 := by
  native_decide

example : coarseK 44 5 = 7 ∧
    quotientSearchBound 2 44 5 = 8 ∧
    coarseRadixDepth 2 44 5 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 44 5) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 44 5 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 44 5 = 30 ∧
    maximumLayerCompilerRawPrecisionBound 2 44 = 552 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 44 5 ≤ maximumLayerCompilerRawPrecisionBound 2 44 := by
  native_decide

example : coarseK 45 0 = 44 ∧
    quotientSearchBound 2 45 0 = 45 ∧
    coarseRadixDepth 2 45 0 = 22 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 45 0) = 22 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 45 0 = 598 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 45 0 = 598 ∧
    maximumLayerCompilerRawPrecisionBound 2 45 = 598 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 45 0 ≤ maximumLayerCompilerRawPrecisionBound 2 45 := by
  native_decide

example : coarseK 45 10 = 4 ∧
    quotientSearchBound 2 45 10 = 5 ∧
    coarseRadixDepth 2 45 10 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 45 10) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 45 10 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 45 10 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 45 = 598 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 45 10 ≤ maximumLayerCompilerRawPrecisionBound 2 45 := by
  native_decide

example : coarseK 46 2 = 15 ∧
    quotientSearchBound 2 46 2 = 16 ∧
    coarseRadixDepth 2 46 2 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 46 2) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 46 2 = 90 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 46 2 = 90 ∧
    maximumLayerCompilerRawPrecisionBound 2 46 = 600 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 46 2 ≤ maximumLayerCompilerRawPrecisionBound 2 46 := by
  native_decide

example : coarseK 46 5 = 7 ∧
    quotientSearchBound 2 46 5 = 8 ∧
    coarseRadixDepth 2 46 5 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 46 5) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 46 5 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 46 5 = 30 ∧
    maximumLayerCompilerRawPrecisionBound 2 46 = 600 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 46 5 ≤ maximumLayerCompilerRawPrecisionBound 2 46 := by
  native_decide

example : coarseK 47 7 = 5 ∧
    quotientSearchBound 2 47 7 = 6 ∧
    coarseRadixDepth 2 47 7 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 47 7) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 47 7 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 47 7 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 47 = 648 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 47 7 ≤ maximumLayerCompilerRawPrecisionBound 2 47 := by
  native_decide

example : coarseK 47 10 = 4 ∧
    quotientSearchBound 2 47 10 = 5 ∧
    coarseRadixDepth 2 47 10 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 47 10) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 47 10 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 47 10 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 47 = 648 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 47 10 ≤ maximumLayerCompilerRawPrecisionBound 2 47 := by
  native_decide

example : coarseK 48 2 = 15 ∧
    quotientSearchBound 2 48 2 = 16 ∧
    coarseRadixDepth 2 48 2 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 48 2) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 48 2 = 90 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 48 2 = 90 ∧
    maximumLayerCompilerRawPrecisionBound 2 48 = 650 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 48 2 ≤ maximumLayerCompilerRawPrecisionBound 2 48 := by
  native_decide

example : coarseK 49 7 = 6 ∧
    quotientSearchBound 2 49 7 = 7 ∧
    coarseRadixDepth 2 49 7 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 49 7) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 49 7 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 49 7 = 28 ∧
    maximumLayerCompilerRawPrecisionBound 2 49 = 700 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 49 7 ≤ maximumLayerCompilerRawPrecisionBound 2 49 := by
  native_decide

example : coarseK 49 17 = 2 ∧
    quotientSearchBound 2 49 17 = 3 ∧
    coarseRadixDepth 2 49 17 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 49 17) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 49 17 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 49 17 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 49 = 700 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 49 17 ≤ maximumLayerCompilerRawPrecisionBound 2 49 := by
  native_decide

example : coarseK 50 2 = 16 ∧
    quotientSearchBound 2 50 2 = 17 ∧
    coarseRadixDepth 2 50 2 = 8 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 50 2) = 8 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 50 2 = 108 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 50 2 = 108 ∧
    maximumLayerCompilerRawPrecisionBound 2 50 = 702 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 50 2 ≤ maximumLayerCompilerRawPrecisionBound 2 50 := by
  native_decide

example : coarseK 51 4 = 10 ∧
    quotientSearchBound 2 51 4 = 11 ∧
    coarseRadixDepth 2 51 4 = 5 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 51 4) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 51 4 = 54 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 51 4 = 54 ∧
    maximumLayerCompilerRawPrecisionBound 2 51 = 754 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 51 4 ≤ maximumLayerCompilerRawPrecisionBound 2 51 := by
  native_decide

example : coarseK 51 7 = 6 ∧
    quotientSearchBound 2 51 7 = 7 ∧
    coarseRadixDepth 2 51 7 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 51 7) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 51 7 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 51 7 = 28 ∧
    maximumLayerCompilerRawPrecisionBound 2 51 = 754 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 51 7 ≤ maximumLayerCompilerRawPrecisionBound 2 51 := by
  native_decide

example : coarseK 51 17 = 2 ∧
    quotientSearchBound 2 51 17 = 3 ∧
    coarseRadixDepth 2 51 17 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 51 17) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 51 17 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 51 17 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 51 = 754 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 51 17 ≤ maximumLayerCompilerRawPrecisionBound 2 51 := by
  native_decide

example : coarseK 52 9 = 5 ∧
    quotientSearchBound 2 52 9 = 6 ∧
    coarseRadixDepth 2 52 9 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 52 9) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 52 9 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 52 9 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 52 = 756 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 52 9 ≤ maximumLayerCompilerRawPrecisionBound 2 52 := by
  native_decide

example : coarseK 53 4 = 10 ∧
    quotientSearchBound 2 53 4 = 11 ∧
    coarseRadixDepth 2 53 4 = 5 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 53 4) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 53 4 = 54 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 53 4 = 54 ∧
    maximumLayerCompilerRawPrecisionBound 2 53 = 810 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 53 4 ≤ maximumLayerCompilerRawPrecisionBound 2 53 := by
  native_decide

example : coarseK 53 17 = 2 ∧
    quotientSearchBound 2 53 17 = 3 ∧
    coarseRadixDepth 2 53 17 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 53 17) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 53 17 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 53 17 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 53 = 810 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 53 17 ≤ maximumLayerCompilerRawPrecisionBound 2 53 := by
  native_decide

example : coarseK 54 9 = 5 ∧
    quotientSearchBound 2 54 9 = 6 ∧
    coarseRadixDepth 2 54 9 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 54 9) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 54 9 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 54 9 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 54 = 812 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 54 9 ≤ maximumLayerCompilerRawPrecisionBound 2 54 := by
  native_decide

example : coarseK 55 1 = 27 ∧
    quotientSearchBound 2 55 1 = 28 ∧
    coarseRadixDepth 2 55 1 = 13 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 55 1) = 13 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 55 1 = 240 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 55 1 = 240 ∧
    maximumLayerCompilerRawPrecisionBound 2 55 = 868 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 55 1 ≤ maximumLayerCompilerRawPrecisionBound 2 55 := by
  native_decide

example : coarseK 55 4 = 10 ∧
    quotientSearchBound 2 55 4 = 11 ∧
    coarseRadixDepth 2 55 4 = 5 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 55 4) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 55 4 = 54 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 55 4 = 54 ∧
    maximumLayerCompilerRawPrecisionBound 2 55 = 868 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 55 4 ≤ maximumLayerCompilerRawPrecisionBound 2 55 := by
  native_decide

example : coarseK 56 6 = 7 ∧
    quotientSearchBound 2 56 6 = 8 ∧
    coarseRadixDepth 2 56 6 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 56 6) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 56 6 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 56 6 = 30 ∧
    maximumLayerCompilerRawPrecisionBound 2 56 = 870 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 56 6 ≤ maximumLayerCompilerRawPrecisionBound 2 56 := by
  native_decide

example : coarseK 56 9 = 5 ∧
    quotientSearchBound 2 56 9 = 6 ∧
    coarseRadixDepth 2 56 9 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 56 9) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 56 9 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 56 9 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 56 = 870 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 56 9 ≤ maximumLayerCompilerRawPrecisionBound 2 56 := by
  native_decide

example : coarseK 57 1 = 28 ∧
    quotientSearchBound 2 57 1 = 29 ∧
    coarseRadixDepth 2 57 1 = 14 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 57 1) = 14 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 57 1 = 270 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 57 1 = 270 ∧
    maximumLayerCompilerRawPrecisionBound 2 57 = 928 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 57 1 ≤ maximumLayerCompilerRawPrecisionBound 2 57 := by
  native_decide

example : coarseK 58 6 = 8 ∧
    quotientSearchBound 2 58 6 = 9 ∧
    coarseRadixDepth 2 58 6 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 58 6) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 58 6 = 40 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 58 6 = 40 ∧
    maximumLayerCompilerRawPrecisionBound 2 58 = 930 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 58 6 ≤ maximumLayerCompilerRawPrecisionBound 2 58 := by
  native_decide

example : coarseK 59 1 = 29 ∧
    quotientSearchBound 2 59 1 = 30 ∧
    coarseRadixDepth 2 59 1 = 14 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 59 1) = 14 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 59 1 = 272 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 59 1 = 272 ∧
    maximumLayerCompilerRawPrecisionBound 2 59 = 990 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 59 1 ≤ maximumLayerCompilerRawPrecisionBound 2 59 := by
  native_decide

example : coarseK 60 3 = 14 ∧
    quotientSearchBound 2 60 3 = 15 ∧
    coarseRadixDepth 2 60 3 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 60 3) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 60 3 = 88 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 60 3 = 88 ∧
    maximumLayerCompilerRawPrecisionBound 2 60 = 992 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 60 3 ≤ maximumLayerCompilerRawPrecisionBound 2 60 := by
  native_decide

example : coarseK 60 6 = 8 ∧
    quotientSearchBound 2 60 6 = 9 ∧
    coarseRadixDepth 2 60 6 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 60 6) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 60 6 = 40 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 60 6 = 40 ∧
    maximumLayerCompilerRawPrecisionBound 2 60 = 992 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 60 6 ≤ maximumLayerCompilerRawPrecisionBound 2 60 := by
  native_decide

example : coarseK 61 8 = 6 ∧
    quotientSearchBound 2 61 8 = 7 ∧
    coarseRadixDepth 2 61 8 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 61 8) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 61 8 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 61 8 = 28 ∧
    maximumLayerCompilerRawPrecisionBound 2 61 = 1054 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 61 8 ≤ maximumLayerCompilerRawPrecisionBound 2 61 := by
  native_decide

example : coarseK 61 31 = 1 ∧
    quotientSearchBound 2 61 31 = 2 ∧
    coarseRadixDepth 2 61 31 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 61 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 61 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 61 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 61 = 1054 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 61 31 ≤ maximumLayerCompilerRawPrecisionBound 2 61 := by
  native_decide

example : coarseK 62 3 = 15 ∧
    quotientSearchBound 2 62 3 = 16 ∧
    coarseRadixDepth 2 62 3 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 62 3) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 62 3 = 90 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 62 3 = 90 ∧
    maximumLayerCompilerRawPrecisionBound 2 62 = 1056 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 62 3 ≤ maximumLayerCompilerRawPrecisionBound 2 62 := by
  native_decide

example : coarseK 62 13 = 4 ∧
    quotientSearchBound 2 62 13 = 5 ∧
    coarseRadixDepth 2 62 13 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 62 13) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 62 13 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 62 13 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 62 = 1056 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 62 13 ≤ maximumLayerCompilerRawPrecisionBound 2 62 := by
  native_decide

example : coarseK 63 8 = 6 ∧
    quotientSearchBound 2 63 8 = 7 ∧
    coarseRadixDepth 2 63 8 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 63 8) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 63 8 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 63 8 = 28 ∧
    maximumLayerCompilerRawPrecisionBound 2 63 = 1120 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 63 8 ≤ maximumLayerCompilerRawPrecisionBound 2 63 := by
  native_decide

example : coarseK 63 31 = 1 ∧
    quotientSearchBound 2 63 31 = 2 ∧
    coarseRadixDepth 2 63 31 = 0 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 63 31) = 0 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 63 31 = 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 63 31 = 6 ∧
    maximumLayerCompilerRawPrecisionBound 2 63 = 1120 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 63 31 ≤ maximumLayerCompilerRawPrecisionBound 2 63 := by
  native_decide

example : coarseK 64 0 = 63 ∧
    quotientSearchBound 2 64 0 = 64 ∧
    coarseRadixDepth 2 64 0 = 31 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 64 0) = 31 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 64 0 = 1122 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 64 0 = 1122 ∧
    maximumLayerCompilerRawPrecisionBound 2 64 = 1122 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 64 0 ≤ maximumLayerCompilerRawPrecisionBound 2 64 := by
  native_decide

example : coarseK 64 3 = 15 ∧
    quotientSearchBound 2 64 3 = 16 ∧
    coarseRadixDepth 2 64 3 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 64 3) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 64 3 = 90 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 64 3 = 90 ∧
    maximumLayerCompilerRawPrecisionBound 2 64 = 1122 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 64 3 ≤ maximumLayerCompilerRawPrecisionBound 2 64 := by
  native_decide

example : coarseK 64 13 = 4 ∧
    quotientSearchBound 2 64 13 = 5 ∧
    coarseRadixDepth 2 64 13 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 64 13) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 64 13 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 64 13 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 64 = 1122 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 64 13 ≤ maximumLayerCompilerRawPrecisionBound 2 64 := by
  native_decide

example : coarseK 65 5 = 10 ∧
    quotientSearchBound 2 65 5 = 11 ∧
    coarseRadixDepth 2 65 5 = 5 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 65 5) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 65 5 = 54 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 65 5 = 54 ∧
    maximumLayerCompilerRawPrecisionBound 2 65 = 1188 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 65 5 ≤ maximumLayerCompilerRawPrecisionBound 2 65 := by
  native_decide

example : coarseK 65 8 = 7 ∧
    quotientSearchBound 2 65 8 = 8 ∧
    coarseRadixDepth 2 65 8 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 65 8) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 65 8 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 65 8 = 30 ∧
    maximumLayerCompilerRawPrecisionBound 2 65 = 1188 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 65 8 ≤ maximumLayerCompilerRawPrecisionBound 2 65 := by
  native_decide

example : coarseK 65 31 = 2 ∧
    quotientSearchBound 2 65 31 = 3 ∧
    coarseRadixDepth 2 65 31 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 65 31) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 65 31 = 10 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 65 31 = 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 65 = 1188 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 65 31 ≤ maximumLayerCompilerRawPrecisionBound 2 65 := by
  native_decide

example : coarseK 66 0 = 65 ∧
    quotientSearchBound 2 66 0 = 66 ∧
    coarseRadixDepth 2 66 0 = 32 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 66 0) = 32 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 66 0 = 1190 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 66 0 = 1190 ∧
    maximumLayerCompilerRawPrecisionBound 2 66 = 1190 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 66 0 ≤ maximumLayerCompilerRawPrecisionBound 2 66 := by
  native_decide

example : coarseK 66 10 = 5 ∧
    quotientSearchBound 2 66 10 = 6 ∧
    coarseRadixDepth 2 66 10 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 66 10) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 66 10 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 66 10 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 66 = 1190 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 66 10 ≤ maximumLayerCompilerRawPrecisionBound 2 66 := by
  native_decide

example : coarseK 66 13 = 4 ∧
    quotientSearchBound 2 66 13 = 5 ∧
    coarseRadixDepth 2 66 13 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 66 13) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 66 13 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 66 13 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 66 = 1190 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 66 13 ≤ maximumLayerCompilerRawPrecisionBound 2 66 := by
  native_decide

example : coarseK 67 5 = 11 ∧
    quotientSearchBound 2 67 5 = 12 ∧
    coarseRadixDepth 2 67 5 = 5 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 67 5) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 67 5 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 67 5 = 56 ∧
    maximumLayerCompilerRawPrecisionBound 2 67 = 1258 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 67 5 ≤ maximumLayerCompilerRawPrecisionBound 2 67 := by
  native_decide

example : coarseK 68 0 = 67 ∧
    quotientSearchBound 2 68 0 = 68 ∧
    coarseRadixDepth 2 68 0 = 33 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 68 0) = 33 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 68 0 = 1260 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 68 0 = 1260 ∧
    maximumLayerCompilerRawPrecisionBound 2 68 = 1260 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 68 0 ≤ maximumLayerCompilerRawPrecisionBound 2 68 := by
  native_decide

example : coarseK 68 10 = 6 ∧
    quotientSearchBound 2 68 10 = 7 ∧
    coarseRadixDepth 2 68 10 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 68 10) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 68 10 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 68 10 = 28 ∧
    maximumLayerCompilerRawPrecisionBound 2 68 = 1260 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 68 10 ≤ maximumLayerCompilerRawPrecisionBound 2 68 := by
  native_decide

example : coarseK 69 2 = 22 ∧
    quotientSearchBound 2 69 2 = 23 ∧
    coarseRadixDepth 2 69 2 = 11 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 69 2) = 11 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 69 2 = 180 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 69 2 = 180 ∧
    maximumLayerCompilerRawPrecisionBound 2 69 = 1330 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 69 2 ≤ maximumLayerCompilerRawPrecisionBound 2 69 := by
  native_decide

example : coarseK 69 5 = 11 ∧
    quotientSearchBound 2 69 5 = 12 ∧
    coarseRadixDepth 2 69 5 = 5 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 69 5) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 69 5 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 69 5 = 56 ∧
    maximumLayerCompilerRawPrecisionBound 2 69 = 1330 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 69 5 ≤ maximumLayerCompilerRawPrecisionBound 2 69 := by
  native_decide

example : coarseK 70 7 = 8 ∧
    quotientSearchBound 2 70 7 = 9 ∧
    coarseRadixDepth 2 70 7 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 70 7) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 70 7 = 40 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 70 7 = 40 ∧
    maximumLayerCompilerRawPrecisionBound 2 70 = 1332 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 70 7 ≤ maximumLayerCompilerRawPrecisionBound 2 70 := by
  native_decide

example : coarseK 70 10 = 6 ∧
    quotientSearchBound 2 70 10 = 7 ∧
    coarseRadixDepth 2 70 10 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 70 10) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 70 10 = 28 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 70 10 = 28 ∧
    maximumLayerCompilerRawPrecisionBound 2 70 = 1332 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 70 10 ≤ maximumLayerCompilerRawPrecisionBound 2 70 := by
  native_decide

example : coarseK 71 2 = 23 ∧
    quotientSearchBound 2 71 2 = 24 ∧
    coarseRadixDepth 2 71 2 = 11 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 71 2) = 11 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 71 2 = 182 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 71 2 = 182 ∧
    maximumLayerCompilerRawPrecisionBound 2 71 = 1404 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 71 2 ≤ maximumLayerCompilerRawPrecisionBound 2 71 := by
  native_decide

example : coarseK 72 7 = 8 ∧
    quotientSearchBound 2 72 7 = 9 ∧
    coarseRadixDepth 2 72 7 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 72 7) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 72 7 = 40 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 72 7 = 40 ∧
    maximumLayerCompilerRawPrecisionBound 2 72 = 1406 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 72 7 ≤ maximumLayerCompilerRawPrecisionBound 2 72 := by
  native_decide

example : coarseK 72 17 = 3 ∧
    quotientSearchBound 2 72 17 = 4 ∧
    coarseRadixDepth 2 72 17 = 1 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 72 17) = 1 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 72 17 = 12 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 72 17 = 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 72 = 1406 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 72 17 ≤ maximumLayerCompilerRawPrecisionBound 2 72 := by
  native_decide

example : coarseK 73 2 = 24 ∧
    quotientSearchBound 2 73 2 = 25 ∧
    coarseRadixDepth 2 73 2 = 12 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 73 2) = 12 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 73 2 = 208 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 73 2 = 208 ∧
    maximumLayerCompilerRawPrecisionBound 2 73 = 1480 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 73 2 ≤ maximumLayerCompilerRawPrecisionBound 2 73 := by
  native_decide

example : coarseK 74 4 = 14 ∧
    quotientSearchBound 2 74 4 = 15 ∧
    coarseRadixDepth 2 74 4 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 74 4) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 74 4 = 88 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 74 4 = 88 ∧
    maximumLayerCompilerRawPrecisionBound 2 74 = 1482 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 74 4 ≤ maximumLayerCompilerRawPrecisionBound 2 74 := by
  native_decide

example : coarseK 74 7 = 9 ∧
    quotientSearchBound 2 74 7 = 10 ∧
    coarseRadixDepth 2 74 7 = 4 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 74 7) = 4 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 74 7 = 42 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 74 7 = 42 ∧
    maximumLayerCompilerRawPrecisionBound 2 74 = 1482 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 74 7 ≤ maximumLayerCompilerRawPrecisionBound 2 74 := by
  native_decide

example : coarseK 74 17 = 4 ∧
    quotientSearchBound 2 74 17 = 5 ∧
    coarseRadixDepth 2 74 17 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 74 17) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 74 17 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 74 17 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 74 = 1482 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 74 17 ≤ maximumLayerCompilerRawPrecisionBound 2 74 := by
  native_decide

example : coarseK 75 9 = 7 ∧
    quotientSearchBound 2 75 9 = 8 ∧
    coarseRadixDepth 2 75 9 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 75 9) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 75 9 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 75 9 = 30 ∧
    maximumLayerCompilerRawPrecisionBound 2 75 = 1558 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 75 9 ≤ maximumLayerCompilerRawPrecisionBound 2 75 := by
  native_decide

example : coarseK 76 4 = 15 ∧
    quotientSearchBound 2 76 4 = 16 ∧
    coarseRadixDepth 2 76 4 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 76 4) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 76 4 = 90 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 76 4 = 90 ∧
    maximumLayerCompilerRawPrecisionBound 2 76 = 1560 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 76 4 ≤ maximumLayerCompilerRawPrecisionBound 2 76 := by
  native_decide

example : coarseK 76 17 = 4 ∧
    quotientSearchBound 2 76 17 = 5 ∧
    coarseRadixDepth 2 76 17 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 76 17) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 76 17 = 18 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 76 17 = 18 ∧
    maximumLayerCompilerRawPrecisionBound 2 76 = 1560 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 76 17 ≤ maximumLayerCompilerRawPrecisionBound 2 76 := by
  native_decide

example : coarseK 77 9 = 7 ∧
    quotientSearchBound 2 77 9 = 8 ∧
    coarseRadixDepth 2 77 9 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 77 9) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 77 9 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 77 9 = 30 ∧
    maximumLayerCompilerRawPrecisionBound 2 77 = 1638 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 77 9 ≤ maximumLayerCompilerRawPrecisionBound 2 77 := by
  native_decide

example : coarseK 78 1 = 38 ∧
    quotientSearchBound 2 78 1 = 39 ∧
    coarseRadixDepth 2 78 1 = 19 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 78 1) = 19 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 78 1 = 460 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 78 1 = 460 ∧
    maximumLayerCompilerRawPrecisionBound 2 78 = 1640 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 78 1 ≤ maximumLayerCompilerRawPrecisionBound 2 78 := by
  native_decide

example : coarseK 78 4 = 15 ∧
    quotientSearchBound 2 78 4 = 16 ∧
    coarseRadixDepth 2 78 4 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 78 4) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 78 4 = 90 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 78 4 = 90 ∧
    maximumLayerCompilerRawPrecisionBound 2 78 = 1640 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 78 4 ≤ maximumLayerCompilerRawPrecisionBound 2 78 := by
  native_decide

example : coarseK 79 6 = 11 ∧
    quotientSearchBound 2 79 6 = 12 ∧
    coarseRadixDepth 2 79 6 = 5 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 79 6) = 5 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 79 6 = 56 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 79 6 = 56 ∧
    maximumLayerCompilerRawPrecisionBound 2 79 = 1720 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 79 6 ≤ maximumLayerCompilerRawPrecisionBound 2 79 := by
  native_decide

example : coarseK 79 9 = 7 ∧
    quotientSearchBound 2 79 9 = 8 ∧
    coarseRadixDepth 2 79 9 = 3 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 79 9) = 3 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 79 9 = 30 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 79 9 = 30 ∧
    maximumLayerCompilerRawPrecisionBound 2 79 = 1720 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 79 9 ≤ maximumLayerCompilerRawPrecisionBound 2 79 := by
  native_decide

example : coarseK 80 1 = 39 ∧
    quotientSearchBound 2 80 1 = 40 ∧
    coarseRadixDepth 2 80 1 = 19 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 80 1) = 19 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 80 1 = 462 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 80 1 = 462 ∧
    maximumLayerCompilerRawPrecisionBound 2 80 = 1722 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 80 1 ≤ maximumLayerCompilerRawPrecisionBound 2 80 := by
  native_decide

example : coarseK 97 4 = 19 ∧
    quotientSearchBound 2 97 4 = 20 ∧
    coarseRadixDepth 2 97 4 = 9 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 97 4) = 9 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 97 4 = 132 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 97 4 = 132 ∧
    maximumLayerCompilerRawPrecisionBound 2 97 = 2548 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 97 4 ≤ maximumLayerCompilerRawPrecisionBound 2 97 := by
  native_decide

example : coarseK 97 7 = 12 ∧
    quotientSearchBound 2 97 7 = 13 ∧
    coarseRadixDepth 2 97 7 = 6 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 97 7) = 6 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 97 7 = 70 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 97 7 = 70 ∧
    maximumLayerCompilerRawPrecisionBound 2 97 = 2548 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 97 7 ≤ maximumLayerCompilerRawPrecisionBound 2 97 := by
  native_decide

example : coarseK 97 17 = 5 ∧
    quotientSearchBound 2 97 17 = 6 ∧
    coarseRadixDepth 2 97 17 = 2 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 97 17) = 2 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 97 17 = 20 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 97 17 = 20 ∧
    maximumLayerCompilerRawPrecisionBound 2 97 = 2548 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 97 17 ≤ maximumLayerCompilerRawPrecisionBound 2 97 := by
  native_decide

example : coarseK 127 6 = 18 ∧
    quotientSearchBound 2 127 6 = 19 ∧
    coarseRadixDepth 2 127 6 = 9 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 127 6) = 9 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 127 6 = 130 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 127 6 = 130 ∧
    maximumLayerCompilerRawPrecisionBound 2 127 = 4288 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 127 6 ≤ maximumLayerCompilerRawPrecisionBound 2 127 := by
  native_decide

example : coarseK 128 1 = 63 ∧
    quotientSearchBound 2 128 1 = 64 ∧
    coarseRadixDepth 2 128 1 = 31 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 128 1) = 31 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 128 1 = 1122 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 128 1 = 1122 ∧
    maximumLayerCompilerRawPrecisionBound 2 128 = 4290 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 128 1 ≤ maximumLayerCompilerRawPrecisionBound 2 128 := by
  native_decide

example : coarseK 255 2 = 84 ∧
    quotientSearchBound 2 255 2 = 85 ∧
    coarseRadixDepth 2 255 2 = 42 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 255 2) = 42 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 255 2 = 1978 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 255 2 = 1978 ∧
    maximumLayerCompilerRawPrecisionBound 2 255 = 16768 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 255 2 ≤ maximumLayerCompilerRawPrecisionBound 2 255 := by
  native_decide

example : coarseK 256 7 = 31 ∧
    quotientSearchBound 2 256 7 = 32 ∧
    coarseRadixDepth 2 256 7 = 15 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 256 7) = 15 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 256 7 = 306 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 256 7 = 306 ∧
    maximumLayerCompilerRawPrecisionBound 2 256 = 16770 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 256 7 ≤ maximumLayerCompilerRawPrecisionBound 2 256 := by
  native_decide

example : coarseK 256 17 = 14 ∧
    quotientSearchBound 2 256 17 = 15 ∧
    coarseRadixDepth 2 256 17 = 7 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 256 17) = 7 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 256 17 = 88 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 256 17 = 88 ∧
    maximumLayerCompilerRawPrecisionBound 2 256 = 16770 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 256 17 ≤ maximumLayerCompilerRawPrecisionBound 2 256 := by
  native_decide

example : coarseK 511 4 = 102 ∧
    quotientSearchBound 2 511 4 = 103 ∧
    coarseRadixDepth 2 511 4 = 51 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 511 4) = 51 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 511 4 = 2860 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 511 4 = 2860 ∧
    maximumLayerCompilerRawPrecisionBound 2 511 = 66304 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 511 4 ≤ maximumLayerCompilerRawPrecisionBound 2 511 := by
  native_decide

example : coarseK 511 7 = 63 ∧
    quotientSearchBound 2 511 7 = 64 ∧
    coarseRadixDepth 2 511 7 = 31 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 511 7) = 31 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 511 7 = 1122 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 511 7 = 1122 ∧
    maximumLayerCompilerRawPrecisionBound 2 511 = 66304 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 511 7 ≤ maximumLayerCompilerRawPrecisionBound 2 511 := by
  native_decide

example : coarseK 511 17 = 28 ∧
    quotientSearchBound 2 511 17 = 29 ∧
    coarseRadixDepth 2 511 17 = 14 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 511 17) = 14 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 511 17 = 270 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 511 17 = 270 ∧
    maximumLayerCompilerRawPrecisionBound 2 511 = 66304 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 511 17 ≤ maximumLayerCompilerRawPrecisionBound 2 511 := by
  native_decide

example : coarseK 1024 6 = 146 ∧
    quotientSearchBound 2 1024 6 = 147 ∧
    coarseRadixDepth 2 1024 6 = 73 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 1024 6) = 73 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 1024 6 = 5698 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 1024 6 = 5698 ∧
    maximumLayerCompilerRawPrecisionBound 2 1024 = 263682 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 1024 6 ≤ maximumLayerCompilerRawPrecisionBound 2 1024 := by
  native_decide

example : coarseK 4097 7 = 512 ∧
    quotientSearchBound 2 4097 7 = 513 ∧
    coarseRadixDepth 2 4097 7 = 256 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 4097 7) = 256 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 4097 7 = 66820 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 4097 7 = 66820 ∧
    maximumLayerCompilerRawPrecisionBound 2 4097 = 4204548 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 4097 7 ≤ maximumLayerCompilerRawPrecisionBound 2 4097 := by
  native_decide

example : coarseK 4097 17 = 227 ∧
    quotientSearchBound 2 4097 17 = 228 ∧
    coarseRadixDepth 2 4097 17 = 113 ∧
    lastRadixBlockQuotient 2 (quotientSearchBound 2 4097 17) = 113 ∧
    maximumLayerCompilerPrimeEnvelopeBound 2 4097 17 = 13340 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 4097 17 = 13340 ∧
    maximumLayerCompilerRawPrecisionBound 2 4097 = 4204548 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 4097 17 ≤ maximumLayerCompilerRawPrecisionBound 2 4097 := by
  native_decide

end KomorebiPadic
