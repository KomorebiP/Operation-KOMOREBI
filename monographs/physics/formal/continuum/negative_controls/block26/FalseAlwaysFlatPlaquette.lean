import KomorebiPhysics.Relativistic3DGeometricEdgeRefinement

open KomorebiPhysics.Relativistic3DGeometricEdgeRefinement

-- Deliberately false: the checked Boolean witness has holonomy -1, not 1.
example :
    plaquette boolSwap (Equiv.refl Bool) (fun _ => 1) alternatingBoolLink false = 1 := by
  simp
