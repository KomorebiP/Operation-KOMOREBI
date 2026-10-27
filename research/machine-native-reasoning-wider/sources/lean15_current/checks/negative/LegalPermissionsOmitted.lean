import MachineTheory.LegalQuotientExamples
open Komorebi.MachineTheory LegalQuotient LegalQuotientExamples

example : FibreCompatible permissionBad (fun _ => ()) := by
  simp only [iff_false_intro permissions_block_collapse]
