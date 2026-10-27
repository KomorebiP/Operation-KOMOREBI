module
public import DyadicExamples
example : (6:ℤ) ≤ padicValRat 2 ((KomorebiPaperIX.EulerCoefficients.eulerEven 4 : ℚ) - KomorebiPaperIX.DyadicReconstruction.truncation 4 0) := by
  rw [KomorebiPaperIX.DyadicExamples.manuscript_error_zero_valuation]
  norm_num
