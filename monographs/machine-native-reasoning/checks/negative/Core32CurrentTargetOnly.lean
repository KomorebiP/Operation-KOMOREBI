import MachineTheory.OccupancyExamples
open Komorebi.MachineTheory.PartitionCorrection
open Komorebi.MachineTheory.PartitionCorrection.Examples

-- Deliberately false: equal current targets need not give equal future signatures.
example : (algebra sensorCell).signature sensorTarget sensorV =
    (algebra sensorCell).signature sensorTarget sensorW := by
  exact sensor_present_targets_equal
