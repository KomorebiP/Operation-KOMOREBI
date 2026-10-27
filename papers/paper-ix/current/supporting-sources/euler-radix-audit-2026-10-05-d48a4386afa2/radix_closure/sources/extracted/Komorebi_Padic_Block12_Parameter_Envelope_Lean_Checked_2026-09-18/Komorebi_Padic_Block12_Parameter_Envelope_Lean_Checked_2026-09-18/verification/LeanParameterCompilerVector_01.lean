import KomorebiPadic

namespace KomorebiPadic

example : maximumLayerCompilerTotalTests 2 5 2 = 5 ∧
    maximumLayerCompilerTotalTests 2 5 2 ≤ maximumLayerCompilerParameterEnvelopeBound 2 5 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 5 2 = 6 ∧
    maximumLayerCompilerTotalTests 2 5 2 ≤ maximumLayerCompilerRawPrecisionBound 2 5 ∧
    maximumLayerCompilerRawPrecisionBound 2 5 = 18 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 7 5 = 6 ∧
    maximumLayerCompilerTotalTests 2 7 5 ≤ maximumLayerCompilerParameterEnvelopeBound 2 7 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 7 5 = 6 ∧
    maximumLayerCompilerTotalTests 2 7 5 ≤ maximumLayerCompilerRawPrecisionBound 2 7 ∧
    maximumLayerCompilerRawPrecisionBound 2 7 = 28 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 10 0 = 20 ∧
    maximumLayerCompilerTotalTests 2 10 0 ≤ maximumLayerCompilerParameterEnvelopeBound 2 10 0 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 10 0 = 42 ∧
    maximumLayerCompilerTotalTests 2 10 0 ≤ maximumLayerCompilerRawPrecisionBound 2 10 ∧
    maximumLayerCompilerRawPrecisionBound 2 10 = 42 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 12 3 = 7 ∧
    maximumLayerCompilerTotalTests 2 12 3 ≤ maximumLayerCompilerParameterEnvelopeBound 2 12 3 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 12 3 = 10 ∧
    maximumLayerCompilerTotalTests 2 12 3 ≤ maximumLayerCompilerRawPrecisionBound 2 12 ∧
    maximumLayerCompilerRawPrecisionBound 2 12 = 56 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 14 6 = 5 ∧
    maximumLayerCompilerTotalTests 2 14 6 ≤ maximumLayerCompilerParameterEnvelopeBound 2 14 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 14 6 = 6 ∧
    maximumLayerCompilerTotalTests 2 14 6 ≤ maximumLayerCompilerRawPrecisionBound 2 14 ∧
    maximumLayerCompilerRawPrecisionBound 2 14 = 72 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 17 1 = 20 ∧
    maximumLayerCompilerTotalTests 2 17 1 ≤ maximumLayerCompilerParameterEnvelopeBound 2 17 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 17 1 = 40 ∧
    maximumLayerCompilerTotalTests 2 17 1 ≤ maximumLayerCompilerRawPrecisionBound 2 17 ∧
    maximumLayerCompilerRawPrecisionBound 2 17 = 108 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 19 4 = 9 ∧
    maximumLayerCompilerTotalTests 2 19 4 ≤ maximumLayerCompilerParameterEnvelopeBound 2 19 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 19 4 = 12 ∧
    maximumLayerCompilerTotalTests 2 19 4 ≤ maximumLayerCompilerRawPrecisionBound 2 19 ∧
    maximumLayerCompilerRawPrecisionBound 2 19 = 130 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 24 2 = 18 ∧
    maximumLayerCompilerTotalTests 2 24 2 ≤ maximumLayerCompilerParameterEnvelopeBound 2 24 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 24 2 = 30 ∧
    maximumLayerCompilerTotalTests 2 24 2 ≤ maximumLayerCompilerRawPrecisionBound 2 24 ∧
    maximumLayerCompilerRawPrecisionBound 2 24 = 182 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 26 5 = 11 ∧
    maximumLayerCompilerTotalTests 2 26 5 ≤ maximumLayerCompilerParameterEnvelopeBound 2 26 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 26 5 = 18 ∧
    maximumLayerCompilerTotalTests 2 26 5 ≤ maximumLayerCompilerRawPrecisionBound 2 26 ∧
    maximumLayerCompilerRawPrecisionBound 2 26 = 210 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 29 0 = 65 ∧
    maximumLayerCompilerTotalTests 2 29 0 ≤ maximumLayerCompilerParameterEnvelopeBound 2 29 0 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 29 0 = 270 ∧
    maximumLayerCompilerTotalTests 2 29 0 ≤ maximumLayerCompilerRawPrecisionBound 2 29 ∧
    maximumLayerCompilerRawPrecisionBound 2 29 = 270 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 31 3 = 18 ∧
    maximumLayerCompilerTotalTests 2 31 3 ≤ maximumLayerCompilerParameterEnvelopeBound 2 31 3 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 31 3 = 30 ∧
    maximumLayerCompilerTotalTests 2 31 3 ≤ maximumLayerCompilerRawPrecisionBound 2 31 ∧
    maximumLayerCompilerRawPrecisionBound 2 31 = 304 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 33 6 = 11 ∧
    maximumLayerCompilerTotalTests 2 33 6 ≤ maximumLayerCompilerParameterEnvelopeBound 2 33 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 33 6 = 18 ∧
    maximumLayerCompilerTotalTests 2 33 6 ≤ maximumLayerCompilerRawPrecisionBound 2 33 ∧
    maximumLayerCompilerRawPrecisionBound 2 33 = 340 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 36 1 = 39 ∧
    maximumLayerCompilerTotalTests 2 36 1 ≤ maximumLayerCompilerParameterEnvelopeBound 2 36 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 36 1 = 110 ∧
    maximumLayerCompilerTotalTests 2 36 1 ≤ maximumLayerCompilerRawPrecisionBound 2 36 ∧
    maximumLayerCompilerRawPrecisionBound 2 36 = 380 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 38 4 = 18 ∧
    maximumLayerCompilerTotalTests 2 38 4 ≤ maximumLayerCompilerParameterEnvelopeBound 2 38 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 38 4 = 30 ∧
    maximumLayerCompilerTotalTests 2 38 4 ≤ maximumLayerCompilerRawPrecisionBound 2 38 ∧
    maximumLayerCompilerRawPrecisionBound 2 38 = 420 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 43 2 = 29 ∧
    maximumLayerCompilerTotalTests 2 43 2 ≤ maximumLayerCompilerParameterEnvelopeBound 2 43 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 43 2 = 88 ∧
    maximumLayerCompilerTotalTests 2 43 2 ≤ maximumLayerCompilerRawPrecisionBound 2 43 ∧
    maximumLayerCompilerRawPrecisionBound 2 43 = 550 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 45 5 = 18 ∧
    maximumLayerCompilerTotalTests 2 45 5 ≤ maximumLayerCompilerParameterEnvelopeBound 2 45 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 45 5 = 30 ∧
    maximumLayerCompilerTotalTests 2 45 5 ≤ maximumLayerCompilerRawPrecisionBound 2 45 ∧
    maximumLayerCompilerRawPrecisionBound 2 45 = 598 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 48 0 = 109 ∧
    maximumLayerCompilerTotalTests 2 48 0 ≤ maximumLayerCompilerParameterEnvelopeBound 2 48 0 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 48 0 = 650 ∧
    maximumLayerCompilerTotalTests 2 48 0 ≤ maximumLayerCompilerRawPrecisionBound 2 48 ∧
    maximumLayerCompilerRawPrecisionBound 2 48 = 650 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 50 3 = 28 ∧
    maximumLayerCompilerTotalTests 2 50 3 ≤ maximumLayerCompilerParameterEnvelopeBound 2 50 3 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 50 3 = 70 ∧
    maximumLayerCompilerTotalTests 2 50 3 ≤ maximumLayerCompilerRawPrecisionBound 2 50 ∧
    maximumLayerCompilerRawPrecisionBound 2 50 = 702 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 52 6 = 18 ∧
    maximumLayerCompilerTotalTests 2 52 6 ≤ maximumLayerCompilerParameterEnvelopeBound 2 52 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 52 6 = 30 ∧
    maximumLayerCompilerTotalTests 2 52 6 ≤ maximumLayerCompilerRawPrecisionBound 2 52 ∧
    maximumLayerCompilerRawPrecisionBound 2 52 = 756 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 55 1 = 59 ∧
    maximumLayerCompilerTotalTests 2 55 1 ≤ maximumLayerCompilerParameterEnvelopeBound 2 55 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 55 1 = 240 ∧
    maximumLayerCompilerTotalTests 2 55 1 ≤ maximumLayerCompilerRawPrecisionBound 2 55 ∧
    maximumLayerCompilerRawPrecisionBound 2 55 = 868 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 57 4 = 23 ∧
    maximumLayerCompilerTotalTests 2 57 4 ≤ maximumLayerCompilerParameterEnvelopeBound 2 57 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 57 4 = 56 ∧
    maximumLayerCompilerTotalTests 2 57 4 ≤ maximumLayerCompilerRawPrecisionBound 2 57 ∧
    maximumLayerCompilerRawPrecisionBound 2 57 = 928 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 62 2 = 44 ∧
    maximumLayerCompilerTotalTests 2 62 2 ≤ maximumLayerCompilerParameterEnvelopeBound 2 62 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 62 2 = 154 ∧
    maximumLayerCompilerTotalTests 2 62 2 ≤ maximumLayerCompilerRawPrecisionBound 2 62 ∧
    maximumLayerCompilerRawPrecisionBound 2 62 = 1056 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 64 5 = 23 ∧
    maximumLayerCompilerTotalTests 2 64 5 ≤ maximumLayerCompilerParameterEnvelopeBound 2 64 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 64 5 = 54 ∧
    maximumLayerCompilerTotalTests 2 64 5 ≤ maximumLayerCompilerRawPrecisionBound 2 64 ∧
    maximumLayerCompilerRawPrecisionBound 2 64 = 1122 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 67 0 = 168 ∧
    maximumLayerCompilerTotalTests 2 67 0 ≤ maximumLayerCompilerParameterEnvelopeBound 2 67 0 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 67 0 = 1258 ∧
    maximumLayerCompilerTotalTests 2 67 0 ≤ maximumLayerCompilerRawPrecisionBound 2 67 ∧
    maximumLayerCompilerRawPrecisionBound 2 67 = 1258 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 69 3 = 35 ∧
    maximumLayerCompilerTotalTests 2 69 3 ≤ maximumLayerCompilerParameterEnvelopeBound 2 69 3 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 69 3 = 110 ∧
    maximumLayerCompilerTotalTests 2 69 3 ≤ maximumLayerCompilerRawPrecisionBound 2 69 ∧
    maximumLayerCompilerRawPrecisionBound 2 69 = 1330 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 71 6 = 21 ∧
    maximumLayerCompilerTotalTests 2 71 6 ≤ maximumLayerCompilerParameterEnvelopeBound 2 71 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 71 6 = 54 ∧
    maximumLayerCompilerTotalTests 2 71 6 ≤ maximumLayerCompilerRawPrecisionBound 2 71 ∧
    maximumLayerCompilerRawPrecisionBound 2 71 = 1404 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 74 1 = 81 ∧
    maximumLayerCompilerTotalTests 2 74 1 ≤ maximumLayerCompilerParameterEnvelopeBound 2 74 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 74 1 = 418 ∧
    maximumLayerCompilerTotalTests 2 74 1 ≤ maximumLayerCompilerRawPrecisionBound 2 74 ∧
    maximumLayerCompilerRawPrecisionBound 2 74 = 1482 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 76 4 = 31 ∧
    maximumLayerCompilerTotalTests 2 76 4 ≤ maximumLayerCompilerParameterEnvelopeBound 2 76 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 76 4 = 90 ∧
    maximumLayerCompilerTotalTests 2 76 4 ≤ maximumLayerCompilerRawPrecisionBound 2 76 ∧
    maximumLayerCompilerRawPrecisionBound 2 76 = 1560 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 81 2 = 56 ∧
    maximumLayerCompilerTotalTests 2 81 2 ≤ maximumLayerCompilerParameterEnvelopeBound 2 81 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 81 2 = 238 ∧
    maximumLayerCompilerTotalTests 2 81 2 ≤ maximumLayerCompilerRawPrecisionBound 2 81 ∧
    maximumLayerCompilerRawPrecisionBound 2 81 = 1804 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 83 5 = 29 ∧
    maximumLayerCompilerTotalTests 2 83 5 ≤ maximumLayerCompilerParameterEnvelopeBound 2 83 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 83 5 = 72 ∧
    maximumLayerCompilerTotalTests 2 83 5 ≤ maximumLayerCompilerRawPrecisionBound 2 83 ∧
    maximumLayerCompilerRawPrecisionBound 2 83 = 1890 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 86 0 = 211 ∧
    maximumLayerCompilerTotalTests 2 86 0 ≤ maximumLayerCompilerParameterEnvelopeBound 2 86 0 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 86 0 = 1980 ∧
    maximumLayerCompilerTotalTests 2 86 0 ≤ maximumLayerCompilerRawPrecisionBound 2 86 ∧
    maximumLayerCompilerRawPrecisionBound 2 86 = 1980 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 88 3 = 45 ∧
    maximumLayerCompilerTotalTests 2 88 3 ≤ maximumLayerCompilerParameterEnvelopeBound 2 88 3 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 88 3 = 156 ∧
    maximumLayerCompilerTotalTests 2 88 3 ≤ maximumLayerCompilerRawPrecisionBound 2 88 ∧
    maximumLayerCompilerRawPrecisionBound 2 88 = 2070 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 90 6 = 27 ∧
    maximumLayerCompilerTotalTests 2 90 6 ≤ maximumLayerCompilerParameterEnvelopeBound 2 90 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 90 6 = 70 ∧
    maximumLayerCompilerTotalTests 2 90 6 ≤ maximumLayerCompilerRawPrecisionBound 2 90 ∧
    maximumLayerCompilerRawPrecisionBound 2 90 = 2162 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 93 1 = 99 ∧
    maximumLayerCompilerTotalTests 2 93 1 ≤ maximumLayerCompilerParameterEnvelopeBound 2 93 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 93 1 = 648 ∧
    maximumLayerCompilerTotalTests 2 93 1 ≤ maximumLayerCompilerRawPrecisionBound 2 93 ∧
    maximumLayerCompilerRawPrecisionBound 2 93 = 2350 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 95 4 = 39 ∧
    maximumLayerCompilerTotalTests 2 95 4 ≤ maximumLayerCompilerParameterEnvelopeBound 2 95 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 95 4 = 130 ∧
    maximumLayerCompilerTotalTests 2 95 4 ≤ maximumLayerCompilerRawPrecisionBound 2 95 ∧
    maximumLayerCompilerRawPrecisionBound 2 95 = 2448 := by
  native_decide

