import PaperX.GeneralLogarithmExamples
open PaperX.GeneralLogarithmExamples PaperX.AffineMonodromy
open PaperX.LogarithmicRecovery PaperX.NilpotentExponential
example : recoverN 0 (expN datum3.N 0) = datum3.N := by
  rw [iff_false_intro general_zero_parameter_recovery_fails]
