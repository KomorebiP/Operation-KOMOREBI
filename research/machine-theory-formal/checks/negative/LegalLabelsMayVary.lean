import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : FibreCompatible labelBad (fun _ => ()) := by
  simp only [iff_false_intro labels_block_collapse]
