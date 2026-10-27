import MachineTheory.PlanningControls
open Komorebi.MachineTheory
open Planning PlanningSensor PlanningControls
noncomputable section
example : Feasible oneReport 0 () dormantBranch := by
  simp [Feasible, dormantBranch]
end
