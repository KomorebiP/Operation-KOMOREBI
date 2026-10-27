import KomorebiPhysics.ExtensionExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : deriv (fun u : ℝ => ∑ _i : Fin 2, u) 0 = 0 := by
  rw [(source_total_derivative 0).deriv]
  norm_num
