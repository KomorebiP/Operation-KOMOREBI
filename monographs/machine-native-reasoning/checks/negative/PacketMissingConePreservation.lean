import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : 0 ≤ weight mass2 signedFamily (1, 0) false := by
  rw [signed_weight_negative]
  norm_num
