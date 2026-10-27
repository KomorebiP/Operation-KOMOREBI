import KomorebiPadic.RepresentativeBudgetClosedForm

open KomorebiPadic

/-! Independently generated Block 10 kernel checks, chunk 17/17. -/

example : maximumLayerCompilerClosedBudgetBound 13 55 1 = 19 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 1 = 19 := by native_decide
example : maximumLayerCompilerClosedBudgetBound 13 55 3 = 17 := by native_decide
example : maximumLayerCompilerBudgetBound 13 55 3 = 17 := by native_decide
example : maximumLayerCompilerClosedBudgetBound 13 89 0 = 29 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 0 = 29 := by native_decide
example : maximumLayerCompilerClosedBudgetBound 13 89 1 = 21 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 1 = 21 := by native_decide
example : maximumLayerCompilerClosedBudgetBound 13 89 3 = 17 := by native_decide
example : maximumLayerCompilerBudgetBound 13 89 3 = 17 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 2 1 0 (by decide) (by decide)).quotientBound = 1 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 2 1 0 (by decide) (by decide)).blockQuotient = 0 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 2 1 0 (by decide) (by decide)).blockRemainder = 0 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 2 8 2 (by decide) (by decide)).quotientBound = 3 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 2 8 2 (by decide) (by decide)).blockQuotient = 1 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 2 8 2 (by decide) (by decide)).blockRemainder = 0 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 3 13 1 (by decide) (by decide)).quotientBound = 4 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 3 13 1 (by decide) (by decide)).blockQuotient = 1 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 3 13 1 (by decide) (by decide)).blockRemainder = 0 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 5 21 3 (by decide) (by decide)).quotientBound = 2 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 5 21 3 (by decide) (by decide)).blockQuotient = 0 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 5 21 3 (by decide) (by decide)).blockRemainder = 1 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 7 34 1 (by decide) (by decide)).quotientBound = 3 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 7 34 1 (by decide) (by decide)).blockQuotient = 0 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 7 34 1 (by decide) (by decide)).blockRemainder = 2 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 13 55 0 (by decide) (by decide)).quotientBound = 5 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 13 55 0 (by decide) (by decide)).blockQuotient = 0 := by native_decide
example : (maximumLayerCompilerClosedFormCertificate 13 55 0 (by decide) (by decide)).blockRemainder = 4 := by native_decide
