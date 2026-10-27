import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 10/25. -/

example : maximumLayerCompilerTotalTests 5 4 0 = 3 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 4 0 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 4 0 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 4 0 ≤ maximumLayerCompilerBudgetBound 5 4 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 4 0 ≤ maximumLayerCompilerTestBound 5 4 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 4 0 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 5 4 1 = 5 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 4 1 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 4 1 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 4 1 ≤ maximumLayerCompilerBudgetBound 5 4 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 4 1 ≤ maximumLayerCompilerTestBound 5 4 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 4 1 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 5 4 3 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 4 3 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 4 3 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 4 3 ≤ maximumLayerCompilerBudgetBound 5 4 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 4 3 ≤ maximumLayerCompilerTestBound 5 4 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 4 3 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 4 7 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 4 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 4 7 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 4 7 ≤ maximumLayerCompilerBudgetBound 5 4 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 4 7 ≤ maximumLayerCompilerTestBound 5 4 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 4 7 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 5 0 = 9 := by native_decide
example : radixRepresentativeBudget 5 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 5 5 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 5 5 0 = 11 := by native_decide
example : maximumLayerCompilerTotalTests 5 5 0 ≤ maximumLayerCompilerBudgetBound 5 5 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 5 0 ≤ maximumLayerCompilerTestBound 5 5 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 5 0 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 5 5 1 = 4 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 5 1 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 5 1 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 5 1 ≤ maximumLayerCompilerBudgetBound 5 5 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 5 1 ≤ maximumLayerCompilerTestBound 5 5 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 5 1 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 5 5 3 = 5 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 5 3 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 5 3 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 5 3 ≤ maximumLayerCompilerBudgetBound 5 5 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 5 3 ≤ maximumLayerCompilerTestBound 5 5 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 5 3 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 5 5 7 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 5 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 5 7 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 5 7 ≤ maximumLayerCompilerBudgetBound 5 5 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 5 7 ≤ maximumLayerCompilerTestBound 5 5 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 5 7 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 8 0 = 5 := by native_decide
example : radixRepresentativeBudget 5 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 5 8 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 5 8 0 = 11 := by native_decide
example : maximumLayerCompilerTotalTests 5 8 0 ≤ maximumLayerCompilerBudgetBound 5 8 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 8 0 ≤ maximumLayerCompilerTestBound 5 8 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 8 0 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 5 8 1 = 3 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 8 1 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 8 1 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 8 1 ≤ maximumLayerCompilerBudgetBound 5 8 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 8 1 ≤ maximumLayerCompilerTestBound 5 8 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 8 1 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 5 8 3 = 5 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 8 3 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 8 3 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 8 3 ≤ maximumLayerCompilerBudgetBound 5 8 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 8 3 ≤ maximumLayerCompilerTestBound 5 8 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 8 3 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 5 8 7 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 8 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 8 7 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 8 7 ≤ maximumLayerCompilerBudgetBound 5 8 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 8 7 ≤ maximumLayerCompilerTestBound 5 8 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 8 7 (by decide) (by decide)).totalTests = 6 := by native_decide
