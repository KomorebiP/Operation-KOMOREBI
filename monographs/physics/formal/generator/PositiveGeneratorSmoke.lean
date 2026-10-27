import KomorebiPhysics.Relativistic3DGeneratorBridge
noncomputable section
open KomorebiPhysics.Relativistic3DGeneratorBridge
open KomorebiPhysics.Relativistic3DWeightedDomain
open KomorebiPhysics.Relativistic3DTorusFourierEvolution
open scoped LinearPMap

example (m : ℝ) (f : KomorebiPhysics.Relativistic3DTorusFourierEvolution.TorusSpinorL2) :
  DifferentiableAt ℝ (fun t => continuumTorusUnitary m t f) 0 ↔
    f ∈ physicalDiracDomain m := physical_differentiableAt_zero_iff_mem_domain m f
example (m : ℝ) (f : physicalDiracDomain m) (t : ℝ) :
  HasDerivAt (fun s => continuumTorusUnitary m s f.1)
    ((-Complex.I) • physicalDiracPMap m (physicalEvolvedDomain m t f)) t :=
  physical_schrodinger_hasDerivAt m f t
example (m : ℝ) (f : physicalDiracDomain m) :
  deriv (fun t => continuumTorusUnitary m t f.1) 0 =
    (-Complex.I) • physicalDiracPMap m f := physical_deriv_zero m f
