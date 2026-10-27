import KomorebiPhysics.Relativistic3DWeightedDyadicReconstruction
open KomorebiPhysics.Relativistic3DWeightedDyadicReconstruction
example : Octree.meshSide 1 ^ 3 = Octree.meshSide 1 := by
  norm_num [Octree.meshSide]
