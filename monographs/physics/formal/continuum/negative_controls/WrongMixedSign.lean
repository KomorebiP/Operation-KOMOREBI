import KomorebiPhysics.ExtensionExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : binaryAtlas.current hamiltonian density 0 1 = (1/2:ℝ) := by
  rw [mixed_current_values.1]
  norm_num
