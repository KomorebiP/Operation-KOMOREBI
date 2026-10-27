import MachineTheory.JointReconstructionExamples
open Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

example : ∃ D : State₂ →ₗ[F₂] State₃, LinearMap.id = D.comp joint₃ := by
  simp only [iff_false_intro extra_nuisance_no_full_linear_decoder]

end
