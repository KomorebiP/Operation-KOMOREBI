import MachineTheory.OccupancyExamples
open Komorebi.MachineTheory.PartitionCorrection
open Komorebi.MachineTheory.PartitionCorrection.Examples

-- Deliberately false: contradictory evidence is not replaced with a world.
example : occupancy sensorCell sensorTarget ∅ ≠ ∅ := by
  simp
