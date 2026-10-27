import MachineTheory.JointReconstructionExamples
open Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

example : (∃ D : State₂ →ₗ[F₂] F₂, LinearMap.id = D.comp embeddedRecord) →
    Function.Surjective embeddedRecord := by
  intro _
  simp only [iff_false_intro proper_range_not_surjective]

end
