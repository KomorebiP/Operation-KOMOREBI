module
import KomorebiPhysics.Relativistic3DBinaryLebesgue
open scoped ENNReal
open KomorebiPhysics.Relativistic3DBinaryLebesgue
open KomorebiPhysics.Relativistic3DBinaryLebesgue.Cube
noncomputable def zeroBits : Axis → Prev.Bit := fun _ => 0
example : bitVectorMeasure ({zeroBits} : Set (Axis → Prev.Bit)) = (4 : ℝ≥0∞)⁻¹ := by
  rw [KomorebiPhysics.Relativistic3DOctreeEuclideanCoding.bitVectorMeasure_singleton]
  norm_num
