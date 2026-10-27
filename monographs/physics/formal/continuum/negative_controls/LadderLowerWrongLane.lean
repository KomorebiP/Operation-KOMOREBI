import KomorebiPhysics.LadderExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : projector 3 0 (lower (packet 3 0 (single 9 1))) ≠ 0 := by
  simp only [lowering_wrong_lane, ne_eq, not_true_eq_false]
end
