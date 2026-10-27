import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 22/25. -/

example : maximumLayerCompilerTotalTests 13 4 0 = 11 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 4 0 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 4 0 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 4 0 ≤ maximumLayerCompilerBudgetBound 13 4 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 4 0 ≤ maximumLayerCompilerTestBound 13 4 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 4 0 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 13 4 1 = 13 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 4 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 4 1 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 4 1 ≤ maximumLayerCompilerBudgetBound 13 4 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 4 1 ≤ maximumLayerCompilerTestBound 13 4 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 4 1 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 13 4 3 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 4 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 4 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 4 3 ≤ maximumLayerCompilerBudgetBound 13 4 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 4 3 ≤ maximumLayerCompilerTestBound 13 4 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 4 3 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 4 7 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 4 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 4 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 4 7 ≤ maximumLayerCompilerBudgetBound 13 4 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 4 7 ≤ maximumLayerCompilerTestBound 13 4 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 4 7 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 5 0 = 10 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 5 0 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 5 0 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 5 0 ≤ maximumLayerCompilerBudgetBound 13 5 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 5 0 ≤ maximumLayerCompilerTestBound 13 5 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 5 0 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 13 5 1 = 12 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 5 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 5 1 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 5 1 ≤ maximumLayerCompilerBudgetBound 13 5 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 5 1 ≤ maximumLayerCompilerTestBound 13 5 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 5 1 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 13 5 3 = 13 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 5 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 5 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 5 3 ≤ maximumLayerCompilerBudgetBound 13 5 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 5 3 ≤ maximumLayerCompilerTestBound 13 5 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 5 3 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 13 5 7 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 5 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 5 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 5 7 ≤ maximumLayerCompilerBudgetBound 13 5 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 5 7 ≤ maximumLayerCompilerTestBound 13 5 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 5 7 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 8 0 = 7 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 8 0 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 8 0 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 8 0 ≤ maximumLayerCompilerBudgetBound 13 8 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 8 0 ≤ maximumLayerCompilerTestBound 13 8 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 8 0 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 13 8 1 = 11 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 8 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 8 1 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 8 1 ≤ maximumLayerCompilerBudgetBound 13 8 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 8 1 ≤ maximumLayerCompilerTestBound 13 8 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 8 1 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 13 8 3 = 13 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 8 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 8 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 8 3 ≤ maximumLayerCompilerBudgetBound 13 8 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 8 3 ≤ maximumLayerCompilerTestBound 13 8 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 8 3 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 13 8 7 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 8 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 8 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 8 7 ≤ maximumLayerCompilerBudgetBound 13 8 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 8 7 ≤ maximumLayerCompilerTestBound 13 8 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 8 7 (by decide) (by decide)).totalTests = 14 := by native_decide
