import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 13/25. -/

example : maximumLayerCompilerTotalTests 7 1 0 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 1 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 1 0 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 1 0 ≤ maximumLayerCompilerBudgetBound 7 1 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 1 0 ≤ maximumLayerCompilerTestBound 7 1 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 1 0 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 1 1 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 1 1 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 1 1 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 1 1 ≤ maximumLayerCompilerBudgetBound 7 1 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 1 1 ≤ maximumLayerCompilerTestBound 7 1 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 1 1 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 1 3 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 1 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 1 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 1 3 ≤ maximumLayerCompilerBudgetBound 7 1 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 1 3 ≤ maximumLayerCompilerTestBound 7 1 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 1 3 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 1 7 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 1 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 1 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 1 7 ≤ maximumLayerCompilerBudgetBound 7 1 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 1 7 ≤ maximumLayerCompilerTestBound 7 1 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 1 7 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 2 0 = 7 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 2 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 2 0 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 2 0 ≤ maximumLayerCompilerBudgetBound 7 2 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 2 0 ≤ maximumLayerCompilerTestBound 7 2 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 2 0 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 7 2 1 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 2 1 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 2 1 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 2 1 ≤ maximumLayerCompilerBudgetBound 7 2 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 2 1 ≤ maximumLayerCompilerTestBound 7 2 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 2 1 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 2 3 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 2 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 2 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 2 3 ≤ maximumLayerCompilerBudgetBound 7 2 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 2 3 ≤ maximumLayerCompilerTestBound 7 2 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 2 3 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 2 7 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 2 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 2 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 2 7 ≤ maximumLayerCompilerBudgetBound 7 2 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 2 7 ≤ maximumLayerCompilerTestBound 7 2 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 2 7 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 3 0 = 6 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 3 0 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 3 0 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 3 0 ≤ maximumLayerCompilerBudgetBound 7 3 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 3 0 ≤ maximumLayerCompilerTestBound 7 3 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 3 0 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 7 3 1 = 7 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 3 1 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 3 1 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 3 1 ≤ maximumLayerCompilerBudgetBound 7 3 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 3 1 ≤ maximumLayerCompilerTestBound 7 3 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 3 1 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 7 3 3 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 3 3 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 3 3 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 3 3 ≤ maximumLayerCompilerBudgetBound 7 3 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 3 3 ≤ maximumLayerCompilerTestBound 7 3 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 3 3 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 7 3 7 = 8 := by native_decide
example : radixRepresentativeBudget 7 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 3 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 7 3 7 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 7 3 7 ≤ maximumLayerCompilerBudgetBound 7 3 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 3 7 ≤ maximumLayerCompilerTestBound 7 3 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 3 7 (by decide) (by decide)).totalTests = 8 := by native_decide
