import KomorebiPhysics.Relativistic3DEuclideanDyadicBoxes
open scoped ENNReal NNReal MeasureTheory unitInterval
namespace KomorebiPhysics.Relativistic3DEuclideanDyadicBoxes
example (a : Prev.Prefix 2) (i : Prev.Axis) :
    axisUpperReal 2 a i - axisLowerReal 2 a i = (1 : ℝ) / 2 := by
  rw [axisUpperReal_sub_lowerReal]
  norm_num
end KomorebiPhysics.Relativistic3DEuclideanDyadicBoxes
