import PaperX.PrecisionExamples
open PaperX.PrecisionExamples
example : ∃ P : Matrix (Fin 2) (Fin 2) ℤ_[2],
    P.map modFour = initialLift.map modFour ∧
    ∀ g, rho g * P = P * tau g := by
  rw [iff_false_intro no_exact_intertwiner_preserves_mod_four]
