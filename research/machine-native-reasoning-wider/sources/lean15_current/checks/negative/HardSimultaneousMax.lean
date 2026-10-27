import MachineTheory.HardExamples
import MachineTheory.HardControls
open Komorebi.MachineTheory
open HardInquiry HardExamples HardControls Finset

/-- Intentionally false boundary claim. -/
example : (twoCoordinates.execute twoCharge 1 bitTree false).map (fun r => (r.cost false,r.cost true)) = some (10,10) := by
  simp only [maxima_not_one_execution false]
