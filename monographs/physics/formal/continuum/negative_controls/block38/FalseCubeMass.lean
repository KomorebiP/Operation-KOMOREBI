module
import KomorebiPhysics.Relativistic3DBinaryLebesgue
open MeasureTheory
open KomorebiPhysics.Relativistic3DBinaryLebesgue.Cube
example : cubeVolume Set.univ = 2 := by
  simp [cubeVolume]
