import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 3/25. -/

example : maximumLayerCompilerTotalTests 2 13 0 = 25 := by native_decide
example : radixRepresentativeBudget 2 13 = 49 := by native_decide
example : maximumLayerCompilerBudgetBound 2 13 0 = 64 := by native_decide
example : maximumLayerCompilerTestBound 2 13 0 = 184 := by native_decide
example : maximumLayerCompilerTotalTests 2 13 0 ≤ maximumLayerCompilerBudgetBound 2 13 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 13 0 ≤ maximumLayerCompilerTestBound 2 13 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 13 0 (by decide) (by decide)).totalTests = 25 := by native_decide
example : maximumLayerCompilerTotalTests 2 13 1 = 13 := by native_decide
example : radixRepresentativeBudget 2 7 = 16 := by native_decide
example : maximumLayerCompilerBudgetBound 2 13 1 = 25 := by native_decide
example : maximumLayerCompilerTestBound 2 13 1 = 58 := by native_decide
example : maximumLayerCompilerTotalTests 2 13 1 ≤ maximumLayerCompilerBudgetBound 2 13 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 13 1 ≤ maximumLayerCompilerTestBound 2 13 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 13 1 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 2 13 3 = 7 := by native_decide
example : radixRepresentativeBudget 2 4 = 6 := by native_decide
example : maximumLayerCompilerBudgetBound 2 13 3 = 12 := by native_decide
example : maximumLayerCompilerTestBound 2 13 3 = 22 := by native_decide
example : maximumLayerCompilerTotalTests 2 13 3 ≤ maximumLayerCompilerBudgetBound 2 13 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 13 3 ≤ maximumLayerCompilerTestBound 2 13 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 13 3 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 2 13 7 = 5 := by native_decide
example : radixRepresentativeBudget 2 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 2 13 7 = 6 := by native_decide
example : maximumLayerCompilerTestBound 2 13 7 = 8 := by native_decide
example : maximumLayerCompilerTotalTests 2 13 7 ≤ maximumLayerCompilerBudgetBound 2 13 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 13 7 ≤ maximumLayerCompilerTestBound 2 13 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 13 7 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 2 21 0 = 44 := by native_decide
example : radixRepresentativeBudget 2 21 = 121 := by native_decide
example : maximumLayerCompilerBudgetBound 2 21 0 = 144 := by native_decide
example : maximumLayerCompilerTestBound 2 21 0 = 464 := by native_decide
example : maximumLayerCompilerTotalTests 2 21 0 ≤ maximumLayerCompilerBudgetBound 2 21 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 21 0 ≤ maximumLayerCompilerTestBound 2 21 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 21 0 (by decide) (by decide)).totalTests = 44 := by native_decide
example : maximumLayerCompilerTotalTests 2 21 1 = 21 := by native_decide
example : radixRepresentativeBudget 2 11 = 36 := by native_decide
example : maximumLayerCompilerBudgetBound 2 21 1 = 49 := by native_decide
example : maximumLayerCompilerTestBound 2 21 1 = 134 := by native_decide
example : maximumLayerCompilerTotalTests 2 21 1 ≤ maximumLayerCompilerBudgetBound 2 21 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 21 1 ≤ maximumLayerCompilerTestBound 2 21 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 21 1 (by decide) (by decide)).totalTests = 21 := by native_decide
example : maximumLayerCompilerTotalTests 2 21 3 = 11 := by native_decide
example : radixRepresentativeBudget 2 6 = 12 := by native_decide
example : maximumLayerCompilerBudgetBound 2 21 3 = 20 := by native_decide
example : maximumLayerCompilerTestBound 2 21 3 = 44 := by native_decide
example : maximumLayerCompilerTotalTests 2 21 3 ≤ maximumLayerCompilerBudgetBound 2 21 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 21 3 ≤ maximumLayerCompilerTestBound 2 21 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 21 3 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 2 21 7 = 7 := by native_decide
example : radixRepresentativeBudget 2 3 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 2 21 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 2 21 7 = 14 := by native_decide
example : maximumLayerCompilerTotalTests 2 21 7 ≤ maximumLayerCompilerBudgetBound 2 21 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 21 7 ≤ maximumLayerCompilerTestBound 2 21 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 21 7 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 2 34 0 = 79 := by native_decide
example : radixRepresentativeBudget 2 34 = 306 := by native_decide
example : maximumLayerCompilerBudgetBound 2 34 0 = 342 := by native_decide
example : maximumLayerCompilerTestBound 2 34 0 = 1192 := by native_decide
example : maximumLayerCompilerTotalTests 2 34 0 ≤ maximumLayerCompilerBudgetBound 2 34 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 34 0 ≤ maximumLayerCompilerTestBound 2 34 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 34 0 (by decide) (by decide)).totalTests = 79 := by native_decide
example : maximumLayerCompilerTotalTests 2 34 1 = 36 := by native_decide
example : radixRepresentativeBudget 2 17 = 81 := by native_decide
example : maximumLayerCompilerBudgetBound 2 34 1 = 100 := by native_decide
example : maximumLayerCompilerTestBound 2 34 1 = 308 := by native_decide
example : maximumLayerCompilerTotalTests 2 34 1 ≤ maximumLayerCompilerBudgetBound 2 34 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 34 1 ≤ maximumLayerCompilerTestBound 2 34 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 34 1 (by decide) (by decide)).totalTests = 36 := by native_decide
example : maximumLayerCompilerTotalTests 2 34 3 = 19 := by native_decide
example : radixRepresentativeBudget 2 9 = 25 := by native_decide
example : maximumLayerCompilerBudgetBound 2 34 3 = 36 := by native_decide
example : maximumLayerCompilerTestBound 2 34 3 = 92 := by native_decide
example : maximumLayerCompilerTotalTests 2 34 3 ≤ maximumLayerCompilerBudgetBound 2 34 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 34 3 ≤ maximumLayerCompilerTestBound 2 34 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 34 3 (by decide) (by decide)).totalTests = 19 := by native_decide
example : maximumLayerCompilerTotalTests 2 34 7 = 11 := by native_decide
example : radixRepresentativeBudget 2 5 = 9 := by native_decide
example : maximumLayerCompilerBudgetBound 2 34 7 = 16 := by native_decide
example : maximumLayerCompilerTestBound 2 34 7 = 32 := by native_decide
example : maximumLayerCompilerTotalTests 2 34 7 ≤ maximumLayerCompilerBudgetBound 2 34 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 34 7 ≤ maximumLayerCompilerTestBound 2 34 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 34 7 (by decide) (by decide)).totalTests = 11 := by native_decide
