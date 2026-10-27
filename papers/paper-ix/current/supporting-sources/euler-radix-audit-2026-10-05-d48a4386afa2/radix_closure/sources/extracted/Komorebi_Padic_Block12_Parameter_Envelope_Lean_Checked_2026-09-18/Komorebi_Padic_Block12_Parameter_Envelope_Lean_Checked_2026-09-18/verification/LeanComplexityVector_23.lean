import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 23/25. -/

example : maximumLayerCompilerTotalTests 13 13 0 = 17 := by native_decide
example : radixRepresentativeBudget 13 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 13 13 0 = 17 := by native_decide
example : maximumLayerCompilerTestBound 13 13 0 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 13 13 0 ≤ maximumLayerCompilerBudgetBound 13 13 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 13 0 ≤ maximumLayerCompilerTestBound 13 13 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 13 0 (by decide) (by decide)).totalTests = 17 := by native_decide
example : maximumLayerCompilerTotalTests 13 13 1 = 8 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 13 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 13 1 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 13 1 ≤ maximumLayerCompilerBudgetBound 13 13 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 13 1 ≤ maximumLayerCompilerTestBound 13 13 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 13 1 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 13 13 3 = 11 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 13 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 13 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 13 3 ≤ maximumLayerCompilerBudgetBound 13 13 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 13 3 ≤ maximumLayerCompilerTestBound 13 13 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 13 3 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 13 13 7 = 13 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 13 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 13 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 13 7 ≤ maximumLayerCompilerBudgetBound 13 13 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 13 7 ≤ maximumLayerCompilerTestBound 13 13 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 13 7 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 13 21 0 = 8 := by native_decide
example : radixRepresentativeBudget 13 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 13 21 0 = 17 := by native_decide
example : maximumLayerCompilerTestBound 13 21 0 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 13 21 0 ≤ maximumLayerCompilerBudgetBound 13 21 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 21 0 ≤ maximumLayerCompilerTestBound 13 21 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 21 0 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 13 21 1 = 4 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 21 1 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 21 1 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 21 1 ≤ maximumLayerCompilerBudgetBound 13 21 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 21 1 ≤ maximumLayerCompilerTestBound 13 21 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 21 1 (by decide) (by decide)).totalTests = 4 := by native_decide
example : maximumLayerCompilerTotalTests 13 21 3 = 9 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 21 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 21 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 21 3 ≤ maximumLayerCompilerBudgetBound 13 21 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 21 3 ≤ maximumLayerCompilerTestBound 13 21 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 21 3 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 13 21 7 = 12 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 21 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 21 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 21 7 ≤ maximumLayerCompilerBudgetBound 13 21 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 21 7 ≤ maximumLayerCompilerTestBound 13 21 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 21 7 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 13 34 0 = 9 := by native_decide
example : radixRepresentativeBudget 13 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 34 0 = 19 := by native_decide
example : maximumLayerCompilerTestBound 13 34 0 = 25 := by native_decide
example : maximumLayerCompilerTotalTests 13 34 0 ≤ maximumLayerCompilerBudgetBound 13 34 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 34 0 ≤ maximumLayerCompilerTestBound 13 34 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 34 0 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 13 34 1 = 12 := by native_decide
example : radixRepresentativeBudget 13 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 13 34 1 = 17 := by native_decide
example : maximumLayerCompilerTestBound 13 34 1 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 13 34 1 ≤ maximumLayerCompilerBudgetBound 13 34 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 34 1 ≤ maximumLayerCompilerTestBound 13 34 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 34 1 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 13 34 3 = 6 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 34 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 34 3 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 34 3 ≤ maximumLayerCompilerBudgetBound 13 34 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 34 3 ≤ maximumLayerCompilerTestBound 13 34 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 34 3 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 13 34 7 = 10 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 34 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 34 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 34 7 ≤ maximumLayerCompilerBudgetBound 13 34 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 34 7 ≤ maximumLayerCompilerTestBound 13 34 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 34 7 (by decide) (by decide)).totalTests = 10 := by native_decide
