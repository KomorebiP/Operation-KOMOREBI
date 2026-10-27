import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 15/25. -/

example : maximumLayerCompilerTotalTests 7 13 0 = 13 := by native_decide
example : radixRepresentativeBudget 7 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 13 0 = 13 := by native_decide
example : maximumLayerCompilerTestBound 7 13 0 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 7 13 0 ≤ maximumLayerCompilerBudgetBound 7 13 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 13 0 ≤ maximumLayerCompilerTestBound 7 13 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 13 0 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 13 1 = 11 := by native_decide
example : radixRepresentativeBudget 7 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 7 13 1 = 11 := by native_decide
example : maximumLayerCompilerTestBound 7 13 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 13 1 ≤ maximumLayerCompilerBudgetBound 7 13 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 13 1 ≤ maximumLayerCompilerTestBound 7 13 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 13 1 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 7 13 3 = 5 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 13 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 13 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 13 3 ≤ maximumLayerCompilerBudgetBound 7 13 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 13 3 ≤ maximumLayerCompilerTestBound 7 13 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 13 3 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 7 13 7 = 7 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 13 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 13 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 13 7 ≤ maximumLayerCompilerBudgetBound 7 13 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 13 7 ≤ maximumLayerCompilerTestBound 7 13 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 13 7 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 7 21 0 = 13 := by native_decide
example : radixRepresentativeBudget 7 4 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 7 21 0 = 15 := by native_decide
example : maximumLayerCompilerTestBound 7 21 0 = 27 := by native_decide
example : maximumLayerCompilerTotalTests 7 21 0 ≤ maximumLayerCompilerBudgetBound 7 21 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 21 0 ≤ maximumLayerCompilerTestBound 7 21 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 21 0 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 21 1 = 6 := by native_decide
example : radixRepresentativeBudget 7 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 7 21 1 = 11 := by native_decide
example : maximumLayerCompilerTestBound 7 21 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 21 1 ≤ maximumLayerCompilerBudgetBound 7 21 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 21 1 ≤ maximumLayerCompilerTestBound 7 21 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 21 1 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 7 21 3 = 3 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 21 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 21 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 21 3 ≤ maximumLayerCompilerBudgetBound 7 21 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 21 3 ≤ maximumLayerCompilerTestBound 7 21 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 21 3 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 7 21 7 = 6 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 21 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 21 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 21 7 ≤ maximumLayerCompilerBudgetBound 7 21 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 21 7 ≤ maximumLayerCompilerTestBound 7 21 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 21 7 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 7 34 0 = 16 := by native_decide
example : radixRepresentativeBudget 7 6 = 6 := by native_decide
example : maximumLayerCompilerBudgetBound 7 34 0 = 19 := by native_decide
example : maximumLayerCompilerTestBound 7 34 0 = 49 := by native_decide
example : maximumLayerCompilerTotalTests 7 34 0 ≤ maximumLayerCompilerBudgetBound 7 34 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 34 0 ≤ maximumLayerCompilerTestBound 7 34 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 34 0 (by decide) (by decide)).totalTests = 16 := by native_decide
example : maximumLayerCompilerTotalTests 7 34 1 = 8 := by native_decide
example : radixRepresentativeBudget 7 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 34 1 = 13 := by native_decide
example : maximumLayerCompilerTestBound 7 34 1 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 7 34 1 ≤ maximumLayerCompilerBudgetBound 7 34 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 34 1 ≤ maximumLayerCompilerTestBound 7 34 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 34 1 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 34 3 = 8 := by native_decide
example : radixRepresentativeBudget 7 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 7 34 3 = 11 := by native_decide
example : maximumLayerCompilerTestBound 7 34 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 34 3 ≤ maximumLayerCompilerBudgetBound 7 34 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 34 3 ≤ maximumLayerCompilerTestBound 7 34 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 34 3 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 34 7 = 4 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 34 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 34 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 34 7 ≤ maximumLayerCompilerBudgetBound 7 34 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 34 7 ≤ maximumLayerCompilerTestBound 7 34 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 34 7 (by decide) (by decide)).totalTests = 4 := by native_decide
