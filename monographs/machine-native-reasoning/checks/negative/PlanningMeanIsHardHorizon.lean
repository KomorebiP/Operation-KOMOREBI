import MachineTheory.PlanningControls
open Komorebi.MachineTheory
open Planning PlanningSensor PlanningControls
noncomputable section
example : adaptiveThree.Bounded 2 := by
  simp [adaptiveThree, Tree.Bounded]
end
