import KomorebiPhysics.CurrentSummationExamples
open KomorebiPhysics.CurrentSummationExamples
noncomputable section
example : (∀ i : Label, Summable (cycles i)) →
    Summable (fun ij : Label × Label => cycles ij.1 ij.2) := by
  intro _
  simp only [not_joint_summable]
end
