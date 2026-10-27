import KomorebiPhysics.LadderExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : ∑ k : ZMod 3,
    ZMod.stdAddChar (-((1 : ZMod 3)*k)) * ZMod.stdAddChar (k*(1 : ZMod 3)) = (1 : ℂ) := by
  rw [unnormalized_character_sum]
  norm_num
end
