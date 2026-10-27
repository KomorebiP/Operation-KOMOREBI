import MachineTheory.ResponseExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateDecision ResponseDecision DecisionHistory ResponseExamples
noncomputable section
example : IsDist (recordAfter id (∅ : Finset Bool) (basis false)) := by
  norm_num [IsDist, recordAfter, mass, push, normalize, restrict, Fintype.sum_bool]
end
