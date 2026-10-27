import MachineTheory.JointReconstructionExamples
open Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

example : ∃ D : F₂ → F₂, ∀ x, D (calibration₂ x) = physical₂ x := by
  simp only [iff_false_intro calibration_alone_impossible]

end
