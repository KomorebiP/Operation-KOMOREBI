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
    centeredCoeffOperator m 0 (centeredCoeffResolvent m 0 Complex.I (by norm_num) f) -
      Complex.I • centeredCoeffResolvent m 0 Complex.I (by norm_num) f = f := by
  exact centered_shift_resolvent m 0 (by norm_num) Complex.I (by norm_num) f
