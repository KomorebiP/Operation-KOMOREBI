import KomorebiPhysics.Relativistic3DWeightedDyadicReconstruction
open KomorebiPhysics.Relativistic3DWeightedDyadicReconstruction
example : Fintype.card (Octree.Prefix 2) = 8 := by
  norm_num [Octree.Prefix]
