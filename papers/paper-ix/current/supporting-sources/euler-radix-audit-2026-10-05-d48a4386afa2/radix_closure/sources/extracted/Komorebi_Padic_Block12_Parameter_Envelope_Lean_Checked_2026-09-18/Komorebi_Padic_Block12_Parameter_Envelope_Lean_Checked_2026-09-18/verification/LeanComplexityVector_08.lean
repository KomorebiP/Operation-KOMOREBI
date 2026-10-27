import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 8/25. -/

example : maximumLayerCompilerTotalTests 3 55 0 = 62 := by native_decide
example : radixRepresentativeBudget 3 28 = 145 := by native_decide
example : maximumLayerCompilerBudgetBound 3 55 0 = 176 := by native_decide
example : maximumLayerCompilerTestBound 3 55 0 = 815 := by native_decide
example : maximumLayerCompilerTotalTests 3 55 0 ≤ maximumLayerCompilerBudgetBound 3 55 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 55 0 ≤ maximumLayerCompilerTestBound 3 55 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 55 0 (by decide) (by decide)).totalTests = 62 := by native_decide
example : maximumLayerCompilerTotalTests 3 55 1 = 29 := by native_decide
example : radixRepresentativeBudget 3 14 = 40 := by native_decide
example : maximumLayerCompilerBudgetBound 3 55 1 = 57 := by native_decide
example : maximumLayerCompilerTestBound 3 55 1 = 213 := by native_decide
example : maximumLayerCompilerTotalTests 3 55 1 ≤ maximumLayerCompilerBudgetBound 3 55 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 55 1 ≤ maximumLayerCompilerTestBound 3 55 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 55 1 (by decide) (by decide)).totalTests = 29 := by native_decide
example : maximumLayerCompilerTotalTests 3 55 3 = 15 := by native_decide
example : radixRepresentativeBudget 3 7 = 12 := by native_decide
example : maximumLayerCompilerBudgetBound 3 55 3 = 22 := by native_decide
example : maximumLayerCompilerTestBound 3 55 3 = 59 := by native_decide
example : maximumLayerCompilerTotalTests 3 55 3 ≤ maximumLayerCompilerBudgetBound 3 55 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 55 3 ≤ maximumLayerCompilerTestBound 3 55 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 55 3 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 3 55 7 = 10 := by native_decide
example : radixRepresentativeBudget 3 4 = 5 := by native_decide
example : maximumLayerCompilerBudgetBound 3 55 7 = 12 := by native_decide
example : maximumLayerCompilerTestBound 3 55 7 = 23 := by native_decide
example : maximumLayerCompilerTotalTests 3 55 7 ≤ maximumLayerCompilerBudgetBound 3 55 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 55 7 ≤ maximumLayerCompilerTestBound 3 55 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 55 7 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 3 89 0 = 96 := by native_decide
example : radixRepresentativeBudget 3 45 = 360 := by native_decide
example : maximumLayerCompilerBudgetBound 3 89 0 = 408 := by native_decide
example : maximumLayerCompilerTestBound 3 89 0 = 2073 := by native_decide
example : maximumLayerCompilerTotalTests 3 89 0 ≤ maximumLayerCompilerBudgetBound 3 89 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 89 0 ≤ maximumLayerCompilerTestBound 3 89 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 89 0 (by decide) (by decide)).totalTests = 96 := by native_decide
example : maximumLayerCompilerTotalTests 3 89 1 = 45 := by native_decide
example : radixRepresentativeBudget 3 23 = 100 := by native_decide
example : maximumLayerCompilerBudgetBound 3 89 1 = 126 := by native_decide
example : maximumLayerCompilerTestBound 3 89 1 = 555 := by native_decide
example : maximumLayerCompilerTotalTests 3 89 1 ≤ maximumLayerCompilerBudgetBound 3 89 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 89 1 ≤ maximumLayerCompilerTestBound 3 89 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 89 1 (by decide) (by decide)).totalTests = 45 := by native_decide
example : maximumLayerCompilerTotalTests 3 89 3 = 23 := by native_decide
example : radixRepresentativeBudget 3 12 = 30 := by native_decide
example : maximumLayerCompilerBudgetBound 3 89 3 = 45 := by native_decide
example : maximumLayerCompilerTestBound 3 89 3 = 159 := by native_decide
example : maximumLayerCompilerTotalTests 3 89 3 ≤ maximumLayerCompilerBudgetBound 3 89 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 89 3 ≤ maximumLayerCompilerTestBound 3 89 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 89 3 (by decide) (by decide)).totalTests = 23 := by native_decide
example : maximumLayerCompilerTotalTests 3 89 7 = 14 := by native_decide
example : radixRepresentativeBudget 3 6 = 9 := by native_decide
example : maximumLayerCompilerBudgetBound 3 89 7 = 18 := by native_decide
example : maximumLayerCompilerTestBound 3 89 7 = 45 := by native_decide
example : maximumLayerCompilerTotalTests 3 89 7 ≤ maximumLayerCompilerBudgetBound 3 89 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 89 7 ≤ maximumLayerCompilerTestBound 3 89 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 89 7 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 3 144 0 = 157 := by native_decide
example : radixRepresentativeBudget 3 72 = 900 := by native_decide
example : maximumLayerCompilerBudgetBound 3 144 0 = 975 := by native_decide
example : maximumLayerCompilerTestBound 3 144 0 = 5259 := by native_decide
example : maximumLayerCompilerTotalTests 3 144 0 ≤ maximumLayerCompilerBudgetBound 3 144 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 144 0 ≤ maximumLayerCompilerTestBound 3 144 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 144 0 (by decide) (by decide)).totalTests = 157 := by native_decide
example : maximumLayerCompilerTotalTests 3 144 1 = 74 := by native_decide
example : radixRepresentativeBudget 3 36 = 234 := by native_decide
example : maximumLayerCompilerBudgetBound 3 144 1 = 273 := by native_decide
example : maximumLayerCompilerTestBound 3 144 1 = 1335 := by native_decide
example : maximumLayerCompilerTotalTests 3 144 1 ≤ maximumLayerCompilerBudgetBound 3 144 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 144 1 ≤ maximumLayerCompilerTestBound 3 144 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 144 1 (by decide) (by decide)).totalTests = 74 := by native_decide
example : maximumLayerCompilerTotalTests 3 144 3 = 37 := by native_decide
example : radixRepresentativeBudget 3 18 = 63 := by native_decide
example : maximumLayerCompilerBudgetBound 3 144 3 = 84 := by native_decide
example : maximumLayerCompilerTestBound 3 144 3 = 345 := by native_decide
example : maximumLayerCompilerTotalTests 3 144 3 ≤ maximumLayerCompilerBudgetBound 3 144 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 144 3 ≤ maximumLayerCompilerTestBound 3 144 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 144 3 (by decide) (by decide)).totalTests = 37 := by native_decide
example : maximumLayerCompilerTotalTests 3 144 7 = 19 := by native_decide
example : radixRepresentativeBudget 3 9 = 18 := by native_decide
example : maximumLayerCompilerBudgetBound 3 144 7 = 30 := by native_decide
example : maximumLayerCompilerTestBound 3 144 7 = 93 := by native_decide
example : maximumLayerCompilerTotalTests 3 144 7 ≤ maximumLayerCompilerBudgetBound 3 144 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 144 7 ≤ maximumLayerCompilerTestBound 3 144 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 144 7 (by decide) (by decide)).totalTests = 19 := by native_decide
