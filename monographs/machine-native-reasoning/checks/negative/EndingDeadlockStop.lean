import MachineTheory.SafeEndingExamples
open Komorebi.MachineTheory.SafeEnding Komorebi.MachineTheory.SafeEnding.Examples

example : EndingGuarantee deadlock (fun _ => none) () := by
  simp only [iff_false_intro (deadlock_no_ending (fun _ => none))]
