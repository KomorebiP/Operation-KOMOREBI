import PaperX.PrecisionExamples
open PaperX.PrecisionExamples PaperX.CompletionExamples
example : rho generator * initialLift = initialLift * tau generator := by
  rw [iff_false_intro initial_lift_not_intertwiner]
