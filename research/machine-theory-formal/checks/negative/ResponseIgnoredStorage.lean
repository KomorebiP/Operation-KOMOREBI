import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : tv modelPosterior storedRecord ≤ 0 := by
  rw [stored_record_error]; norm_num
end
