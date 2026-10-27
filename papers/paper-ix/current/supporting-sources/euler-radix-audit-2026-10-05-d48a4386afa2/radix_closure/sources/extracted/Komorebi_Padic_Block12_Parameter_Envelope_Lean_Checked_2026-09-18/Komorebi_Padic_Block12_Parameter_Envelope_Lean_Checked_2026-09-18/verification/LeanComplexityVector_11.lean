import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 11/25. -/

example : maximumLayerCompilerTotalTests 5 13 0 = 13 := by native_decide
example : radixRepresentativeBudget 5 4 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 5 13 0 = 13 := by native_decide
example : maximumLayerCompilerTestBound 5 13 0 = 25 := by native_decide
example : maximumLayerCompilerTotalTests 5 13 0 ≤ maximumLayerCompilerBudgetBound 5 13 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 13 0 ≤ maximumLayerCompilerTestBound 5 13 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 13 0 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 5 13 1 = 6 := by native_decide
example : radixRepresentativeBudget 5 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 5 13 1 = 9 := by native_decide
example : maximumLayerCompilerTestBound 5 13 1 = 11 := by native_decide
example : maximumLayerCompilerTotalTests 5 13 1 ≤ maximumLayerCompilerBudgetBound 5 13 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 13 1 ≤ maximumLayerCompilerTestBound 5 13 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 13 1 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 13 3 = 3 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 13 3 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 13 3 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 13 3 ≤ maximumLayerCompilerBudgetBound 5 13 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 13 3 ≤ maximumLayerCompilerTestBound 5 13 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 13 3 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 5 13 7 = 5 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 13 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 13 7 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 13 7 ≤ maximumLayerCompilerBudgetBound 5 13 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 13 7 ≤ maximumLayerCompilerTestBound 5 13 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 13 7 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 5 21 0 = 17 := by native_decide
example : radixRepresentativeBudget 5 6 = 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 21 0 = 18 := by native_decide
example : maximumLayerCompilerTestBound 5 21 0 = 47 := by native_decide
example : maximumLayerCompilerTotalTests 5 21 0 ≤ maximumLayerCompilerBudgetBound 5 21 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 21 0 ≤ maximumLayerCompilerTestBound 5 21 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 21 0 (by decide) (by decide)).totalTests = 17 := by native_decide
example : maximumLayerCompilerTotalTests 5 21 1 = 8 := by native_decide
example : radixRepresentativeBudget 5 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 21 1 = 11 := by native_decide
example : maximumLayerCompilerTestBound 5 21 1 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 5 21 1 ≤ maximumLayerCompilerBudgetBound 5 21 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 21 1 ≤ maximumLayerCompilerTestBound 5 21 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 21 1 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 5 21 3 = 7 := by native_decide
example : radixRepresentativeBudget 5 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 5 21 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 5 21 3 = 11 := by native_decide
example : maximumLayerCompilerTotalTests 5 21 3 ≤ maximumLayerCompilerBudgetBound 5 21 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 21 3 ≤ maximumLayerCompilerTestBound 5 21 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 21 3 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 21 7 = 4 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 21 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 21 7 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 21 7 ≤ maximumLayerCompilerBudgetBound 5 21 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 21 7 ≤ maximumLayerCompilerTestBound 5 21 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 21 7 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 5 34 0 = 22 := by native_decide
example : radixRepresentativeBudget 5 9 = 13 := by native_decide
example : maximumLayerCompilerBudgetBound 5 34 0 = 27 := by native_decide
example : maximumLayerCompilerTestBound 5 34 0 = 95 := by native_decide
example : maximumLayerCompilerTotalTests 5 34 0 ≤ maximumLayerCompilerBudgetBound 5 34 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 34 0 ≤ maximumLayerCompilerTestBound 5 34 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 34 0 (by decide) (by decide)).totalTests = 22 := by native_decide
example : maximumLayerCompilerTotalTests 5 34 1 = 14 := by native_decide
example : radixRepresentativeBudget 5 5 = 5 := by native_decide
example : maximumLayerCompilerBudgetBound 5 34 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 5 34 1 = 35 := by native_decide
example : maximumLayerCompilerTotalTests 5 34 1 ≤ maximumLayerCompilerBudgetBound 5 34 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 34 1 ≤ maximumLayerCompilerTestBound 5 34 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 34 1 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 5 34 3 = 10 := by native_decide
example : radixRepresentativeBudget 5 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 34 3 = 11 := by native_decide
example : maximumLayerCompilerTestBound 5 34 3 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 5 34 3 ≤ maximumLayerCompilerBudgetBound 5 34 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 34 3 ≤ maximumLayerCompilerTestBound 5 34 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 34 3 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 5 34 7 = 8 := by native_decide
example : radixRepresentativeBudget 5 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 5 34 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 5 34 7 = 11 := by native_decide
example : maximumLayerCompilerTotalTests 5 34 7 ≤ maximumLayerCompilerBudgetBound 5 34 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 34 7 ≤ maximumLayerCompilerTestBound 5 34 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 34 7 (by decide) (by decide)).totalTests = 8 := by native_decide
