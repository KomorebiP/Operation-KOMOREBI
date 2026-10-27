import KomorebiPhysics.ExtensionExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : binaryAtlas.amplitude hamiltonian density 1 0 =
    binaryAtlas.amplitude hamiltonian density 0 1 := by
  apply Complex.ext
  · norm_num [MatrixAtlas.amplitude, binaryAtlas, hamiltonian, density,
      Matrix.trace, Matrix.diag, Matrix.mul_apply, Fin.sum_univ_two,
      Complex.mul_re, Complex.mul_im]
  · norm_num [MatrixAtlas.amplitude, binaryAtlas, hamiltonian, density,
      Matrix.trace, Matrix.diag, Matrix.mul_apply, Fin.sum_univ_two,
      Complex.mul_re, Complex.mul_im]
