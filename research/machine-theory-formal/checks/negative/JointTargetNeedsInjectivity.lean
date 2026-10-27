import MachineTheory.JointReconstructionExamples
open Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

example : (∃ D : State₂ →ₗ[F₂] F₂, physical₃ = D.comp joint₃) →
    Function.Injective joint₃ := by
  intro _
  simp only [iff_false_intro extra_nuisance_not_injective]

end
