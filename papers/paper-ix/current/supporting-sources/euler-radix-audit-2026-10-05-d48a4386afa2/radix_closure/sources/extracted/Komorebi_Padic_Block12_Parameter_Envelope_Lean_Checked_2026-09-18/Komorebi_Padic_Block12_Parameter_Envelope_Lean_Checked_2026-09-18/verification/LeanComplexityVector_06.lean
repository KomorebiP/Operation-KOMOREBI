import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 6/25. -/

example : maximumLayerCompilerTotalTests 3 4 0 = 5 := by native_decide
example : radixRepresentativeBudget 3 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 3 4 0 = 7 := by native_decide
example : maximumLayerCompilerTestBound 3 4 0 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 3 4 0 ≤ maximumLayerCompilerBudgetBound 3 4 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 4 0 ≤ maximumLayerCompilerTestBound 3 4 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 4 0 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 4 1 = 3 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 4 1 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 4 1 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 4 1 ≤ maximumLayerCompilerBudgetBound 3 4 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 4 1 ≤ maximumLayerCompilerTestBound 3 4 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 4 1 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 3 4 3 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 4 3 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 4 3 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 4 3 ≤ maximumLayerCompilerBudgetBound 3 4 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 4 3 ≤ maximumLayerCompilerTestBound 3 4 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 4 3 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 4 7 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 4 7 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 4 7 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 4 7 ≤ maximumLayerCompilerBudgetBound 3 4 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 4 7 ≤ maximumLayerCompilerTestBound 3 4 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 4 7 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 5 0 = 9 := by native_decide
example : radixRepresentativeBudget 3 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 5 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 3 5 0 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 3 5 0 ≤ maximumLayerCompilerBudgetBound 3 5 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 5 0 ≤ maximumLayerCompilerTestBound 3 5 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 5 0 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 3 5 1 = 7 := by native_decide
example : radixRepresentativeBudget 3 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 3 5 1 = 7 := by native_decide
example : maximumLayerCompilerTestBound 3 5 1 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 3 5 1 ≤ maximumLayerCompilerBudgetBound 3 5 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 5 1 ≤ maximumLayerCompilerTestBound 3 5 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 5 1 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 3 5 3 = 3 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 5 3 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 5 3 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 5 3 ≤ maximumLayerCompilerBudgetBound 3 5 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 5 3 ≤ maximumLayerCompilerTestBound 3 5 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 5 3 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 3 5 7 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 5 7 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 5 7 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 5 7 ≤ maximumLayerCompilerBudgetBound 3 5 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 5 7 ≤ maximumLayerCompilerTestBound 3 5 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 5 7 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 8 0 = 10 := by native_decide
example : radixRepresentativeBudget 3 4 = 5 := by native_decide
example : maximumLayerCompilerBudgetBound 3 8 0 = 12 := by native_decide
example : maximumLayerCompilerTestBound 3 8 0 = 23 := by native_decide
example : maximumLayerCompilerTotalTests 3 8 0 ≤ maximumLayerCompilerBudgetBound 3 8 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 8 0 ≤ maximumLayerCompilerTestBound 3 8 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 8 0 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 3 8 1 = 5 := by native_decide
example : radixRepresentativeBudget 3 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 3 8 1 = 7 := by native_decide
example : maximumLayerCompilerTestBound 3 8 1 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 3 8 1 ≤ maximumLayerCompilerBudgetBound 3 8 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 8 1 ≤ maximumLayerCompilerTestBound 3 8 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 8 1 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 8 3 = 3 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 8 3 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 8 3 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 8 3 ≤ maximumLayerCompilerBudgetBound 3 8 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 8 3 ≤ maximumLayerCompilerTestBound 3 8 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 8 3 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 3 8 7 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 8 7 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 8 7 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 8 7 ≤ maximumLayerCompilerBudgetBound 3 8 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 8 7 ≤ maximumLayerCompilerTestBound 3 8 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 8 7 (by decide) (by decide)).totalTests = 4 := by native_decide
