import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : (coarse.step false true).getD false = (coarse.step false true).getD true := by
  simp only [iff_false_intro disabled_totalizations_not_unique.2]
