import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : detail (3 / 4, 1 / 4) ∈ quadrant := by
  rw [haar_detail_packet]
  norm_num [quadrant]
