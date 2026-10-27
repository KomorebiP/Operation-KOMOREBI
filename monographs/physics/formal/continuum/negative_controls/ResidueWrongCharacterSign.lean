import KomorebiPhysics.LadderExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral
open KomorebiPhysics.LadderDomains KomorebiPhysics.LadderExamples
open KomorebiPhysics.LadderRouting KomorebiPhysics.ResidueProjectors
open scoped BigOperators lp
noncomputable section
example : (3 : ℂ)⁻¹ * ∑ k : ZMod 3,
    ZMod.stdAddChar ((1 : ZMod 3)*k) * ZMod.stdAddChar (k*(1 : ZMod 3)) = 1 := by
  rw [ResidueCharacters.wrong_sign_three]
  norm_num
end
