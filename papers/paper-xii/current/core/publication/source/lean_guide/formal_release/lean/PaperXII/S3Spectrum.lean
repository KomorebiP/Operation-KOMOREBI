import PaperXII.S3Standard
import Mathlib.LinearAlgebra.Matrix.Charpoly.Coeff
import Mathlib.Algebra.Polynomial.Splits

/-! The coefficient field contains every eigenvalue of the actual standard S3
representation. The factorizations cover all six permutations. -/
set_option autoImplicit false
namespace PaperXII.S3Spectrum

open Matrix Polynomial S3Standard

abbrev K := ZMod 7

/-- Expand the two spectral factors without moving field arithmetic into polynomials. -/
theorem spectral_factors (a b : K) :
    (X - C a) * (X - C b) = X ^ 2 - C (a + b) * X + C (a * b) := by
  simp only [map_add, map_mul]
  ring

/-- The identity has the two expected unit eigenvalues. -/
theorem identity_charpoly : (matrixRep K (1 : Group)).charpoly = (X - 1) ^ 2 := by
  rw [map_one, Matrix.charpoly_one]
  rfl

/-- The displayed transposition has eigenvalues 1 and -1. -/
theorem transposition_charpoly :
    (matrixRep K transposition).charpoly = (X - C 1) * (X - C 6) := by
  rw [matrixRep_transposition, Matrix.charpoly_fin_two]
  rw [spectral_factors]
  rw [show (1 + 6 : K) = 0 by decide, show (1 * 6 : K) = -1 by decide]
  norm_num [Matrix.trace, Matrix.diag, Matrix.det_fin_two,
    Matrix.mul_apply, Fin.sum_univ_succ, pow_two]

/-- The displayed three-cycle splits already over F7. -/
theorem cycle_charpoly :
    (matrixRep K cycle).charpoly = (X - C 2) * (X - C 4) := by
  rw [matrixRep_cycle, Matrix.charpoly_fin_two]
  rw [spectral_factors]
  rw [show (2 + 4 : K) = -1 by decide, show (2 * 4 : K) = 1 by decide]
  norm_num [Matrix.trace, Matrix.diag, Matrix.det_fin_two,
    Matrix.mul_apply, Fin.sum_univ_succ, pow_two]

/-- The inverse three-cycle has the same two eigenvalues. -/
theorem cycle_square_charpoly :
    (matrixRep K (cycle ^ 2)).charpoly = (X - C 2) * (X - C 4) := by
  rw [map_pow, matrixRep_cycle, Matrix.charpoly_fin_two]
  rw [spectral_factors]
  rw [show (2 + 4 : K) = -1 by decide, show (2 * 4 : K) = 1 by decide]
  norm_num [Matrix.trace, Matrix.diag, Matrix.det_fin_two,
    Matrix.mul_apply, Fin.sum_univ_succ, pow_two]

/-- The second transposition has eigenvalues 1 and -1. -/
theorem transposition_cycle_charpoly :
    (matrixRep K (transposition * cycle)).charpoly = (X - C 1) * (X - C 6) := by
  rw [map_mul, matrixRep_transposition, matrixRep_cycle, Matrix.charpoly_fin_two]
  rw [spectral_factors]
  rw [show (1 + 6 : K) = 0 by decide, show (1 * 6 : K) = -1 by decide]
  norm_num [Matrix.trace, Matrix.diag, Matrix.det_fin_two,
    Matrix.mul_apply, Fin.sum_univ_succ, pow_two]

/-- The third transposition has eigenvalues 1 and -1. -/
theorem transposition_cycle_square_charpoly :
    (matrixRep K (transposition * cycle ^ 2)).charpoly = (X - C 1) * (X - C 6) := by
  rw [map_mul, map_pow, matrixRep_transposition, matrixRep_cycle, Matrix.charpoly_fin_two]
  rw [spectral_factors]
  rw [show (1 + 6 : K) = 0 by decide, show (1 * 6 : K) = -1 by decide]
  norm_num [Matrix.trace, Matrix.diag, Matrix.det_fin_two,
    Matrix.mul_apply, Fin.sum_univ_succ, pow_two]

/-- Every group element's characteristic polynomial splits over the actual coefficient field. -/
theorem all_charpolys_split (g : Group) : (matrixRep K g).charpoly.Splits := by
  rcases group_cases g with rfl | rfl | rfl | rfl | rfl | rfl
  · rw [identity_charpoly]
    exact (Polynomial.Splits.X_sub_C (1 : K)).pow 2
  · rw [transposition_charpoly]
    exact (Polynomial.Splits.X_sub_C 1).mul (Polynomial.Splits.X_sub_C 6)
  · rw [cycle_charpoly]
    exact (Polynomial.Splits.X_sub_C 2).mul (Polynomial.Splits.X_sub_C 4)
  · rw [cycle_square_charpoly]
    exact (Polynomial.Splits.X_sub_C 2).mul (Polynomial.Splits.X_sub_C 4)
  · rw [transposition_cycle_charpoly]
    exact (Polynomial.Splits.X_sub_C 1).mul (Polynomial.Splits.X_sub_C 6)
  · rw [transposition_cycle_square_charpoly]
    exact (Polynomial.Splits.X_sub_C 1).mul (Polynomial.Splits.X_sub_C 6)

end PaperXII.S3Spectrum
