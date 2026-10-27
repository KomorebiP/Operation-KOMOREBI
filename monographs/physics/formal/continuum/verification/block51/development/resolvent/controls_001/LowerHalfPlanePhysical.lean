import KomorebiPhysics.Relativistic3DCenteredResolvent
noncomputable section
open Filter
open scoped Topology
open KomorebiPhysics.Relativistic3DCenteredResolvent
open KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics.Relativistic3DFourierHilbertStability
abbrev CoeffL2 := KomorebiPhysics.Relativistic3DFullFourierEvolution.CoeffL2
abbrev TorusSpinorL2 := KomorebiPhysics.Relativistic3DTorusFourierEvolution.TorusSpinorL2
example (m : ℝ) (f : TorusSpinorL2) :
    Tendsto (fun h => physicalCenteredResolvent m h (-Complex.I) (by norm_num) f)
      (𝓝[≠] 0) (𝓝 (physicalContinuumResolvent m (-Complex.I) (by norm_num) f)) :=
  physical_centered_resolvent_tendsto m (-Complex.I) (by norm_num) f

example (m h : ℝ) (hh : h ≠ 0) (f : TorusSpinorL2) :
    physicalCenteredResolvent m h (-Complex.I) (by norm_num)
      (physicalCenteredOperator m h f - (-Complex.I) • f) = f :=
  physical_centered_resolvent_shift m h hh (-Complex.I) (by norm_num) f
