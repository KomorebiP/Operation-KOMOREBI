import StepAmplificationExamples
open KomorebiPaperIX KomorebiPaperIX.Mahler KomorebiPaperIX.GlobalEulerBoundary
example : precision 2 2 (difference 1 1 (Congruential.coeff 4 0) 1) := by
  exact DyadicStepAmplification.normalized_precision 0 1 1 1 (by decide)
