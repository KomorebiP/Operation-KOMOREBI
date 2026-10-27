import KomorebiPhysics.Relativistic3DWeightedDiracDomain
open KomorebiPhysics.Relativistic3DWeightedDomain

example : ¬ IsSelfAdjoint (physicalDiracPMap 0) := by
  exact physicalDiracPMap_selfAdjoint 0
