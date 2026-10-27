import MachineTheory.SafeEndingExamples
open Komorebi.MachineTheory.SafeEnding Komorebi.MachineTheory.SafeEnding.Examples

example : (2 : Fin 3) ∈ runningRegion threeState := by
  simp [three_running]
