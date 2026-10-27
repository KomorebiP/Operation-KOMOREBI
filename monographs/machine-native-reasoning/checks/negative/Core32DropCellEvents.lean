import MachineTheory.OccupancyExamples
open Komorebi.MachineTheory.PartitionCorrection
open Komorebi.MachineTheory.PartitionCorrection.Examples

-- Deliberately false: after removing singleton-cell events, the old two-cell
-- occupancy count is no longer the exact signature count for a constant target.
example : Fintype.card ((algebra oneCell).Memory constantTarget) = 4 := by
  rw [one_cell_signature_count]
  decide
