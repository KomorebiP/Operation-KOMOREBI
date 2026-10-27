import MachineTheory.JointReconstructionExamples
open Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

example : ∃ D : F₂ → F₂, ∀ x, D (display₂ x) = physical₂ x := by
  simp only [iff_false_intro display_alone_impossible]

end
