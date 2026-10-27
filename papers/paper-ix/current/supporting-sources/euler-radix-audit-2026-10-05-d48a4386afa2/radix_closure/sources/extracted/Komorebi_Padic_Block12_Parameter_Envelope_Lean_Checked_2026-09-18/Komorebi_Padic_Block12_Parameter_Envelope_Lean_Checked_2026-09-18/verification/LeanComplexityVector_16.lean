import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 16/25. -/

example : maximumLayerCompilerTotalTests 7 55 0 = 27 := by native_decide
example : radixRepresentativeBudget 7 10 = 13 := by native_decide
example : maximumLayerCompilerBudgetBound 7 55 0 = 30 := by native_decide
example : maximumLayerCompilerTestBound 7 55 0 = 117 := by native_decide
example : maximumLayerCompilerTotalTests 7 55 0 ≤ maximumLayerCompilerBudgetBound 7 55 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 55 0 ≤ maximumLayerCompilerTestBound 7 55 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 55 0 (by decide) (by decide)).totalTests = 27 := by native_decide
example : maximumLayerCompilerTotalTests 7 55 1 = 14 := by native_decide
example : radixRepresentativeBudget 7 5 = 5 := by native_decide
example : maximumLayerCompilerBudgetBound 7 55 1 = 17 := by native_decide
example : maximumLayerCompilerTestBound 7 55 1 = 37 := by native_decide
example : maximumLayerCompilerTotalTests 7 55 1 ≤ maximumLayerCompilerBudgetBound 7 55 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 55 1 ≤ maximumLayerCompilerTestBound 7 55 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 55 1 (by decide) (by decide)).totalTests = 14 := by native_decide
example : maximumLayerCompilerTotalTests 7 55 3 = 11 := by native_decide
example : radixRepresentativeBudget 7 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 55 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 7 55 3 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 7 55 3 ≤ maximumLayerCompilerBudgetBound 7 55 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 55 3 ≤ maximumLayerCompilerTestBound 7 55 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 55 3 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 7 55 7 = 10 := by native_decide
example : radixRepresentativeBudget 7 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 7 55 7 = 11 := by native_decide
example : maximumLayerCompilerTestBound 7 55 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 55 7 ≤ maximumLayerCompilerBudgetBound 7 55 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 55 7 ≤ maximumLayerCompilerTestBound 7 55 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 55 7 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 7 89 0 = 33 := by native_decide
example : radixRepresentativeBudget 7 15 = 24 := by native_decide
example : maximumLayerCompilerBudgetBound 7 89 0 = 46 := by native_decide
example : maximumLayerCompilerTestBound 7 89 0 = 247 := by native_decide
example : maximumLayerCompilerTotalTests 7 89 0 ≤ maximumLayerCompilerBudgetBound 7 89 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 89 0 ≤ maximumLayerCompilerTestBound 7 89 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 89 0 (by decide) (by decide)).totalTests = 33 := by native_decide
example : maximumLayerCompilerTotalTests 7 89 1 = 21 := by native_decide
example : radixRepresentativeBudget 7 8 = 9 := by native_decide
example : maximumLayerCompilerBudgetBound 7 89 1 = 24 := by native_decide
example : maximumLayerCompilerTestBound 7 89 1 = 79 := by native_decide
example : maximumLayerCompilerTotalTests 7 89 1 ≤ maximumLayerCompilerBudgetBound 7 89 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 89 1 ≤ maximumLayerCompilerTestBound 7 89 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 89 1 (by decide) (by decide)).totalTests = 21 := by native_decide
example : maximumLayerCompilerTotalTests 7 89 3 = 10 := by native_decide
example : radixRepresentativeBudget 7 4 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 7 89 3 = 15 := by native_decide
example : maximumLayerCompilerTestBound 7 89 3 = 27 := by native_decide
example : maximumLayerCompilerTotalTests 7 89 3 ≤ maximumLayerCompilerBudgetBound 7 89 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 89 3 ≤ maximumLayerCompilerTestBound 7 89 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 89 3 (by decide) (by decide)).totalTests = 10 := by native_decide
example : maximumLayerCompilerTotalTests 7 89 7 = 5 := by native_decide
example : radixRepresentativeBudget 7 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 7 89 7 = 11 := by native_decide
example : maximumLayerCompilerTestBound 7 89 7 = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 89 7 ≤ maximumLayerCompilerBudgetBound 7 89 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 89 7 ≤ maximumLayerCompilerTestBound 7 89 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 89 7 (by decide) (by decide)).totalTests = 5 := by native_decide
example : maximumLayerCompilerTotalTests 7 144 0 = 50 := by native_decide
example : radixRepresentativeBudget 7 24 = 54 := by native_decide
example : maximumLayerCompilerBudgetBound 7 144 0 = 85 := by native_decide
example : maximumLayerCompilerTestBound 7 144 0 = 607 := by native_decide
example : maximumLayerCompilerTotalTests 7 144 0 ≤ maximumLayerCompilerBudgetBound 7 144 0 := by native_decide
example : maximumLayerCompilerBudgetBound 7 144 0 ≤ maximumLayerCompilerTestBound 7 144 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 144 0 (by decide) (by decide)).totalTests = 50 := by native_decide
example : maximumLayerCompilerTotalTests 7 144 1 = 25 := by native_decide
example : radixRepresentativeBudget 7 12 = 17 := by native_decide
example : maximumLayerCompilerBudgetBound 7 144 1 = 36 := by native_decide
example : maximumLayerCompilerTestBound 7 144 1 = 163 := by native_decide
example : maximumLayerCompilerTotalTests 7 144 1 ≤ maximumLayerCompilerBudgetBound 7 144 1 := by native_decide
example : maximumLayerCompilerBudgetBound 7 144 1 ≤ maximumLayerCompilerTestBound 7 144 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 144 1 (by decide) (by decide)).totalTests = 25 := by native_decide
example : maximumLayerCompilerTotalTests 7 144 3 = 13 := by native_decide
example : radixRepresentativeBudget 7 6 = 6 := by native_decide
example : maximumLayerCompilerBudgetBound 7 144 3 = 19 := by native_decide
example : maximumLayerCompilerTestBound 7 144 3 = 49 := by native_decide
example : maximumLayerCompilerTotalTests 7 144 3 ≤ maximumLayerCompilerBudgetBound 7 144 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 144 3 ≤ maximumLayerCompilerTestBound 7 144 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 144 3 (by decide) (by decide)).totalTests = 13 := by native_decide
example : maximumLayerCompilerTotalTests 7 144 7 = 7 := by native_decide
example : radixRepresentativeBudget 7 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 7 144 7 = 13 := by native_decide
example : maximumLayerCompilerTestBound 7 144 7 = 19 := by native_decide
example : maximumLayerCompilerTotalTests 7 144 7 ≤ maximumLayerCompilerBudgetBound 7 144 7 := by native_decide
example : maximumLayerCompilerBudgetBound 7 144 7 ≤ maximumLayerCompilerTestBound 7 144 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 7 144 7 (by decide) (by decide)).totalTests = 7 := by native_decide
