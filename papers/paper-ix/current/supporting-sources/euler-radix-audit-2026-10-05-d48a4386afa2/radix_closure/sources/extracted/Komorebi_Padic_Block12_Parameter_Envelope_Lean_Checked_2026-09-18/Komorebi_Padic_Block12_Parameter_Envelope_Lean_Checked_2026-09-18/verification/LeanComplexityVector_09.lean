import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 9/25. -/

example : maximumLayerCompilerTotalTests 5 1 0 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 1 0 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 1 0 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 1 0 ≤ maximumLayerCompilerBudgetBound 5 1 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 1 0 ≤ maximumLayerCompilerTestBound 5 1 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 1 0 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 1 1 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 1 1 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 1 1 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 1 1 ≤ maximumLayerCompilerBudgetBound 5 1 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 1 1 ≤ maximumLayerCompilerTestBound 5 1 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 1 1 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 1 3 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 1 3 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 1 3 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 1 3 ≤ maximumLayerCompilerBudgetBound 5 1 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 1 3 ≤ maximumLayerCompilerTestBound 5 1 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 1 3 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 1 7 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 1 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 1 7 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 1 7 ≤ maximumLayerCompilerBudgetBound 5 1 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 1 7 ≤ maximumLayerCompilerTestBound 5 1 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 1 7 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 2 0 = 5 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 2 0 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 2 0 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 2 0 ≤ maximumLayerCompilerBudgetBound 5 2 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 2 0 ≤ maximumLayerCompilerTestBound 5 2 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 2 0 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 5 2 1 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 2 1 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 2 1 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 2 1 ≤ maximumLayerCompilerBudgetBound 5 2 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 2 1 ≤ maximumLayerCompilerTestBound 5 2 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 2 1 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 2 3 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 2 3 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 2 3 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 2 3 ≤ maximumLayerCompilerBudgetBound 5 2 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 2 3 ≤ maximumLayerCompilerTestBound 5 2 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 2 3 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 2 7 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 2 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 2 7 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 2 7 ≤ maximumLayerCompilerBudgetBound 5 2 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 2 7 ≤ maximumLayerCompilerTestBound 5 2 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 2 7 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 3 0 = 4 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 3 0 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 3 0 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 3 0 ≤ maximumLayerCompilerBudgetBound 5 3 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 3 0 ≤ maximumLayerCompilerTestBound 5 3 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 3 0 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 5 3 1 = 5 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 3 1 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 3 1 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 3 1 ≤ maximumLayerCompilerBudgetBound 5 3 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 3 1 ≤ maximumLayerCompilerTestBound 5 3 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 3 1 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 5 3 3 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 3 3 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 3 3 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 3 3 ≤ maximumLayerCompilerBudgetBound 5 3 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 3 3 ≤ maximumLayerCompilerTestBound 5 3 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 3 3 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 3 7 = 6 := by native_decide
example : radixRepresentativeBudget 5 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 3 7 = 7 := by native_decide
example : maximumLayerCompilerTestBound 5 3 7 = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 3 7 ≤ maximumLayerCompilerBudgetBound 5 3 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 3 7 ≤ maximumLayerCompilerTestBound 5 3 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 3 7 (by decide) (by decide)).totalTests = 6 := by native_decide
