import KomorebiPhysics.Relativistic3DGeneratorBridge
noncomputable section
open KomorebiPhysics.Relativistic3DGeneratorBridge
open KomorebiPhysics.Relativistic3DWeightedDomain
open KomorebiPhysics.Relativistic3DTorusFourierEvolution
open scoped LinearPMap

example (m : ℝ) (f : physicalDiracDomain m) :
  deriv (fun t => continuumTorusUnitary m t f.1) 0 = physicalDiracPMap m f :=
  physical_deriv_zero m f
