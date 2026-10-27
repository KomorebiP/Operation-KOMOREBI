import KomorebiPhysics.InfiniteCoarseExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (coarse harmonicEigenvalue).current coherentState 0 1 = 0 := by
  rw [current_even_from_odd]
  norm_num
end
