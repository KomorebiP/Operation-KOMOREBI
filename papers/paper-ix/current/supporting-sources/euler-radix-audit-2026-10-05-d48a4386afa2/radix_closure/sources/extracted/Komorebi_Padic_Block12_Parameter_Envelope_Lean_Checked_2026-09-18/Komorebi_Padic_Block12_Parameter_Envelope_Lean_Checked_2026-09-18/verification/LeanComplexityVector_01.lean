import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 1/25. -/

example : maximumLayerCompilerTotalTests 2 1 0 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 1 0 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 1 0 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 1 0 ≤ maximumLayerCompilerBudgetBound 2 1 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 1 0 ≤ maximumLayerCompilerTestBound 2 1 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 1 0 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 1 1 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 1 1 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 1 1 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 1 1 ≤ maximumLayerCompilerBudgetBound 2 1 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 1 1 ≤ maximumLayerCompilerTestBound 2 1 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 1 1 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 1 3 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 1 3 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 1 3 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 1 3 ≤ maximumLayerCompilerBudgetBound 2 1 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 1 3 ≤ maximumLayerCompilerTestBound 2 1 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 1 3 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 1 7 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 1 7 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 1 7 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 1 7 ≤ maximumLayerCompilerBudgetBound 2 1 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 1 7 ≤ maximumLayerCompilerTestBound 2 1 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 1 7 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 2 0 = 6 := by native_decide
example : radixRepresentativeBudget 2 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 2 2 0 = 6 := by native_decide
example : maximumLayerCompilerTestBound 2 2 0 = 8 := by native_decide
example : maximumLayerCompilerTotalTests 2 2 0 ≤ maximumLayerCompilerBudgetBound 2 2 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 2 0 ≤ maximumLayerCompilerTestBound 2 2 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 2 0 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 2 2 1 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 2 1 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 2 1 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 2 1 ≤ maximumLayerCompilerBudgetBound 2 2 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 2 1 ≤ maximumLayerCompilerTestBound 2 2 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 2 1 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 2 3 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 2 3 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 2 3 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 2 3 ≤ maximumLayerCompilerBudgetBound 2 2 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 2 3 ≤ maximumLayerCompilerTestBound 2 2 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 2 3 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 2 7 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 2 7 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 2 7 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 2 7 ≤ maximumLayerCompilerBudgetBound 2 2 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 2 7 ≤ maximumLayerCompilerTestBound 2 2 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 2 7 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 3 0 = 8 := by native_decide
example : radixRepresentativeBudget 2 3 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 2 3 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 2 3 0 = 14 := by native_decide
example : maximumLayerCompilerTotalTests 2 3 0 ≤ maximumLayerCompilerBudgetBound 2 3 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 3 0 ≤ maximumLayerCompilerTestBound 2 3 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 3 0 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 2 3 1 = 6 := by native_decide
example : radixRepresentativeBudget 2 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 2 3 1 = 6 := by native_decide
example : maximumLayerCompilerTestBound 2 3 1 = 8 := by native_decide
example : maximumLayerCompilerTotalTests 2 3 1 ≤ maximumLayerCompilerBudgetBound 2 3 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 3 1 ≤ maximumLayerCompilerTestBound 2 3 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 3 1 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 2 3 3 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 3 3 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 3 3 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 3 3 ≤ maximumLayerCompilerBudgetBound 2 3 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 3 3 ≤ maximumLayerCompilerTestBound 2 3 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 3 3 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 2 3 7 = 3 := by native_decide
example : radixRepresentativeBudget 2 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 3 7 = 4 := by native_decide
example : maximumLayerCompilerTestBound 2 3 7 = 4 := by native_decide
example : maximumLayerCompilerTotalTests 2 3 7 ≤ maximumLayerCompilerBudgetBound 2 3 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 3 7 ≤ maximumLayerCompilerTestBound 2 3 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 3 7 (by decide) (by decide)).totalTests = 3 := by native_decide
