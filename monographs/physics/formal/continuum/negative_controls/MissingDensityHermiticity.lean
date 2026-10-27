import KomorebiPhysics.ExtensionExamples

open KomorebiPhysics KomorebiPhysics.MixedTransfer
open KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder

-- Deliberately invalid: this file MUST fail, independently of import failures.
example : binaryAtlas.current hamiltonian badDensity 0 1 =
    -binaryAtlas.current hamiltonian badDensity 1 0 := by
  norm_num [MatrixAtlas.current, MatrixAtlas.amplitude, binaryAtlas, hamiltonian,
    density, badDensity, badHamiltonian, Matrix.trace, Matrix.diag,
    Matrix.mul_apply, Fin.sum_univ_two, Complex.mul_re, Complex.mul_im]
