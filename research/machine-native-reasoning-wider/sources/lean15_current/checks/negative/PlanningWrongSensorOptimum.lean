import MachineTheory
open Komorebi.MachineTheory
open Planning PlanningSensor PlanningControls
noncomputable section
example : value countModel 3 (0,0) = 3/10 := by
  rw [sensor_value_table.2.2.2]
  norm_num
end
