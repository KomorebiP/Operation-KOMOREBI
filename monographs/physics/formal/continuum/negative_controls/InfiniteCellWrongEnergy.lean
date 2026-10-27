import KomorebiPhysics.InfiniteCoarseExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (coarse harmonicEigenvalue).atlas.energy (coherentState : Space) 0 = 9/25 := by
  rw [even_probability]
  norm_num
end
