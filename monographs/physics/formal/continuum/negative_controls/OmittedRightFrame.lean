import KomorebiPhysics
open KomorebiPhysics.DeformationExamples
open KomorebiPhysics.Deformation
open scoped Matrix

example : (3 : ℝ) • N = P * dX * Q + comm N P * X * Q := by
  rw [exact_three_terms.1, exact_three_terms.2.1]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [N]
