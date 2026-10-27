import KomorebiPhysics.CurrentSummationExamples
open KomorebiPhysics.CurrentSummationExamples
open scoped BigOperators
noncomputable section
example : (HasSum (fun i : Label => ∑' j, cycles i j) 0 ∧
    HasSum (fun j : Label => ∑' i, cycles i j) 0) →
    Summable (fun ij : Label × Label => cycles ij.1 ij.2) := by
  intro _
  simp only [not_joint_summable]
end
