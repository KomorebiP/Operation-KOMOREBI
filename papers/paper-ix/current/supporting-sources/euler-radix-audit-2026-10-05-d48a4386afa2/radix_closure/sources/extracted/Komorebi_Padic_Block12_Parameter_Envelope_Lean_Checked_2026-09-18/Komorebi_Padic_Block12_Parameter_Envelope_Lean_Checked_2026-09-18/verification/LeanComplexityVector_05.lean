import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 5/25. -/

example : maximumLayerCompilerTotalTests 3 1 0 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 1 0 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 1 0 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 1 0 ≤ maximumLayerCompilerBudgetBound 3 1 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 1 0 ≤ maximumLayerCompilerTestBound 3 1 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 1 0 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 1 1 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 1 1 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 1 1 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 1 1 ≤ maximumLayerCompilerBudgetBound 3 1 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 1 1 ≤ maximumLayerCompilerTestBound 3 1 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 1 1 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 1 3 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 1 3 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 1 3 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 1 3 ≤ maximumLayerCompilerBudgetBound 3 1 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 1 3 ≤ maximumLayerCompilerTestBound 3 1 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 1 3 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 1 7 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 1 7 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 1 7 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 1 7 ≤ maximumLayerCompilerBudgetBound 3 1 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 1 7 ≤ maximumLayerCompilerTestBound 3 1 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 1 7 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 2 0 = 3 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 2 0 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 2 0 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 2 0 ≤ maximumLayerCompilerBudgetBound 3 2 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 2 0 ≤ maximumLayerCompilerTestBound 3 2 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 2 0 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 3 2 1 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 2 1 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 2 1 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 2 1 ≤ maximumLayerCompilerBudgetBound 3 2 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 2 1 ≤ maximumLayerCompilerTestBound 3 2 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 2 1 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 2 3 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 2 3 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 2 3 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 2 3 ≤ maximumLayerCompilerBudgetBound 3 2 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 2 3 ≤ maximumLayerCompilerTestBound 3 2 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 2 3 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 2 7 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 2 7 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 2 7 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 2 7 ≤ maximumLayerCompilerBudgetBound 3 2 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 2 7 ≤ maximumLayerCompilerTestBound 3 2 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 2 7 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 3 0 = 7 := by native_decide
example : radixRepresentativeBudget 3 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 3 3 0 = 7 := by native_decide
example : maximumLayerCompilerTestBound 3 3 0 = 9 := by native_decide
example : maximumLayerCompilerTotalTests 3 3 0 ≤ maximumLayerCompilerBudgetBound 3 3 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 3 0 ≤ maximumLayerCompilerTestBound 3 3 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 3 0 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 3 3 1 = 3 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 3 1 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 3 1 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 3 1 ≤ maximumLayerCompilerBudgetBound 3 3 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 3 1 ≤ maximumLayerCompilerTestBound 3 3 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 3 1 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 3 3 3 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 3 3 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 3 3 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 3 3 ≤ maximumLayerCompilerBudgetBound 3 3 3 := by native_decide
example : maximumLayerCompilerBudgetBound 3 3 3 ≤ maximumLayerCompilerTestBound 3 3 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 3 3 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 3 3 7 = 4 := by native_decide
example : radixRepresentativeBudget 3 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 3 3 7 = 5 := by native_decide
example : maximumLayerCompilerTestBound 3 3 7 = 5 := by native_decide
example : maximumLayerCompilerTotalTests 3 3 7 ≤ maximumLayerCompilerBudgetBound 3 3 7 := by native_decide
example : maximumLayerCompilerBudgetBound 3 3 7 ≤ maximumLayerCompilerTestBound 3 3 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 3 7 (by decide) (by decide)).totalTests = 4 := by native_decide
