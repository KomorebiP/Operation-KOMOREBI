import MachineTheory.JointReconstructionExamples
open Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

example : extension₀ = extension₁ := by
  simp only [iff_false_intro extensions_differ_outside_range]

end
