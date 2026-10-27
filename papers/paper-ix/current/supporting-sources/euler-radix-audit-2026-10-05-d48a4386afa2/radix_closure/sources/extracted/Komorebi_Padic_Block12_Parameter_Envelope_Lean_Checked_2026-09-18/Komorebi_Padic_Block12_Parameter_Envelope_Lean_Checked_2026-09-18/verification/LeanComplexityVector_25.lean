import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 25/25. -/

example : maximumLayerCompilerTotalTests 3 500 0 = 586 := by native_decide
example : radixRepresentativeBudget 3 250 = 10542 := by native_decide
example : maximumLayerCompilerBudgetBound 3 500 0 = 10795 := by native_decide
example : maximumLayerCompilerTestBound 3 500 0 = 62753 := by native_decide
example : maximumLayerCompilerTotalTests 3 500 0 ≤ maximumLayerCompilerBudgetBound 3 500 0 := by native_decide
example : maximumLayerCompilerBudgetBound 3 500 0 ≤ maximumLayerCompilerTestBound 3 500 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 3 500 0 (by decide) (by decide)).totalTests = 586 := by native_decide
example : maximumLayerCompilerTotalTests 13 300 2 = 27 := by native_decide
example : radixRepresentativeBudget 13 9 = 9 := by native_decide
example : maximumLayerCompilerBudgetBound 13 300 2 = 31 := by native_decide
example : maximumLayerCompilerTestBound 13 300 2 = 103 := by native_decide
example : maximumLayerCompilerTotalTests 13 300 2 ≤ maximumLayerCompilerBudgetBound 13 300 2 := by native_decide
example : maximumLayerCompilerBudgetBound 13 300 2 ≤ maximumLayerCompilerTestBound 13 300 2 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 300 2 (by decide) (by decide)).totalTests = 27 := by native_decide
