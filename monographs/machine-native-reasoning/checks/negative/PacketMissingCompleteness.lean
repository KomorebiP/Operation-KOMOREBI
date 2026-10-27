import MachineTheory.PositivePacketExamples

open Komorebi.MachineTheory.PositivePackets
open Komorebi.MachineTheory.PositivePackets.Examples
open scoped BigOperators

-- Deliberately false boundary fixture.
example : weight mass2 (fun _ : Unit => halfIdentity) (1, 0) () = 1 := by
  rw [incomplete_weight_counterexample]
  norm_num
