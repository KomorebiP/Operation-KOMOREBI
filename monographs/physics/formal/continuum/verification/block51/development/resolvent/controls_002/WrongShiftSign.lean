import KomorebiPhysics.Relativistic3DCenteredResolvent
noncomputable section
open Filter
open scoped Topology
open KomorebiPhysics.Relativistic3DCenteredResolvent
open KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics.Relativistic3DFourierHilbertStability
abbrev ResolventTestCoefficients := KomorebiPhysics.Relativistic3DFullFourierEvolution.CoeffL2
abbrev ResolventTestPhysical := KomorebiPhysics.Relativistic3DTorusFourierEvolution.TorusSpinorL2
example (m h : ℝ) (hh : h ≠ 0) (f : ResolventTestCoefficients) :
    centeredCoeffOperator m h (centeredCoeffResolvent m h Complex.I (by norm_num) f) +
      Complex.I • centeredCoeffResolvent m h Complex.I (by norm_num) f = f := by
  exact centered_shift_resolvent m h hh Complex.I (by norm_num) f
