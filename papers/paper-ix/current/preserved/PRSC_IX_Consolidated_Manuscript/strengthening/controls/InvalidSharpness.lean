import DyadicSharpTower
open KomorebiPaperIX KomorebiPaperIX.DyadicSharpTower KomorebiPaperIX.DyadicReconstruction
example : padicValRat 2 ((EulerCoefficients.eulerEven 1:ℚ) - truncation 1 0) = 4 := by
  have h := first_omitted_error_valuation 0
  norm_num at h
  exact h
