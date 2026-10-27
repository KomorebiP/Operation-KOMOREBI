import KomorebiPhysics.Relativistic3DUnboundedDirac
open KomorebiPhysics.Relativistic3DUnboundedDirac

example : ¬ (continuumDiracPMap 0).IsClosed := by
  exact continuumDiracPMap_isClosed 0
