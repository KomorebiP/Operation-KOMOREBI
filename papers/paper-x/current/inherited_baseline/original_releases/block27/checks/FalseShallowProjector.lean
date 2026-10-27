import PaperX.SummandBoundary
open PaperX.SummandBoundary PaperX.PrecisionExamples PaperX.CompletionExamples
example : ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[2],
    P.map modTwo = (skewProjector 1).map modTwo ∧
    ∀ g : C2, tau g * P = P * tau g := by
  rw [iff_false_intro no_exact_endomorphism_retains_skew_one]
