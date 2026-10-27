import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 19/25. -/

example : maximumLayerCompilerTotalTests 11 13 0 = 12 := by native_decide
example : radixRepresentativeBudget 11 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 11 13 0 = 15 := by native_decide
example : maximumLayerCompilerTestBound 11 13 0 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 11 13 0 ≤ maximumLayerCompilerBudgetBound 11 13 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 13 0 ≤ maximumLayerCompilerTestBound 11 13 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 13 0 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 13 1 = 6 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 13 1 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 13 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 13 1 ≤ maximumLayerCompilerBudgetBound 11 13 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 13 1 ≤ maximumLayerCompilerTestBound 11 13 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 13 1 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 11 13 3 = 9 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 13 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 13 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 13 3 ≤ maximumLayerCompilerBudgetBound 11 13 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 13 3 ≤ maximumLayerCompilerTestBound 11 13 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 13 3 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 11 13 7 = 11 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 13 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 13 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 13 7 ≤ maximumLayerCompilerBudgetBound 11 13 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 13 7 ≤ maximumLayerCompilerTestBound 11 13 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 13 7 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 11 21 0 = 17 := by native_decide
example : radixRepresentativeBudget 11 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 21 0 = 17 := by native_decide
example : maximumLayerCompilerTestBound 11 21 0 = 23 := by native_decide
example : maximumLayerCompilerTotalTests 11 21 0 ≤ maximumLayerCompilerBudgetBound 11 21 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 21 0 ≤ maximumLayerCompilerTestBound 11 21 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 21 0 (by decide) (by decide)).totalTests = 17 := by native_decide
example : maximumLayerCompilerTotalTests 11 21 1 = 15 := by native_decide
example : radixRepresentativeBudget 11 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 11 21 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 11 21 1 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 11 21 1 ≤ maximumLayerCompilerBudgetBound 11 21 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 21 1 ≤ maximumLayerCompilerTestBound 11 21 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 21 1 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 11 21 3 = 7 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 21 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 21 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 21 3 ≤ maximumLayerCompilerBudgetBound 11 21 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 21 3 ≤ maximumLayerCompilerTestBound 11 21 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 21 3 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 11 21 7 = 10 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 21 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 21 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 21 7 ≤ maximumLayerCompilerBudgetBound 11 21 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 21 7 ≤ maximumLayerCompilerTestBound 11 21 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 21 7 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 11 34 0 = 15 := by native_decide
example : radixRepresentativeBudget 11 4 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 11 34 0 = 19 := by native_decide
example : maximumLayerCompilerTestBound 11 34 0 = 31 := by native_decide
example : maximumLayerCompilerTotalTests 11 34 0 ≤ maximumLayerCompilerBudgetBound 11 34 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 34 0 ≤ maximumLayerCompilerTestBound 11 34 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 34 0 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 11 34 1 = 8 := by native_decide
example : radixRepresentativeBudget 11 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 11 34 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 11 34 1 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 11 34 1 ≤ maximumLayerCompilerBudgetBound 11 34 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 34 1 ≤ maximumLayerCompilerTestBound 11 34 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 34 1 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 11 34 3 = 4 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 34 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 34 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 34 3 ≤ maximumLayerCompilerBudgetBound 11 34 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 34 3 ≤ maximumLayerCompilerTestBound 11 34 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 34 3 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 11 34 7 = 8 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 34 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 34 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 34 7 ≤ maximumLayerCompilerBudgetBound 11 34 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 34 7 ≤ maximumLayerCompilerTestBound 11 34 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 34 7 (by decide) (by decide)).totalTests = 8 := by native_decide
