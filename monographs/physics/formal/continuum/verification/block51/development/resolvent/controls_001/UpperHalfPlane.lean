import KomorebiPhysics.Relativistic3DCenteredResolvent
noncomputable section
open Filter
open scoped Topology
open KomorebiPhysics.Relativistic3DCenteredResolvent
open KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics.Relativistic3DFourierHilbertStability
abbrev CoeffL2 := KomorebiPhysics.Relativistic3DFullFourierEvolution.CoeffL2
abbrev TorusSpinorL2 := KomorebiPhysics.Relativistic3DTorusFourierEvolution.TorusSpinorL2
example (m : ℝ) (f : CoeffL2) :
    Tendsto (fun h => centeredCoeffResolvent m h Complex.I (by norm_num) f)
      (𝓝[≠] 0) (𝓝 (continuumCoeffResolvent m Complex.I (by norm_num) f)) :=
  centered_resolvent_tendsto m Complex.I (by norm_num) f

example (m h : ℝ) (hh : h ≠ 0) (f : CoeffL2) :
    centeredCoeffOperator m h (centeredCoeffResolvent m h Complex.I (by norm_num) f) -
      Complex.I • centeredCoeffResolvent m h Complex.I (by norm_num) f = f :=
  centered_shift_resolvent m h hh Complex.I (by norm_num) f
