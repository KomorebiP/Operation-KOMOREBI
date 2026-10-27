import MachineTheory.PlanningControls
open Komorebi.MachineTheory
open Planning PlanningSensor PlanningControls
noncomputable section
example : value expensiveSensor 1 (0,0) = 3/10 := by
  rw [expensive_value]
  norm_num
end
