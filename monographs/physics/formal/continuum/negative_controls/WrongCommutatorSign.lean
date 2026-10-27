import KomorebiPhysics
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : comm N P = comm P N := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [KomorebiPhysics.Deformation.comm, N, P, Matrix.mul_apply, Fin.sum_univ_two]
