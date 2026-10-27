import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 18/25. -/

example : maximumLayerCompilerTotalTests 11 4 0 = 9 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 4 0 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 4 0 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 4 0 ≤ maximumLayerCompilerBudgetBound 11 4 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 4 0 ≤ maximumLayerCompilerTestBound 11 4 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 4 0 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 11 4 1 = 11 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 4 1 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 4 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 4 1 ≤ maximumLayerCompilerBudgetBound 11 4 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 4 1 ≤ maximumLayerCompilerTestBound 11 4 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 4 1 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 11 4 3 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 4 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 4 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 4 3 ≤ maximumLayerCompilerBudgetBound 11 4 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 4 3 ≤ maximumLayerCompilerTestBound 11 4 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 4 3 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 4 7 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 4 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 4 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 4 7 ≤ maximumLayerCompilerBudgetBound 11 4 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 4 7 ≤ maximumLayerCompilerTestBound 11 4 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 4 7 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 5 0 = 8 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 5 0 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 5 0 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 5 0 ≤ maximumLayerCompilerBudgetBound 11 5 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 5 0 ≤ maximumLayerCompilerTestBound 11 5 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 5 0 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 11 5 1 = 10 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 5 1 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 5 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 5 1 ≤ maximumLayerCompilerBudgetBound 11 5 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 5 1 ≤ maximumLayerCompilerTestBound 11 5 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 5 1 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 11 5 3 = 11 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 5 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 5 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 5 3 ≤ maximumLayerCompilerBudgetBound 11 5 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 5 3 ≤ maximumLayerCompilerTestBound 11 5 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 5 3 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 11 5 7 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 5 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 5 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 5 7 ≤ maximumLayerCompilerBudgetBound 11 5 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 5 7 ≤ maximumLayerCompilerTestBound 11 5 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 5 7 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 8 0 = 5 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 8 0 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 8 0 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 8 0 ≤ maximumLayerCompilerBudgetBound 11 8 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 8 0 ≤ maximumLayerCompilerTestBound 11 8 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 8 0 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 11 8 1 = 9 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 8 1 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 8 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 8 1 ≤ maximumLayerCompilerBudgetBound 11 8 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 8 1 ≤ maximumLayerCompilerTestBound 11 8 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 8 1 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 11 8 3 = 11 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 8 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 8 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 8 3 ≤ maximumLayerCompilerBudgetBound 11 8 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 8 3 ≤ maximumLayerCompilerTestBound 11 8 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 8 3 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 11 8 7 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 8 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 8 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 8 7 ≤ maximumLayerCompilerBudgetBound 11 8 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 8 7 ≤ maximumLayerCompilerTestBound 11 8 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 8 7 (by decide) (by decide)).totalTests = 12 := by native_decide
