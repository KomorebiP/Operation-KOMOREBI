module
import KomorebiPhysics.Relativistic3DBinaryLebesgue
open KomorebiPhysics.Relativistic3DBinaryLebesgue
example : binaryCDF ((1 : ℝ) / 2) = (1 : ℝ) / 4 := by
  rw [binaryCDF_eq ((1 : ℝ) / 2) (by norm_num) (by norm_num)]
  norm_num
