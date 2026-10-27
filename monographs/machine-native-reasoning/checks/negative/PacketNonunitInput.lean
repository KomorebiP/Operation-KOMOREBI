import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : (∑ b : Bool, weight mass2 coordinateFamily (2, 0) b) = 1 := by
  norm_num [weight, mass2, coordinateFamily, leftPacket, rightPacket, first, second]
