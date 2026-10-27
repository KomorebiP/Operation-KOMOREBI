import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : halfIdentity (halfIdentity (1, 0)) = halfIdentity (1, 0) := by
  norm_num [halfIdentity]
