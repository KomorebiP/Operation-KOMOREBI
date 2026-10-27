import KomorebiPhysics.Relativistic3DGeneratorBridge
noncomputable section
open KomorebiPhysics.Relativistic3DGeneratorBridge
open KomorebiPhysics.Relativistic3DWeightedDomain
open KomorebiPhysics.Relativistic3DTorusFourierEvolution
open scoped LinearPMap

example (m : ℝ) (f : KomorebiPhysics.Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
  DifferentiableAt ℝ (fun t => continuumTorusUnitary m t f) 0 :=
  (physical_orbit_hasDerivAt_zero m f).differentiableAt
