import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 21/25. -/

example : maximumLayerCompilerTotalTests 13 1 0 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 1 0 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 1 0 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 1 0 ≤ maximumLayerCompilerBudgetBound 13 1 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 1 0 ≤ maximumLayerCompilerTestBound 13 1 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 1 0 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 1 1 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 1 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 1 1 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 1 1 ≤ maximumLayerCompilerBudgetBound 13 1 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 1 1 ≤ maximumLayerCompilerTestBound 13 1 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 1 1 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 1 3 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 1 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 1 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 1 3 ≤ maximumLayerCompilerBudgetBound 13 1 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 1 3 ≤ maximumLayerCompilerTestBound 13 1 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 1 3 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 1 7 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 1 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 1 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 1 7 ≤ maximumLayerCompilerBudgetBound 13 1 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 1 7 ≤ maximumLayerCompilerTestBound 13 1 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 1 7 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 2 0 = 13 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 2 0 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 2 0 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 2 0 ≤ maximumLayerCompilerBudgetBound 13 2 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 2 0 ≤ maximumLayerCompilerTestBound 13 2 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 2 0 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 13 2 1 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 2 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 2 1 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 2 1 ≤ maximumLayerCompilerBudgetBound 13 2 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 2 1 ≤ maximumLayerCompilerTestBound 13 2 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 2 1 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 2 3 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 2 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 2 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 2 3 ≤ maximumLayerCompilerBudgetBound 13 2 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 2 3 ≤ maximumLayerCompilerTestBound 13 2 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 2 3 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 2 7 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 2 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 2 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 2 7 ≤ maximumLayerCompilerBudgetBound 13 2 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 2 7 ≤ maximumLayerCompilerTestBound 13 2 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 2 7 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 3 0 = 12 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 3 0 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 3 0 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 3 0 ≤ maximumLayerCompilerBudgetBound 13 3 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 3 0 ≤ maximumLayerCompilerTestBound 13 3 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 3 0 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 13 3 1 = 13 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 3 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 3 1 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 3 1 ≤ maximumLayerCompilerBudgetBound 13 3 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 3 1 ≤ maximumLayerCompilerTestBound 13 3 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 3 1 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 13 3 3 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 3 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 3 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 3 3 ≤ maximumLayerCompilerBudgetBound 13 3 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 3 3 ≤ maximumLayerCompilerTestBound 13 3 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 3 3 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 13 3 7 = 14 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 3 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 3 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 3 7 ≤ maximumLayerCompilerBudgetBound 13 3 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 3 7 ≤ maximumLayerCompilerTestBound 13 3 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 3 7 (by decide) (by decide)).totalTests = 14 := by native_decide
