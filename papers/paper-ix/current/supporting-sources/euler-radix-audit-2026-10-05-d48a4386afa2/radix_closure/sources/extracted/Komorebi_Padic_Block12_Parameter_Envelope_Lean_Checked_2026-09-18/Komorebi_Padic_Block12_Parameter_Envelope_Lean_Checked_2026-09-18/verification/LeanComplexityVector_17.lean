import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 17/25. -/

example : maximumLayerCompilerTotalTests 11 1 0 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 1 0 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 1 0 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 1 0 ≤ maximumLayerCompilerBudgetBound 11 1 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 1 0 ≤ maximumLayerCompilerTestBound 11 1 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 1 0 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 1 1 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 1 1 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 1 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 1 1 ≤ maximumLayerCompilerBudgetBound 11 1 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 1 1 ≤ maximumLayerCompilerTestBound 11 1 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 1 1 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 1 3 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 1 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 1 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 1 3 ≤ maximumLayerCompilerBudgetBound 11 1 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 1 3 ≤ maximumLayerCompilerTestBound 11 1 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 1 3 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 1 7 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 1 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 1 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 1 7 ≤ maximumLayerCompilerBudgetBound 11 1 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 1 7 ≤ maximumLayerCompilerTestBound 11 1 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 1 7 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 2 0 = 11 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 2 0 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 2 0 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 2 0 ≤ maximumLayerCompilerBudgetBound 11 2 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 2 0 ≤ maximumLayerCompilerTestBound 11 2 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 2 0 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 11 2 1 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 2 1 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 2 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 2 1 ≤ maximumLayerCompilerBudgetBound 11 2 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 2 1 ≤ maximumLayerCompilerTestBound 11 2 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 2 1 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 2 3 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 2 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 2 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 2 3 ≤ maximumLayerCompilerBudgetBound 11 2 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 2 3 ≤ maximumLayerCompilerTestBound 11 2 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 2 3 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 2 7 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 2 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 2 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 2 7 ≤ maximumLayerCompilerBudgetBound 11 2 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 2 7 ≤ maximumLayerCompilerTestBound 11 2 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 2 7 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 3 0 = 10 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 3 0 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 3 0 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 3 0 ≤ maximumLayerCompilerBudgetBound 11 3 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 3 0 ≤ maximumLayerCompilerTestBound 11 3 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 3 0 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 11 3 1 = 11 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 3 1 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 3 1 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 3 1 ≤ maximumLayerCompilerBudgetBound 11 3 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 3 1 ≤ maximumLayerCompilerTestBound 11 3 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 3 1 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 11 3 3 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 3 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 3 3 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 3 3 ≤ maximumLayerCompilerBudgetBound 11 3 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 3 3 ≤ maximumLayerCompilerTestBound 11 3 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 3 3 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 11 3 7 = 12 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 3 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 3 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 3 7 ≤ maximumLayerCompilerBudgetBound 11 3 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 3 7 ≤ maximumLayerCompilerTestBound 11 3 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 3 7 (by decide) (by decide)).totalTests = 12 := by native_decide
