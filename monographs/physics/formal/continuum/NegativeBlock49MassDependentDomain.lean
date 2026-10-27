import KomorebiPhysics.Relativistic3DWeightedDiracDomain
open KomorebiPhysics.Relativistic3DWeightedDomain

example : physicalDiracDomain 0 ≠ physicalDiracDomain 1 := by
  exact physicalDiracDomain_eq_mass 0 1
