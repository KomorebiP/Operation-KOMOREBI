import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : mass2 ((0 : ℝ)⁻¹ • (0 : V2)) = 1 := by
  norm_num [mass2, first, second]
