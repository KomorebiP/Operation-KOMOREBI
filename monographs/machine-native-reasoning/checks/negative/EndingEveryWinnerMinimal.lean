import MachineTheory.SafeEndingExamples
open Komorebi.MachineTheory.SafeEnding Komorebi.MachineTheory.SafeEnding.Examples

example : 2 ≤ endRank waitModel true := by
  simp [wait_rank]
