import KomorebiPhysics.LadderExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : lower (single 9 1) = lp.single 2 8 (9 : ℂ) := by
  simp only [wrong_square_root_amplitude]
end
