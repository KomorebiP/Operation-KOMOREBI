import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 20/25. -/

example : maximumLayerCompilerTotalTests 11 55 0 = 19 := by native_decide
example : radixRepresentativeBudget 11 6 = 6 := by native_decide
example : maximumLayerCompilerBudgetBound 11 55 0 = 23 := by native_decide
example : maximumLayerCompilerTestBound 11 55 0 = 53 := by native_decide
example : maximumLayerCompilerTotalTests 11 55 0 ≤ maximumLayerCompilerBudgetBound 11 55 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 55 0 ≤ maximumLayerCompilerTestBound 11 55 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 55 0 (by decide) (by decide)).totalTests = 19 := by native_decide
example : maximumLayerCompilerTotalTests 11 55 1 = 9 := by native_decide
example : radixRepresentativeBudget 11 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 55 1 = 17 := by native_decide
example : maximumLayerCompilerTestBound 11 55 1 = 23 := by native_decide
example : maximumLayerCompilerTotalTests 11 55 1 ≤ maximumLayerCompilerBudgetBound 11 55 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 55 1 ≤ maximumLayerCompilerTestBound 11 55 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 55 1 (by decide) (by decide)).totalTests = 9 := by native_decide
example : maximumLayerCompilerTotalTests 11 55 3 = 11 := by native_decide
example : radixRepresentativeBudget 11 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 11 55 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 11 55 3 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 11 55 3 ≤ maximumLayerCompilerBudgetBound 11 55 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 55 3 ≤ maximumLayerCompilerTestBound 11 55 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 55 3 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 11 55 7 = 6 := by native_decide
example : radixRepresentativeBudget 11 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 55 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 11 55 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 55 7 ≤ maximumLayerCompilerBudgetBound 11 55 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 55 7 ≤ maximumLayerCompilerTestBound 11 55 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 55 7 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 11 89 0 = 20 := by native_decide
example : radixRepresentativeBudget 11 9 = 9 := by native_decide
example : maximumLayerCompilerBudgetBound 11 89 0 = 29 := by native_decide
example : maximumLayerCompilerTestBound 11 89 0 = 101 := by native_decide
example : maximumLayerCompilerTotalTests 11 89 0 ≤ maximumLayerCompilerBudgetBound 11 89 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 89 0 ≤ maximumLayerCompilerTestBound 11 89 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 89 0 (by decide) (by decide)).totalTests = 20 := by native_decide
example : maximumLayerCompilerTotalTests 11 89 1 = 16 := by native_decide
example : radixRepresentativeBudget 11 5 = 5 := by native_decide
example : maximumLayerCompilerBudgetBound 11 89 1 = 21 := by native_decide
example : maximumLayerCompilerTestBound 11 89 1 = 41 := by native_decide
example : maximumLayerCompilerTotalTests 11 89 1 ≤ maximumLayerCompilerBudgetBound 11 89 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 89 1 ≤ maximumLayerCompilerTestBound 11 89 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 89 1 (by decide) (by decide)).totalTests = 16 := by native_decide
example : maximumLayerCompilerTotalTests 11 89 3 = 14 := by native_decide
example : radixRepresentativeBudget 11 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 89 3 = 17 := by native_decide
example : maximumLayerCompilerTestBound 11 89 3 = 23 := by native_decide
example : maximumLayerCompilerTotalTests 11 89 3 ≤ maximumLayerCompilerBudgetBound 11 89 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 89 3 ≤ maximumLayerCompilerTestBound 11 89 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 89 3 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 11 89 7 = 13 := by native_decide
example : radixRepresentativeBudget 11 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 11 89 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 11 89 7 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 11 89 7 ≤ maximumLayerCompilerBudgetBound 11 89 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 89 7 ≤ maximumLayerCompilerTestBound 11 89 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 89 7 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 144 0 = 37 := by native_decide
example : radixRepresentativeBudget 11 15 = 19 := by native_decide
example : maximumLayerCompilerBudgetBound 11 144 0 = 45 := by native_decide
example : maximumLayerCompilerTestBound 11 144 0 = 251 := by native_decide
example : maximumLayerCompilerTotalTests 11 144 0 ≤ maximumLayerCompilerBudgetBound 11 144 0 := by native_decide
example : maximumLayerCompilerBudgetBound 11 144 0 ≤ maximumLayerCompilerTestBound 11 144 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 144 0 (by decide) (by decide)).totalTests = 37 := by native_decide
example : maximumLayerCompilerTotalTests 11 144 1 = 25 := by native_decide
example : radixRepresentativeBudget 11 8 = 8 := by native_decide
example : maximumLayerCompilerBudgetBound 11 144 1 = 27 := by native_decide
example : maximumLayerCompilerTestBound 11 144 1 = 83 := by native_decide
example : maximumLayerCompilerTotalTests 11 144 1 ≤ maximumLayerCompilerBudgetBound 11 144 1 := by native_decide
example : maximumLayerCompilerBudgetBound 11 144 1 ≤ maximumLayerCompilerTestBound 11 144 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 144 1 (by decide) (by decide)).totalTests = 25 := by native_decide
example : maximumLayerCompilerTotalTests 11 144 3 = 13 := by native_decide
example : radixRepresentativeBudget 11 4 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 11 144 3 = 19 := by native_decide
example : maximumLayerCompilerTestBound 11 144 3 = 31 := by native_decide
example : maximumLayerCompilerTotalTests 11 144 3 ≤ maximumLayerCompilerBudgetBound 11 144 3 := by native_decide
example : maximumLayerCompilerBudgetBound 11 144 3 ≤ maximumLayerCompilerTestBound 11 144 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 144 3 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 11 144 7 = 7 := by native_decide
example : radixRepresentativeBudget 11 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 11 144 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 11 144 7 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 11 144 7 ≤ maximumLayerCompilerBudgetBound 11 144 7 := by native_decide
example : maximumLayerCompilerBudgetBound 11 144 7 ≤ maximumLayerCompilerTestBound 11 144 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 11 144 7 (by decide) (by decide)).totalTests = 7 := by native_decide
