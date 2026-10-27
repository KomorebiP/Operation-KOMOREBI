import MachineTheory.JointReconstructionExamples
open Komorebi.MachineTheory.JointReconstructionExamples
noncomputable section

example : ¬ ∃ D : State₂ → F₂, ∀ x, D (joint₂ x) = calibration₂ x := by
  have h : ∃ D : State₂ → F₂, ∀ x, D (joint₂ x) = calibration₂ x :=
    ⟨fun r => r.2, fun _ => rfl⟩
  simp only [h, not_true_eq_false]

end
