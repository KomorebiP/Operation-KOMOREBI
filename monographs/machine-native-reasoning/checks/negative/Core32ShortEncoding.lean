import MachineTheory.OccupancyExamples
open Komorebi.MachineTheory.PartitionCorrection
open Komorebi.MachineTheory.PartitionCorrection.Examples

-- Deliberately invalid: an optimal four-bit encoding is not a three-bit encoding.
example : Set SensorWorld → (Fin 3 → Bool) := encode sensorCell sensorTarget
