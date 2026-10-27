import KomorebiPhysics
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : (3 : ℝ) • N = comm N P * X * Q + P * X * comm N Q := by
  rw [exact_three_terms.2.1, exact_three_terms.2.2]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [N]
