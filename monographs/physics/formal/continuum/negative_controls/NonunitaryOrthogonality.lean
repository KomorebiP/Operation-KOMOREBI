import KomorebiPhysics
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : (transport (shear 1) (inverseShear 1) P).transpose =
    transport (shear 1) (inverseShear 1) P := by
  rw [transported_projector]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [P, N, Matrix.transpose_apply]
