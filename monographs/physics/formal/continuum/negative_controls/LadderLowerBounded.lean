import KomorebiPhysics.LadderExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : ∃ A : Space →L[ℂ] Space, ∀ x : domain, lower x = A x := by
  simp only [no_bounded_lower_extension]
end
