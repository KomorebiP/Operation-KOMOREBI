import KomorebiLSM.Block4Examples

open Komorebi.LSM.FiniteBayes Komorebi.LSM.FiniteInstruments Komorebi.LSM.Block4Examples

example : ∃ f : ℝ → ℝ, ∀ p, IsPrior p →
    f (mass p) = mass (tinyInstrument.branch ((),true) p) := by
  simp only [mass_alone_cannot_predict]
