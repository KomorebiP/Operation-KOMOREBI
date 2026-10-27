import KomorebiPhysics.Relativistic3DCenteredResolvent
noncomputable section
open Filter
open scoped Topology
open KomorebiPhysics.Relativistic3DCenteredResolvent
open KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics.Relativistic3DFourierHilbertStability
abbrev ResolventTestCoefficients := KomorebiPhysics.Relativistic3DFullFourierEvolution.CoeffL2
abbrev ResolventTestPhysical := KomorebiPhysics.Relativistic3DTorusFourierEvolution.TorusSpinorL2
example (m : ℝ) (f : ResolventTestCoefficients) :
    continuumCoeffResolvent m (1 + Complex.I) (by norm_num) f ∈
      KomorebiPhysics.Relativistic3DUnboundedDirac.continuumDiracDomain m :=
  continuumCoeffResolvent_mem_domain m (1 + Complex.I) (by norm_num) f

example (m h : ℝ) : ‖centeredCoeffResolvent m h (1 + Complex.I) (by norm_num)‖ ≤ 1 := by
  simpa using centeredCoeffResolvent_norm_le m h (1 + Complex.I) (by norm_num)
