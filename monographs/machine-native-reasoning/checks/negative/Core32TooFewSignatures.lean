import MachineTheory.OccupancyExamples
open Komorebi.MachineTheory.PartitionCorrection
open Komorebi.MachineTheory.PartitionCorrection.Examples

-- Deliberately false: three bits cannot name all sixteen sensor signatures.
example : Fintype.card ((algebra sensorCell).Memory sensorTarget) = 8 := by
  rw [sensor_signature_count]
  decide
