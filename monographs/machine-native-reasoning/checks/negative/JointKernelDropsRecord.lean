import MachineTheory.JointReconstructionExamples
open Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

example : LinearMap.ker joint₂ = LinearMap.ker display₂ := by
  have hn : LinearMap.ker joint₂ ≠ LinearMap.ker display₂ := by
    intro h
    have hv : (1,1) ∈ LinearMap.ker joint₂ := by
      rw [h]
      exact lost_direction_is_removed.1
    exact lost_direction_is_removed.2 hv
  simp only [iff_false_intro hn]

end
