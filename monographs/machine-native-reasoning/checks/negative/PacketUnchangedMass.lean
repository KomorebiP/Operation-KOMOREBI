import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : mass2 (shear (0, 1)) = 1 := by
  norm_num [mass2, first, second, shear]
