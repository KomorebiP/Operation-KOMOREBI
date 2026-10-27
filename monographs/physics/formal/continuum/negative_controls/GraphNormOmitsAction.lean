import KomorebiPhysics.UnboundedExamples
open scoped lp
open KomorebiPhysics KomorebiPhysics.UnboundedExamples
example : GraphDomain.graphNorm harmonic (basisState 0) =
    ‖(basisState 0 : ℓ²(ℕ, ℂ))‖ := by
  simp only [graph_norm_not_ambient]
