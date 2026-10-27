import KomorebiPadic.CompilerComplexity

open KomorebiPadic

/-! Independently generated Block 09 kernel checks, chunk 4/25. -/

example : maximumLayerCompilerTotalTests 2 55 0 = 131 := by native_decide
example : radixRepresentativeBudget 2 55 = 784 := by native_decide
example : maximumLayerCompilerBudgetBound 2 55 0 = 841 := by native_decide
example : maximumLayerCompilerTestBound 2 55 0 = 3082 := by native_decide
example : maximumLayerCompilerTotalTests 2 55 0 ≤ maximumLayerCompilerBudgetBound 2 55 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 55 0 ≤ maximumLayerCompilerTestBound 2 55 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 55 0 (by decide) (by decide)).totalTests = 131 := by native_decide
example : maximumLayerCompilerTotalTests 2 55 1 = 59 := by native_decide
example : radixRepresentativeBudget 2 28 = 210 := by native_decide
example : maximumLayerCompilerBudgetBound 2 55 1 = 240 := by native_decide
example : maximumLayerCompilerTestBound 2 55 1 = 814 := by native_decide
example : maximumLayerCompilerTotalTests 2 55 1 ≤ maximumLayerCompilerBudgetBound 2 55 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 55 1 ≤ maximumLayerCompilerTestBound 2 55 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 55 1 (by decide) (by decide)).totalTests = 59 := by native_decide
example : maximumLayerCompilerTotalTests 2 55 3 = 30 := by native_decide
example : radixRepresentativeBudget 2 14 = 56 := by native_decide
example : maximumLayerCompilerBudgetBound 2 55 3 = 72 := by native_decide
example : maximumLayerCompilerTestBound 2 55 3 = 212 := by native_decide
example : maximumLayerCompilerTotalTests 2 55 3 ≤ maximumLayerCompilerBudgetBound 2 55 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 55 3 ≤ maximumLayerCompilerTestBound 2 55 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 55 3 (by decide) (by decide)).totalTests = 30 := by native_decide
example : maximumLayerCompilerTotalTests 2 55 7 = 15 := by native_decide
example : radixRepresentativeBudget 2 7 = 16 := by native_decide
example : maximumLayerCompilerBudgetBound 2 55 7 = 25 := by native_decide
example : maximumLayerCompilerTestBound 2 55 7 = 58 := by native_decide
example : maximumLayerCompilerTotalTests 2 55 7 ≤ maximumLayerCompilerBudgetBound 2 55 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 55 7 ≤ maximumLayerCompilerTestBound 2 55 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 55 7 (by decide) (by decide)).totalTests = 15 := by native_decide
example : maximumLayerCompilerTotalTests 2 89 0 = 220 := by native_decide
example : radixRepresentativeBudget 2 89 = 2025 := by native_decide
example : maximumLayerCompilerBudgetBound 2 89 0 = 2116 := by native_decide
example : maximumLayerCompilerTestBound 2 89 0 = 8012 := by native_decide
example : maximumLayerCompilerTotalTests 2 89 0 ≤ maximumLayerCompilerBudgetBound 2 89 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 89 0 ≤ maximumLayerCompilerTestBound 2 89 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 89 0 (by decide) (by decide)).totalTests = 220 := by native_decide
example : maximumLayerCompilerTotalTests 2 89 1 = 94 := by native_decide
example : radixRepresentativeBudget 2 45 = 529 := by native_decide
example : maximumLayerCompilerBudgetBound 2 89 1 = 576 := by native_decide
example : maximumLayerCompilerTestBound 2 89 1 = 2072 := by native_decide
example : maximumLayerCompilerTotalTests 2 89 1 ≤ maximumLayerCompilerBudgetBound 2 89 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 89 1 ≤ maximumLayerCompilerTestBound 2 89 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 89 1 (by decide) (by decide)).totalTests = 94 := by native_decide
example : maximumLayerCompilerTotalTests 2 89 3 = 45 := by native_decide
example : radixRepresentativeBudget 2 23 = 144 := by native_decide
example : maximumLayerCompilerBudgetBound 2 89 3 = 169 := by native_decide
example : maximumLayerCompilerTestBound 2 89 3 = 554 := by native_decide
example : maximumLayerCompilerTotalTests 2 89 3 ≤ maximumLayerCompilerBudgetBound 2 89 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 89 3 ≤ maximumLayerCompilerTestBound 2 89 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 89 3 (by decide) (by decide)).totalTests = 45 := by native_decide
example : maximumLayerCompilerTotalTests 2 89 7 = 23 := by native_decide
example : radixRepresentativeBudget 2 12 = 42 := by native_decide
example : maximumLayerCompilerBudgetBound 2 89 7 = 56 := by native_decide
example : maximumLayerCompilerTestBound 2 89 7 = 158 := by native_decide
example : maximumLayerCompilerTotalTests 2 89 7 ≤ maximumLayerCompilerBudgetBound 2 89 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 89 7 ≤ maximumLayerCompilerTestBound 2 89 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 89 7 (by decide) (by decide)).totalTests = 23 := by native_decide
example : maximumLayerCompilerTotalTests 2 144 0 = 380 := by native_decide
example : radixRepresentativeBudget 2 144 = 5256 := by native_decide
example : maximumLayerCompilerBudgetBound 2 144 0 = 5402 := by native_decide
example : maximumLayerCompilerTestBound 2 144 0 = 20882 := by native_decide
example : maximumLayerCompilerTotalTests 2 144 0 ≤ maximumLayerCompilerBudgetBound 2 144 0 := by native_decide
example : maximumLayerCompilerBudgetBound 2 144 0 ≤ maximumLayerCompilerTestBound 2 144 0 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 144 0 (by decide) (by decide)).totalTests = 380 := by native_decide
example : maximumLayerCompilerTotalTests 2 144 1 = 160 := by native_decide
example : radixRepresentativeBudget 2 72 = 1332 := by native_decide
example : maximumLayerCompilerBudgetBound 2 144 1 = 1406 := by native_decide
example : maximumLayerCompilerTestBound 2 144 1 = 5258 := by native_decide
example : maximumLayerCompilerTotalTests 2 144 1 ≤ maximumLayerCompilerBudgetBound 2 144 1 := by native_decide
example : maximumLayerCompilerBudgetBound 2 144 1 ≤ maximumLayerCompilerTestBound 2 144 1 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 144 1 (by decide) (by decide)).totalTests = 160 := by native_decide
example : maximumLayerCompilerTotalTests 2 144 3 = 73 := by native_decide
example : radixRepresentativeBudget 2 36 = 342 := by native_decide
example : maximumLayerCompilerBudgetBound 2 144 3 = 380 := by native_decide
example : maximumLayerCompilerTestBound 2 144 3 = 1334 := by native_decide
example : maximumLayerCompilerTotalTests 2 144 3 ≤ maximumLayerCompilerBudgetBound 2 144 3 := by native_decide
example : maximumLayerCompilerBudgetBound 2 144 3 ≤ maximumLayerCompilerTestBound 2 144 3 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 144 3 (by decide) (by decide)).totalTests = 73 := by native_decide
example : maximumLayerCompilerTotalTests 2 144 7 = 37 := by native_decide
example : radixRepresentativeBudget 2 18 = 90 := by native_decide
example : maximumLayerCompilerBudgetBound 2 144 7 = 110 := by native_decide
example : maximumLayerCompilerTestBound 2 144 7 = 344 := by native_decide
example : maximumLayerCompilerTotalTests 2 144 7 ≤ maximumLayerCompilerBudgetBound 2 144 7 := by native_decide
example : maximumLayerCompilerBudgetBound 2 144 7 ≤ maximumLayerCompilerTestBound 2 144 7 := by native_decide
example : (maximumLayerCompilerComplexityCertificate 2 144 7 (by decide) (by decide)).totalTests = 37 := by native_decide
