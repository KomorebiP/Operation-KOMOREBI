import MachineTheory.ApproximationExamples
open Komorebi.MachineTheory
open Instrument Variation ApproximateHistory ApproximateDecision ApproximationExamples
open scoped BigOperators
noncomputable section
example : risk truthLaw (classificationLoss false)-risk truthLaw (classificationLoss true) ≤ tv truthLaw truthLaw := by
  rw [classification_values.1,classification_values.2.1,tv_self]
  norm_num

end
