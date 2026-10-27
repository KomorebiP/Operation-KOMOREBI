import KomorebiPhysics.Relativistic3DGeneratorBridge
noncomputable section
open KomorebiPhysics.Relativistic3DGeneratorBridge
open KomorebiPhysics.Relativistic3DWeightedDomain
open KomorebiPhysics.Relativistic3DTorusFourierEvolution
open scoped LinearPMap

example (m : ℝ) (f : physicalDiracDomain m) :
  HasDerivAt (fun t => continuumTorusUnitary m t f.1)
    (Complex.I • physicalDiracPMap m f) 0 :=
  physical_orbit_hasDerivAt_zero m f
