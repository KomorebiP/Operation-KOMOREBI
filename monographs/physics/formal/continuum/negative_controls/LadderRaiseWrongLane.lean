import KomorebiPhysics.LadderExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : projector 3 1 (raise (packet 3 2 (single 8 1))) ≠ 0 := by
  simp only [raising_wrong_lane, ne_eq, not_true_eq_false]
end
