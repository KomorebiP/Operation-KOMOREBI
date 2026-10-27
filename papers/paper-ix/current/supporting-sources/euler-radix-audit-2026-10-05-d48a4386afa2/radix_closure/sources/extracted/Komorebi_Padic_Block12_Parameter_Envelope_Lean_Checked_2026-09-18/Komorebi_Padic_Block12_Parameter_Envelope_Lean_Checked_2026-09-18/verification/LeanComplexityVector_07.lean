import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 7/25. -/

example : maximumLayerCompilerTotalTests 3 13 0 = 17 := by native_decide
example : radixRepresentativeBudget 3 7 = 12 := by native_decide
example : maximumLayerCompilerBudgetBound 3 13 0 = 22 := by native_decide
example : maximumLayerCompilerTestBound 3 13 0 = 59 := by native_decide
example : maximumLayerCompilerTotalTests 3 13 0 ≤ maximumLayerCompilerBudgetBound 3 13 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 13 0 ≤ maximumLayerCompilerTestBound 3 13 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 13 0 (by decide) (by decide)).totalTests = 17 := by native_decide
example : maximumLayerCompilerTotalTests 3 13 1 = 11 := by native_decide
example : radixRepresentativeBudget 3 4 = 5 := by native_decide
example : maximumLayerCompilerBudgetBound 3 13 1 = 12 := by native_decide
example : maximumLayerCompilerTestBound 3 13 1 = 23 := by native_decide
example : maximumLayerCompilerTotalTests 3 13 1 ≤ maximumLayerCompilerBudgetBound 3 13 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 13 1 ≤ maximumLayerCompilerTestBound 3 13 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 13 1 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 3 13 3 = 5 := by native_decide
example : radixRepresentativeBudget 3 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 3 13 3 = 7 := by native_decide
example : maximumLayerCompilerTestBound 3 13 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 3 13 3 ≤ maximumLayerCompilerBudgetBound 3 13 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 13 3 ≤ maximumLayerCompilerTestBound 3 13 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 13 3 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 13 7 = 3 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 13 7 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 13 7 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 13 7 ≤ maximumLayerCompilerBudgetBound 3 13 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 13 7 ≤ maximumLayerCompilerTestBound 3 13 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 13 7 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 3 21 0 = 21 := by native_decide
example : radixRepresentativeBudget 3 11 = 26 := by native_decide
example : maximumLayerCompilerBudgetBound 3 21 0 = 40 := by native_decide
example : maximumLayerCompilerTestBound 3 21 0 = 135 := by native_decide
example : maximumLayerCompilerTotalTests 3 21 0 ≤ maximumLayerCompilerBudgetBound 3 21 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 21 0 ≤ maximumLayerCompilerTestBound 3 21 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 21 0 (by decide) (by decide)).totalTests = 21 := by native_decide
example : maximumLayerCompilerTotalTests 3 21 1 = 15 := by native_decide
example : radixRepresentativeBudget 3 6 = 9 := by native_decide
example : maximumLayerCompilerBudgetBound 3 21 1 = 18 := by native_decide
example : maximumLayerCompilerTestBound 3 21 1 = 45 := by native_decide
example : maximumLayerCompilerTotalTests 3 21 1 ≤ maximumLayerCompilerBudgetBound 3 21 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 21 1 ≤ maximumLayerCompilerTestBound 3 21 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 21 1 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 3 21 3 = 8 := by native_decide
example : radixRepresentativeBudget 3 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 21 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 3 21 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 3 21 3 ≤ maximumLayerCompilerBudgetBound 3 21 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 21 3 ≤ maximumLayerCompilerTestBound 3 21 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 21 3 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 3 21 7 = 6 := by native_decide
example : radixRepresentativeBudget 3 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 3 21 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 3 21 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 3 21 7 ≤ maximumLayerCompilerBudgetBound 3 21 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 21 7 ≤ maximumLayerCompilerTestBound 3 21 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 21 7 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 3 34 0 = 38 := by native_decide
example : radixRepresentativeBudget 3 17 = 57 := by native_decide
example : maximumLayerCompilerBudgetBound 3 34 0 = 77 := by native_decide
example : maximumLayerCompilerTestBound 3 34 0 = 309 := by native_decide
example : maximumLayerCompilerTotalTests 3 34 0 ≤ maximumLayerCompilerBudgetBound 3 34 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 34 0 ≤ maximumLayerCompilerTestBound 3 34 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 34 0 (by decide) (by decide)).totalTests = 38 := by native_decide
example : maximumLayerCompilerTotalTests 3 34 1 = 21 := by native_decide
example : radixRepresentativeBudget 3 9 = 18 := by native_decide
example : maximumLayerCompilerBudgetBound 3 34 1 = 30 := by native_decide
example : maximumLayerCompilerTestBound 3 34 1 = 93 := by native_decide
example : maximumLayerCompilerTotalTests 3 34 1 ≤ maximumLayerCompilerBudgetBound 3 34 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 34 1 ≤ maximumLayerCompilerTestBound 3 34 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 34 1 (by decide) (by decide)).totalTests = 21 := by native_decide
example : maximumLayerCompilerTotalTests 3 34 3 = 13 := by native_decide
example : radixRepresentativeBudget 3 5 = 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 34 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 3 34 3 = 33 := by native_decide
example : maximumLayerCompilerTotalTests 3 34 3 ≤ maximumLayerCompilerBudgetBound 3 34 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 34 3 ≤ maximumLayerCompilerTestBound 3 34 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 34 3 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 3 34 7 = 8 := by native_decide
example : radixRepresentativeBudget 3 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 34 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 3 34 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 3 34 7 ≤ maximumLayerCompilerBudgetBound 3 34 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 34 7 ≤ maximumLayerCompilerTestBound 3 34 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 34 7 (by decide) (by decide)).totalTests = 8 := by native_decide
