import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : (LinearMap.id : V2 →ₗ[ℝ] V2) ((LinearMap.id : V2 →ₗ[ℝ] V2) (1, 0)) = 0 := by
  norm_num
