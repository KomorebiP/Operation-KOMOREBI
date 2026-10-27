import MachineTheory
open Komorebi.MachineTheory
open Planning PlanningSensor PlanningControls
noncomputable section
example : OptimalFirst differentTargets 0 true (.inl false) := by
  norm_num [value, finiteMin, menu, differentTargets, permissions, OptimalFirst, firstValue]
end
