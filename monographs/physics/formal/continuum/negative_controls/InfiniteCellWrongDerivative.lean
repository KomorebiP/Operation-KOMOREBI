import KomorebiPhysics.InfiniteCoarseExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : HasDerivAt (fun t => (coarse harmonicEigenvalue).atlas.energy
    (evolution harmonicEigenvalue t (coherentState : Space)) 0) (-288/625) 0 := by
  apply even_probability_hasDerivAt.congr_deriv
  norm_num
end
