import KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.HarmonicSurrogates
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.UnboundedExamples
open scoped Topology lp
noncomputable section
example : ‖evolution harmonicEigenvalue (halfTurnTime 100) -
    ContinuousLinearMap.id ℂ Space‖ = 0 := by
  rw [halfTurn_operator_distance]
end
