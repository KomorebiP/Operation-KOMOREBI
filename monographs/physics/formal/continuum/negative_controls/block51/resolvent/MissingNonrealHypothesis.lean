import KomorebiPhysics.Relativistic3DCenteredResolvent
noncomputable section
open Filter
open scoped Topology
open KomorebiPhysics.Relativistic3DCenteredResolvent
open KomorebiPhysics.Relativistic3DCenteredConvergence
open KomorebiPhysics.Relativistic3DFourierHilbertStability
abbrev ResolventTestCoefficients := KomorebiPhysics.Relativistic3DFullFourierEvolution.CoeffL2
abbrev ResolventTestPhysical := KomorebiPhysics.Relativistic3DTorusFourierEvolution.TorusSpinorL2
example (A : HilbertSpinorEnd) (hA : IsSelfAdjoint A) (z : ℂ) :
    IsUnit (A - z • (1 : HilbertSpinorEnd)) := by
  exact shifted_isUnit A hA z (by assumption)
