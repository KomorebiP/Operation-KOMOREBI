import KomorebiPhysics.InfiniteCoarseExamples
open KomorebiPhysics KomorebiPhysics.BoundedSpectral KomorebiPhysics.UnboundedExamples
open KomorebiPhysics.SpectralEvolution KomorebiPhysics.SpectralEvolutionExamples
open KomorebiPhysics.InfiniteCoarseExamples
open scoped BigOperators Topology lp
noncomputable section
example : (parity ⁻¹' {(0 : Fin 2)}).Finite := by
  have hn : ¬ (parity ⁻¹' {(0 : Fin 2)}).Finite := even_fiber_infinite
  simp only [hn]
end
