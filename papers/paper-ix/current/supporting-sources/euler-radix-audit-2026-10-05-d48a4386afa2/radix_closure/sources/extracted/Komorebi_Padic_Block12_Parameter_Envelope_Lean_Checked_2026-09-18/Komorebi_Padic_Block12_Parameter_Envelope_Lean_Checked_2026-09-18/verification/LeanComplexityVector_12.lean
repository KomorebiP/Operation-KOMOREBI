import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 12/25. -/

example : maximumLayerCompilerTotalTests 5 55 0 = 31 := by native_decide
example : radixRepresentativeBudget 5 14 = 27 := by native_decide
example : maximumLayerCompilerBudgetBound 5 55 0 = 46 := by native_decide
example : maximumLayerCompilerTestBound 5 55 0 = 215 := by native_decide
example : maximumLayerCompilerTotalTests 5 55 0 ≤ maximumLayerCompilerBudgetBound 5 55 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 55 0 ≤ maximumLayerCompilerTestBound 5 55 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 55 0 (by decide) (by decide)).totalTests = 31 := by native_decide
example : maximumLayerCompilerTotalTests 5 55 1 = 15 := by native_decide
example : radixRepresentativeBudget 5 7 = 9 := by native_decide
example : maximumLayerCompilerBudgetBound 5 55 1 = 21 := by native_decide
example : maximumLayerCompilerTestBound 5 55 1 = 61 := by native_decide
example : maximumLayerCompilerTotalTests 5 55 1 ≤ maximumLayerCompilerBudgetBound 5 55 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 55 1 ≤ maximumLayerCompilerTestBound 5 55 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 55 1 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 5 55 3 = 11 := by native_decide
example : radixRepresentativeBudget 5 4 = 4 := by native_decide
example : maximumLayerCompilerBudgetBound 5 55 3 = 13 := by native_decide
example : maximumLayerCompilerTestBound 5 55 3 = 25 := by native_decide
example : maximumLayerCompilerTotalTests 5 55 3 ≤ maximumLayerCompilerBudgetBound 5 55 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 55 3 ≤ maximumLayerCompilerTestBound 5 55 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 55 3 (by decide) (by decide)).totalTests = 11 := by native_decide
example : maximumLayerCompilerTotalTests 5 55 7 = 6 := by native_decide
example : radixRepresentativeBudget 5 2 = 2 := by native_decide
example : maximumLayerCompilerBudgetBound 5 55 7 = 9 := by native_decide
example : maximumLayerCompilerTestBound 5 55 7 = 11 := by native_decide
example : maximumLayerCompilerTotalTests 5 55 7 ≤ maximumLayerCompilerBudgetBound 5 55 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 55 7 ≤ maximumLayerCompilerTestBound 5 55 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 55 7 (by decide) (by decide)).totalTests = 6 := by native_decide
example : maximumLayerCompilerTotalTests 5 89 0 = 45 := by native_decide
example : radixRepresentativeBudget 5 23 = 65 := by native_decide
example : maximumLayerCompilerBudgetBound 5 89 0 = 93 := by native_decide
example : maximumLayerCompilerTestBound 5 89 0 = 557 := by native_decide
example : maximumLayerCompilerTotalTests 5 89 0 ≤ maximumLayerCompilerBudgetBound 5 89 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 89 0 ≤ maximumLayerCompilerTestBound 5 89 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 89 0 (by decide) (by decide)).totalTests = 45 := by native_decide
example : maximumLayerCompilerTotalTests 5 89 1 = 23 := by native_decide
example : radixRepresentativeBudget 5 12 = 21 := by native_decide
example : maximumLayerCompilerBudgetBound 5 89 1 = 38 := by native_decide
example : maximumLayerCompilerTestBound 5 89 1 = 161 := by native_decide
example : maximumLayerCompilerTotalTests 5 89 1 ≤ maximumLayerCompilerBudgetBound 5 89 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 89 1 ≤ maximumLayerCompilerTestBound 5 89 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 89 1 (by decide) (by decide)).totalTests = 23 := by native_decide
example : maximumLayerCompilerTotalTests 5 89 3 = 15 := by native_decide
example : radixRepresentativeBudget 5 6 = 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 89 3 = 18 := by native_decide
example : maximumLayerCompilerTestBound 5 89 3 = 47 := by native_decide
example : maximumLayerCompilerTotalTests 5 89 3 ≤ maximumLayerCompilerBudgetBound 5 89 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 89 3 ≤ maximumLayerCompilerTestBound 5 89 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 89 3 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 5 89 7 = 7 := by native_decide
example : radixRepresentativeBudget 5 3 = 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 89 7 = 11 := by native_decide
example : maximumLayerCompilerTestBound 5 89 7 = 17 := by native_decide
example : maximumLayerCompilerTotalTests 5 89 7 ≤ maximumLayerCompilerBudgetBound 5 89 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 89 7 ≤ maximumLayerCompilerTestBound 5 89 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 89 7 (by decide) (by decide)).totalTests = 7 := by native_decide
example : maximumLayerCompilerTotalTests 5 144 0 = 75 := by native_decide
example : radixRepresentativeBudget 5 36 = 148 := by native_decide
example : maximumLayerCompilerBudgetBound 5 144 0 = 189 := by native_decide
example : maximumLayerCompilerTestBound 5 144 0 = 1337 := by native_decide
example : maximumLayerCompilerTotalTests 5 144 0 ≤ maximumLayerCompilerBudgetBound 5 144 0 := by native_decide
example : maximumLayerCompilerBudgetBound 5 144 0 ≤ maximumLayerCompilerTestBound 5 144 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 144 0 (by decide) (by decide)).totalTests = 75 := by native_decide
example : maximumLayerCompilerTotalTests 5 144 1 = 37 := by native_decide
example : radixRepresentativeBudget 5 18 = 42 := by native_decide
example : maximumLayerCompilerBudgetBound 5 144 1 = 65 := by native_decide
example : maximumLayerCompilerTestBound 5 144 1 = 347 := by native_decide
example : maximumLayerCompilerTotalTests 5 144 1 ≤ maximumLayerCompilerBudgetBound 5 144 1 := by native_decide
example : maximumLayerCompilerBudgetBound 5 144 1 ≤ maximumLayerCompilerTestBound 5 144 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 144 1 (by decide) (by decide)).totalTests = 37 := by native_decide
example : maximumLayerCompilerTotalTests 5 144 3 = 19 := by native_decide
example : radixRepresentativeBudget 5 9 = 13 := by native_decide
example : maximumLayerCompilerBudgetBound 5 144 3 = 27 := by native_decide
example : maximumLayerCompilerTestBound 5 144 3 = 95 := by native_decide
example : maximumLayerCompilerTotalTests 5 144 3 ≤ maximumLayerCompilerBudgetBound 5 144 3 := by native_decide
example : maximumLayerCompilerBudgetBound 5 144 3 ≤ maximumLayerCompilerTestBound 5 144 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 144 3 (by decide) (by decide)).totalTests = 19 := by native_decide
example : maximumLayerCompilerTotalTests 5 144 7 = 13 := by native_decide
example : radixRepresentativeBudget 5 5 = 5 := by native_decide
example : maximumLayerCompilerBudgetBound 5 144 7 = 15 := by native_decide
example : maximumLayerCompilerTestBound 5 144 7 = 35 := by native_decide
example : maximumLayerCompilerTotalTests 5 144 7 ≤ maximumLayerCompilerBudgetBound 5 144 7 := by native_decide
example : maximumLayerCompilerBudgetBound 5 144 7 ≤ maximumLayerCompilerTestBound 5 144 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 5 144 7 (by decide) (by decide)).totalTests = 13 := by native_decide
