import KomorebiPhysics.Relativistic3DEuclideanDyadicBoxes
open scoped ENNReal NNReal MeasureTheory unitInterval
open MeasureTheory
namespace KomorebiPhysics.Relativistic3DEuclideanDyadicBoxes
example (a : Prev.Prefix 2) :
    Prev.cubeVolume (dyadicBox 2 a) = (8 : ℝ≥0∞)⁻¹ := by
  rw [cubeVolume_dyadicBox]
  norm_num
end KomorebiPhysics.Relativistic3DEuclideanDyadicBoxes
