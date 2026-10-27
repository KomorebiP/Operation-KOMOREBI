import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : 0 < weight mass2 coordinateFamily (1, 0) true := by
  norm_num [weight, mass2, coordinateFamily, rightPacket, first, second]
