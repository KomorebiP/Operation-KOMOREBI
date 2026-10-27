import KomorebiPhysics.Relativistic3DGeometricEdgeRefinement

open KomorebiPhysics.Relativistic3DGeometricEdgeRefinement

-- Deliberately false: one half-edge translation is not one coarse translation.
example {Site : Type} (τ : Site ≃ Site) (x : Site) :
    halfShift τ (Sum.inl x) = coarseLift τ (Sum.inl x) := by
  simp
