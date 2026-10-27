import KomorebiPhysics.LadderExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : lower (single 0 1) ≠ 0 := by
  simp only [vacuum_lowering, ne_eq, not_true_eq_false]
end
