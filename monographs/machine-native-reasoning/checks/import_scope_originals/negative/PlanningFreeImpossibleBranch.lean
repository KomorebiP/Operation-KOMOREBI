import MachineTheory
open Komorebi.MachineTheory
open Planning PlanningSensor PlanningControls
noncomputable section
example : evaluate oneReport dormantBranch () = 1/2 := by
  rw [impossible_branch_cost_zero]
  norm_num
end
