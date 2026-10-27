import MachineTheory.PlanningControls
open Komorebi.MachineTheory
open Planning PlanningSensor PlanningControls
noncomputable section
example : Feasible permissions 0 true (.stop false) := by
  simp [Feasible, permissions]
end
