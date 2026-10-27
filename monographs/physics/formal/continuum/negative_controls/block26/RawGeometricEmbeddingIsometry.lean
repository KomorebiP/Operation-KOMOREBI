import KomorebiPhysics.Relativistic3DGeometricEdgeRefinement

open KomorebiPhysics.Relativistic3DCliffordTransportU1
open KomorebiPhysics.Relativistic3DCliffordHilbertRefinement
open KomorebiPhysics.Relativistic3DGeometricEdgeRefinement

-- Deliberately false without the half-cell measure: raw interpolation doubles weight.
example {Site : Type} [Fintype Site]
    {u : Link (Site := Site)} (S : EdgeSubdivision u)
    (ψ φ : State (Site := Site)) :
    stateIP (S.embed ψ) (S.embed φ) = stateIP ψ φ := by
  rw [embed_stateIP]
