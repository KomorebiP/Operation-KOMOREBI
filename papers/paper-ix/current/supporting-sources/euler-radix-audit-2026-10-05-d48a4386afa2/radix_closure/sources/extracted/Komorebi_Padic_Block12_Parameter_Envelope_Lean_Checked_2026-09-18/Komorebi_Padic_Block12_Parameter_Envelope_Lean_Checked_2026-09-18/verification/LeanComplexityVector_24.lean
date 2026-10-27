import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 24/25. -/

example : maximumLayerCompilerTotalTests 13 55 0 = 16 := by native_decide
example : radixRepresentativeBudget 13 5 = 5 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 0 = 23 := by native_decide
example : maximumLayerCompilerTestBound 13 55 0 = 43 := by native_decide
example : maximumLayerCompilerTotalTests 13 55 0 ≤ maximumLayerCompilerBudgetBound 13 55 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 0 ≤ maximumLayerCompilerTestBound 13 55 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 55 0 (by decide) (by decide)).totalTests = 16 := by native_decide
example : maximumLayerCompilerTotalTests 13 55 1 = 15 := by native_decide
example : radixRepresentativeBudget 13 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 1 = 19 := by native_decide
example : maximumLayerCompilerTestBound 13 55 1 = 25 := by native_decide
example : maximumLayerCompilerTotalTests 13 55 1 ≤ maximumLayerCompilerBudgetBound 13 55 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 1 ≤ maximumLayerCompilerTestBound 13 55 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 55 1 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 55 3 = 15 := by native_decide
example : radixRepresentativeBudget 13 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 3 = 17 := by native_decide
example : maximumLayerCompilerTestBound 13 55 3 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 13 55 3 ≤ maximumLayerCompilerBudgetBound 13 55 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 3 ≤ maximumLayerCompilerTestBound 13 55 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 55 3 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 55 7 = 8 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 55 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 55 7 ≤ maximumLayerCompilerBudgetBound 13 55 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 7 ≤ maximumLayerCompilerTestBound 13 55 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 55 7 (by decide) (by decide)).totalTests = 8 := by native_decide
example : maximumLayerCompilerTotalTests 13 89 0 = 25 := by native_decide
example : radixRepresentativeBudget 13 8 = 8 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 0 = 29 := by native_decide
example : maximumLayerCompilerTestBound 13 89 0 = 85 := by native_decide
example : maximumLayerCompilerTotalTests 13 89 0 ≤ maximumLayerCompilerBudgetBound 13 89 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 0 ≤ maximumLayerCompilerTestBound 13 89 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 89 0 (by decide) (by decide)).totalTests = 25 := by native_decide
example : maximumLayerCompilerTotalTests 13 89 1 = 12 := by native_decide
example : radixRepresentativeBudget 13 4 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 1 = 21 := by native_decide
example : maximumLayerCompilerTestBound 13 89 1 = 33 := by native_decide
example : maximumLayerCompilerTotalTests 13 89 1 ≤ maximumLayerCompilerBudgetBound 13 89 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 1 ≤ maximumLayerCompilerTestBound 13 89 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 89 1 (by decide) (by decide)).totalTests = 12 := by native_decide
example : maximumLayerCompilerTotalTests 13 89 3 = 6 := by native_decide
example : radixRepresentativeBudget 13 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 3 = 17 := by native_decide
example : maximumLayerCompilerTestBound 13 89 3 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 13 89 3 ≤ maximumLayerCompilerBudgetBound 13 89 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 3 ≤ maximumLayerCompilerTestBound 13 89 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 89 3 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 13 89 7 = 3 := by native_decide
example : radixRepresentativeBudget 13 1 = 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 13 89 7 = 15 := by native_decide
example : maximumLayerCompilerTotalTests 13 89 7 ≤ maximumLayerCompilerBudgetBound 13 89 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 7 ≤ maximumLayerCompilerTestBound 13 89 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 89 7 (by decide) (by decide)).totalTests = 3 := by native_decide
example : maximumLayerCompilerTotalTests 13 144 0 = 25 := by native_decide
example : radixRepresentativeBudget 13 12 = 12 := by native_decide
example : maximumLayerCompilerBudgetBound 13 144 0 = 37 := by native_decide
example : maximumLayerCompilerTestBound 13 144 0 = 169 := by native_decide
example : maximumLayerCompilerTotalTests 13 144 0 ≤ maximumLayerCompilerBudgetBound 13 144 0 := by native_decide
example : maximumLayerCompilerBudgetBound 13 144 0 ≤ maximumLayerCompilerTestBound 13 144 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 144 0 (by decide) (by decide)).totalTests = 25 := by native_decide
example : maximumLayerCompilerTotalTests 13 144 1 = 13 := by native_decide
example : radixRepresentativeBudget 13 6 = 6 := by native_decide
example : maximumLayerCompilerBudgetBound 13 144 1 = 25 := by native_decide
example : maximumLayerCompilerTestBound 13 144 1 = 55 := by native_decide
example : maximumLayerCompilerTotalTests 13 144 1 ≤ maximumLayerCompilerBudgetBound 13 144 1 := by native_decide
example : maximumLayerCompilerBudgetBound 13 144 1 ≤ maximumLayerCompilerTestBound 13 144 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 144 1 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 13 144 3 = 7 := by native_decide
example : radixRepresentativeBudget 13 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 144 3 = 19 := by native_decide
example : maximumLayerCompilerTestBound 13 144 3 = 25 := by native_decide
example : maximumLayerCompilerTotalTests 13 144 3 ≤ maximumLayerCompilerBudgetBound 13 144 3 := by native_decide
example : maximumLayerCompilerBudgetBound 13 144 3 ≤ maximumLayerCompilerTestBound 13 144 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 144 3 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 13 144 7 = 11 := by native_decide
example : radixRepresentativeBudget 13 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 13 144 7 = 17 := by native_decide
example : maximumLayerCompilerTestBound 13 144 7 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 13 144 7 ≤ maximumLayerCompilerBudgetBound 13 144 7 := by native_decide
example : maximumLayerCompilerBudgetBound 13 144 7 ≤ maximumLayerCompilerTestBound 13 144 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 13 144 7 (by decide) (by decide)).totalTests = 11 := by native_decide
