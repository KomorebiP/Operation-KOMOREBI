import KomorebiPhysics.Relativistic3DUnboundedDirac
open KomorebiPhysics.Relativistic3DUnboundedDirac

example : ¬ IsSelfAdjoint (continuumDiracPMap 0) := by
  exact continuumDiracPMap_selfAdjoint 0
