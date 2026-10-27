import MachineTheory.OccupancyExamples
open Komorebi.MachineTheory.PartitionCorrection
open Komorebi.MachineTheory.PartitionCorrection.Examples

-- Deliberately false: adding an unused ambient target does not create a pair.
example : ∃ d : Pair oneCell natTarget, d.val.2 = 2 := by
  refine ⟨pair oneCell natTarget false, ?_⟩
  decide
