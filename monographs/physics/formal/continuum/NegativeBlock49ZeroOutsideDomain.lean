import KomorebiPhysics.Relativistic3DWeightedDiracDomain
open KomorebiPhysics.Relativistic3DWeightedDomain

example : (0 : TorusSpinorL2) ∉ physicalDiracDomain 0 := by
  simp [physicalDiracDomain]