example : maximumLayerCompilerTotalTests 2 100 2 = 68 ∧
    maximumLayerCompilerTotalTests 2 100 2 ≤ maximumLayerCompilerParameterEnvelopeBound 2 100 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 2 100 2 = 342 ∧
    maximumLayerCompilerTotalTests 2 100 2 ≤ maximumLayerCompilerRawPrecisionBound 2 100 ∧
    maximumLayerCompilerRawPrecisionBound 2 100 = 2652 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 3 1 = 3 ∧
    maximumLayerCompilerTotalTests 3 3 1 ≤ maximumLayerCompilerParameterEnvelopeBound 3 3 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 3 1 = 5 ∧
    maximumLayerCompilerTotalTests 3 3 1 ≤ maximumLayerCompilerRawPrecisionBound 3 3 ∧
    maximumLayerCompilerRawPrecisionBound 3 3 = 7 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 5 4 = 4 ∧
    maximumLayerCompilerTotalTests 3 5 4 ≤ maximumLayerCompilerParameterEnvelopeBound 3 5 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 5 4 = 5 ∧
    maximumLayerCompilerTotalTests 3 5 4 ≤ maximumLayerCompilerRawPrecisionBound 3 5 ∧
    maximumLayerCompilerRawPrecisionBound 3 5 = 9 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 10 2 = 5 ∧
    maximumLayerCompilerTotalTests 3 10 2 ≤ maximumLayerCompilerParameterEnvelopeBound 3 10 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 10 2 = 7 ∧
    maximumLayerCompilerTotalTests 3 10 2 ≤ maximumLayerCompilerRawPrecisionBound 3 10 ∧
    maximumLayerCompilerRawPrecisionBound 3 10 = 16 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 12 5 = 3 ∧
    maximumLayerCompilerTotalTests 3 12 5 ≤ maximumLayerCompilerParameterEnvelopeBound 3 12 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 12 5 = 5 ∧
    maximumLayerCompilerTotalTests 3 12 5 ≤ maximumLayerCompilerRawPrecisionBound 3 12 ∧
    maximumLayerCompilerRawPrecisionBound 3 12 = 18 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 15 0 = 15 ∧
    maximumLayerCompilerTotalTests 3 15 0 ≤ maximumLayerCompilerParameterEnvelopeBound 3 15 0 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 15 0 = 28 ∧
    maximumLayerCompilerTotalTests 3 15 0 ≤ maximumLayerCompilerRawPrecisionBound 3 15 ∧
    maximumLayerCompilerRawPrecisionBound 3 15 = 28 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 17 3 = 9 ∧
    maximumLayerCompilerTotalTests 3 17 3 ≤ maximumLayerCompilerParameterEnvelopeBound 3 17 3 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 17 3 = 9 ∧
    maximumLayerCompilerTotalTests 3 17 3 ≤ maximumLayerCompilerRawPrecisionBound 3 17 ∧
    maximumLayerCompilerRawPrecisionBound 3 17 = 30 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 19 6 = 6 ∧
    maximumLayerCompilerTotalTests 3 19 6 ≤ maximumLayerCompilerParameterEnvelopeBound 3 19 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 19 6 = 7 ∧
    maximumLayerCompilerTotalTests 3 19 6 ≤ maximumLayerCompilerRawPrecisionBound 3 19 ∧
    maximumLayerCompilerRawPrecisionBound 3 19 = 41 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 22 1 = 14 ∧
    maximumLayerCompilerTotalTests 3 22 1 ≤ maximumLayerCompilerParameterEnvelopeBound 3 22 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 22 1 = 18 ∧
    maximumLayerCompilerTotalTests 3 22 1 ≤ maximumLayerCompilerRawPrecisionBound 3 22 ∧
    maximumLayerCompilerRawPrecisionBound 3 22 = 43 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 24 4 = 8 ∧
    maximumLayerCompilerTotalTests 3 24 4 ≤ maximumLayerCompilerParameterEnvelopeBound 3 24 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 24 4 = 9 ∧
    maximumLayerCompilerTotalTests 3 24 4 ≤ maximumLayerCompilerRawPrecisionBound 3 24 ∧
    maximumLayerCompilerRawPrecisionBound 3 24 = 45 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 29 2 = 11 ∧
    maximumLayerCompilerTotalTests 3 29 2 ≤ maximumLayerCompilerParameterEnvelopeBound 3 29 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 29 2 = 16 ∧
    maximumLayerCompilerTotalTests 3 29 2 ≤ maximumLayerCompilerRawPrecisionBound 3 29 ∧
    maximumLayerCompilerRawPrecisionBound 3 29 = 63 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 31 5 = 8 ∧
    maximumLayerCompilerTotalTests 3 31 5 ≤ maximumLayerCompilerParameterEnvelopeBound 3 31 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 31 5 = 9 ∧
    maximumLayerCompilerTotalTests 3 31 5 ≤ maximumLayerCompilerRawPrecisionBound 3 31 ∧
    maximumLayerCompilerRawPrecisionBound 3 31 = 80 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 34 0 = 38 ∧
    maximumLayerCompilerTotalTests 3 34 0 ≤ maximumLayerCompilerParameterEnvelopeBound 3 34 0 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 34 0 = 82 ∧
    maximumLayerCompilerTotalTests 3 34 0 ≤ maximumLayerCompilerRawPrecisionBound 3 34 ∧
    maximumLayerCompilerRawPrecisionBound 3 34 = 82 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 36 3 = 12 ∧
    maximumLayerCompilerTotalTests 3 36 3 ≤ maximumLayerCompilerParameterEnvelopeBound 3 36 3 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 36 3 = 16 ∧
    maximumLayerCompilerTotalTests 3 36 3 ≤ maximumLayerCompilerRawPrecisionBound 3 36 ∧
    maximumLayerCompilerRawPrecisionBound 3 36 = 84 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 38 6 = 7 ∧
    maximumLayerCompilerTotalTests 3 38 6 ≤ maximumLayerCompilerParameterEnvelopeBound 3 38 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 38 6 = 9 ∧
    maximumLayerCompilerTotalTests 3 38 6 ≤ maximumLayerCompilerRawPrecisionBound 3 38 ∧
    maximumLayerCompilerRawPrecisionBound 3 38 = 104 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 41 1 = 21 ∧
    maximumLayerCompilerTotalTests 3 41 1 ≤ maximumLayerCompilerParameterEnvelopeBound 3 41 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 41 1 = 43 ∧
    maximumLayerCompilerTotalTests 3 41 1 ≤ maximumLayerCompilerRawPrecisionBound 3 41 ∧
    maximumLayerCompilerRawPrecisionBound 3 41 = 108 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 43 4 = 12 ∧
    maximumLayerCompilerTotalTests 3 43 4 ≤ maximumLayerCompilerParameterEnvelopeBound 3 43 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 43 4 = 16 ∧
    maximumLayerCompilerTotalTests 3 43 4 ≤ maximumLayerCompilerRawPrecisionBound 3 43 ∧
    maximumLayerCompilerRawPrecisionBound 3 43 = 131 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 48 2 = 17 ∧
    maximumLayerCompilerTotalTests 3 48 2 ≤ maximumLayerCompilerParameterEnvelopeBound 3 48 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 48 2 = 28 ∧
    maximumLayerCompilerTotalTests 3 48 2 ≤ maximumLayerCompilerRawPrecisionBound 3 48 ∧
    maximumLayerCompilerRawPrecisionBound 3 48 = 135 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 50 5 = 13 ∧
    maximumLayerCompilerTotalTests 3 50 5 ≤ maximumLayerCompilerParameterEnvelopeBound 3 50 5 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 50 5 = 16 ∧
    maximumLayerCompilerTotalTests 3 50 5 ≤ maximumLayerCompilerRawPrecisionBound 3 50 ∧
    maximumLayerCompilerRawPrecisionBound 3 50 = 161 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 53 0 = 58 ∧
    maximumLayerCompilerTotalTests 3 53 0 ≤ maximumLayerCompilerParameterEnvelopeBound 3 53 0 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 53 0 = 165 ∧
    maximumLayerCompilerTotalTests 3 53 0 ≤ maximumLayerCompilerRawPrecisionBound 3 53 ∧
    maximumLayerCompilerRawPrecisionBound 3 53 = 165 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 55 3 = 15 ∧
    maximumLayerCompilerTotalTests 3 55 3 ≤ maximumLayerCompilerParameterEnvelopeBound 3 55 3 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 55 3 = 26 ∧
    maximumLayerCompilerTotalTests 3 55 3 ≤ maximumLayerCompilerRawPrecisionBound 3 55 ∧
    maximumLayerCompilerRawPrecisionBound 3 55 = 194 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 57 6 = 9 ∧
    maximumLayerCompilerTotalTests 3 57 6 ≤ maximumLayerCompilerParameterEnvelopeBound 3 57 6 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 57 6 = 16 ∧
    maximumLayerCompilerTotalTests 3 57 6 ≤ maximumLayerCompilerRawPrecisionBound 3 57 ∧
    maximumLayerCompilerRawPrecisionBound 3 57 = 196 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 60 1 = 31 ∧
    maximumLayerCompilerTotalTests 3 60 1 ≤ maximumLayerCompilerParameterEnvelopeBound 3 60 1 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 60 1 = 63 ∧
    maximumLayerCompilerTotalTests 3 60 1 ≤ maximumLayerCompilerRawPrecisionBound 3 60 ∧
    maximumLayerCompilerRawPrecisionBound 3 60 = 198 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 62 4 = 16 ∧
    maximumLayerCompilerTotalTests 3 62 4 ≤ maximumLayerCompilerParameterEnvelopeBound 3 62 4 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 62 4 = 26 ∧
    maximumLayerCompilerTotalTests 3 62 4 ≤ maximumLayerCompilerRawPrecisionBound 3 62 ∧
    maximumLayerCompilerRawPrecisionBound 3 62 = 230 := by
  native_decide

example : maximumLayerCompilerTotalTests 3 67 2 = 23 ∧
    maximumLayerCompilerTotalTests 3 67 2 ≤ maximumLayerCompilerParameterEnvelopeBound 3 67 2 ∧
    maximumLayerCompilerParameterEnvelopeBound 3 67 2 = 45 ∧
    maximumLayerCompilerTotalTests 3 67 2 ≤ maximumLayerCompilerRawPrecisionBound 3 67 ∧
    maximumLayerCompilerRawPrecisionBound 3 67 = 269 := by
  native_decide

end KomorebiPadic
