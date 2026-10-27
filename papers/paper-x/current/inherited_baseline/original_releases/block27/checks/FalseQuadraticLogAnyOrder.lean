import PaperX.GeneralLogarithmExamples
open PaperX.ReconstructionBoundary PaperX.UnipotentLogarithm PaperX.NilpotentExponential
example : log₂ (expN datum4.N 1) = datum4.N := by
  rw [iff_false_intro quadratic_log_fails_beyond_cube]
