import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : offImage₀ = offImage₁ := by
  simp only [iff_false_intro missing_surjectivity_two_quotients.2.2]
