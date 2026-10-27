import PaperX.PrecisionBoundary
open PaperX.PrecisionBoundary PaperX.RepresentationClasses
example : Conjugate trivial PaperX.PrecisionExamples.tau := by
  rw [iff_false_intro sign_not_integrally_conjugate_trivial]
