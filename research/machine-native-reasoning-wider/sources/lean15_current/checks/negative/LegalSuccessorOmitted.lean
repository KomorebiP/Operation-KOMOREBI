import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : FibreCompatible successorBad forgetHistory := by
  simp only [iff_false_intro successors_block_quotient]
