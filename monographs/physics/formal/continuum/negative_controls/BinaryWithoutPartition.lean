import KomorebiPhysics.ExtensionExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : (overlap * overlap) 0 0 = 0 ∨ (overlap * overlap) 0 0 = 1 := by
  norm_num [overlap, Matrix.mul_apply, Fin.sum_univ_two]
