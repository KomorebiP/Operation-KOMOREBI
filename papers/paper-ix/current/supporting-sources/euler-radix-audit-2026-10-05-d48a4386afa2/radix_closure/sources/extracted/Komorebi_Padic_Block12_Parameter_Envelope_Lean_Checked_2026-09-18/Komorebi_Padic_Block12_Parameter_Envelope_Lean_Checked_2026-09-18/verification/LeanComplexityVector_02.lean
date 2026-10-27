import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 2/25. -/

example : maximumLayerCompilerTotalTests 2 4 0 = 7 := by native_decide
example : radixRepresentativeBudget 2 4 = 6 := by native_decide
example : maximumLayerCompilerBudgetBound 2 4 0 = 12 := by native_decide
example : maximumLayerCompilerTestBound 2 4 0 = 22 := by native_decide
example : maximumLayerCompilerTotalTests 2 4 0 ≤ maximumLayerCompilerBudgetBound 2 4 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 4 0 ≤ maximumLayerCompilerTestBound 2 4 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 4 0 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 2 4 1 = 5 := by native_decide
example : radixRepresentativeBudget 2 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 2 4 1 = 6 := by native_decide
example : maximumLayerCompilerTestBound 2 4 1 = 8 := by native_decide
example : maximumLayerCompilerTotalTests 2 4 1 ≤ maximumLayerCompilerBudgetBound 2 4 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 4 1 ≤ maximumLayerCompilerTestBound 2 4 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 4 1 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 2 4 3 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 4 3 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 4 3 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 4 3 ≤ maximumLayerCompilerBudgetBound 2 4 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 4 3 ≤ maximumLayerCompilerTestBound 2 4 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 4 3 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 4 7 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 4 7 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 4 7 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 4 7 ≤ maximumLayerCompilerBudgetBound 2 4 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 4 7 ≤ maximumLayerCompilerTestBound 2 4 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 4 7 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 5 0 = 12 := by native_decide
example : radixRepresentativeBudget 2 5 = 9 := by native_decide
example : maximumLayerCompilerBudgetBound 2 5 0 = 16 := by native_decide
example : maximumLayerCompilerTestBound 2 5 0 = 32 := by native_decide
example : maximumLayerCompilerTotalTests 2 5 0 ≤ maximumLayerCompilerBudgetBound 2 5 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 5 0 ≤ maximumLayerCompilerTestBound 2 5 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 5 0 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 2 5 1 = 8 := by native_decide
example : radixRepresentativeBudget 2 3 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 2 5 1 = 9 := by native_decide
example : maximumLayerCompilerTestBound 2 5 1 = 14 := by native_decide
example : maximumLayerCompilerTotalTests 2 5 1 ≤ maximumLayerCompilerBudgetBound 2 5 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 5 1 ≤ maximumLayerCompilerTestBound 2 5 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 5 1 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 2 5 3 = 6 := by native_decide
example : radixRepresentativeBudget 2 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 2 5 3 = 6 := by native_decide
example : maximumLayerCompilerTestBound 2 5 3 = 8 := by native_decide
example : maximumLayerCompilerTotalTests 2 5 3 ≤ maximumLayerCompilerBudgetBound 2 5 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 5 3 ≤ maximumLayerCompilerTestBound 2 5 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 5 3 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 2 5 7 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 5 7 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 5 7 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 5 7 ≤ maximumLayerCompilerBudgetBound 2 5 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 5 7 ≤ maximumLayerCompilerTestBound 2 5 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 5 7 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 8 0 = 17 := by native_decide
example : radixRepresentativeBudget 2 8 = 20 := by native_decide
example : maximumLayerCompilerBudgetBound 2 8 0 = 30 := by native_decide
example : maximumLayerCompilerTestBound 2 8 0 = 74 := by native_decide
example : maximumLayerCompilerTotalTests 2 8 0 ≤ maximumLayerCompilerBudgetBound 2 8 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 8 0 ≤ maximumLayerCompilerTestBound 2 8 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 8 0 (by decide) (by decide)).totalTests = 17 := by native_decide
example : maximumLayerCompilerTotalTests 2 8 1 = 10 := by native_decide
example : radixRepresentativeBudget 2 4 = 6 := by native_decide
example : maximumLayerCompilerBudgetBound 2 8 1 = 12 := by native_decide
example : maximumLayerCompilerTestBound 2 8 1 = 22 := by native_decide
example : maximumLayerCompilerTotalTests 2 8 1 ≤ maximumLayerCompilerBudgetBound 2 8 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 8 1 ≤ maximumLayerCompilerTestBound 2 8 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 8 1 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 2 8 3 = 5 := by native_decide
example : radixRepresentativeBudget 2 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 2 8 3 = 6 := by native_decide
example : maximumLayerCompilerTestBound 2 8 3 = 8 := by native_decide
example : maximumLayerCompilerTotalTests 2 8 3 ≤ maximumLayerCompilerBudgetBound 2 8 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 8 3 ≤ maximumLayerCompilerTestBound 2 8 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 8 3 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 2 8 7 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 8 7 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 8 7 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 8 7 ≤ maximumLayerCompilerBudgetBound 2 8 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 8 7 ≤ maximumLayerCompilerTestBound 2 8 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 8 7 (by decide) (by decide)).totalTests = 3 := by native_decide
