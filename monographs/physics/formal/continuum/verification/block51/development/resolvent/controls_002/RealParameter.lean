import KomorebiPhysics.Relativistic3DCenteredResolvent
noncomputable section
open Filter
open scoped Topology
open KomorebiPhysics.Relativistic3DCenteredResolvent
open KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics.Relativistic3DFourierHilbertStability
abbrev ResolventTestCoefficients := KomorebiPhysics.Relativistic3DFullFourierEvolution.CoeffL2
abbrev ResolventTestPhysical := KomorebiPhysics.Relativistic3DTorusFourierEvolution.TorusSpinorL2
example (m h : ℝ) (f : ResolventTestCoefficients) : ResolventTestCoefficients :=
  centeredCoeffResolvent m h (0 : ℂ) (by norm_num) f
