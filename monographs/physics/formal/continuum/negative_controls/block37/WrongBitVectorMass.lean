import KomorebiPhysics.Relativistic3DOctreeEuclideanCoding

open scoped ENNReal
open Set
open KomorebiPhysics.Relativistic3DOctreeEuclideanCoding

example (b : Axis → Bit) : bitVectorMeasure {b} = (4 : ℝ≥0∞)⁻¹ := by
  rw [bitVectorMeasure_singleton]
  norm_num
