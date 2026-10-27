import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 14/25. -/

example : maximumLayerCompilerTotalTests 7 4 0 = 5 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 4 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 4 0 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 4 0 ≤ maximumLayerCompilerBudgetBound 7 4 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 4 0 ≤ maximumLayerCompilerTestBound 7 4 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 4 0 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 7 4 1 = 7 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 4 1 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 4 1 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 4 1 ≤ maximumLayerCompilerBudgetBound 7 4 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 4 1 ≤ maximumLayerCompilerTestBound 7 4 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 4 1 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 7 4 3 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 4 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 4 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 4 3 ≤ maximumLayerCompilerBudgetBound 7 4 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 4 3 ≤ maximumLayerCompilerTestBound 7 4 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 4 3 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 4 7 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 4 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 4 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 4 7 ≤ maximumLayerCompilerBudgetBound 7 4 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 4 7 ≤ maximumLayerCompilerTestBound 7 4 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 4 7 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 5 0 = 4 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 5 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 5 0 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 5 0 ≤ maximumLayerCompilerBudgetBound 7 5 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 5 0 ≤ maximumLayerCompilerTestBound 7 5 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 5 0 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 7 5 1 = 6 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 5 1 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 5 1 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 5 1 ≤ maximumLayerCompilerBudgetBound 7 5 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 5 1 ≤ maximumLayerCompilerTestBound 7 5 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 5 1 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 7 5 3 = 7 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 5 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 5 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 5 3 ≤ maximumLayerCompilerBudgetBound 7 5 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 5 3 ≤ maximumLayerCompilerTestBound 7 5 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 5 3 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 7 5 7 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 5 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 5 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 5 7 ≤ maximumLayerCompilerBudgetBound 7 5 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 5 7 ≤ maximumLayerCompilerTestBound 7 5 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 5 7 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 8 0 = 9 := by native_decide
example : radixRepresentativeBudget 7 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 7 8 0 = 11 := by native_decide
example : maximumLayerCompilerTestBound 7 8 0 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 8 0 ≤ maximumLayerCompilerBudgetBound 7 8 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 8 0 ≤ maximumLayerCompilerTestBound 7 8 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 8 0 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 8 1 = 5 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 8 1 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 8 1 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 8 1 ≤ maximumLayerCompilerBudgetBound 7 8 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 8 1 ≤ maximumLayerCompilerTestBound 7 8 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 8 1 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 7 8 3 = 7 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 8 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 8 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 8 3 ≤ maximumLayerCompilerBudgetBound 7 8 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 8 3 ≤ maximumLayerCompilerTestBound 7 8 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 8 3 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 7 8 7 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 8 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 8 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 8 7 ≤ maximumLayerCompilerBudgetBound 7 8 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 8 7 ≤ maximumLayerCompilerTestBound 7 8 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 8 7 (by decide) (by decide)).totalTests = 8 := by native_decide
