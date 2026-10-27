import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Data.ZMod.Basic
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic

namespace KomorebiBeal.Block47

open Polynomial

/-- The sextic reduced modulo seven. Its geometric interpretation is external. -/
noncomputable def freySexticModSeven (a b : ZMod 7) : Polynomial (ZMod 7) :=
  X ^ 6 + C (10 * b) * X ^ 3 + C (12 * a) * X + C (5 * b ^ 2)

theorem frey_cube_expansion (a b : ZMod 7) :
    freySexticModSeven a b ^ 3 =
      X ^ 18 + C (30 * b) * X ^ 15 + C (36 * a) * X ^ 13 +
      C (315 * b ^ 2) * X ^ 12 + C (720 * a * b) * X ^ 10 +
      C (1300 * b ^ 3) * X ^ 9 + C (432 * a ^ 2) * X ^ 8 +
      C (3960 * a * b ^ 2) * X ^ 7 + C (1575 * b ^ 4) * X ^ 6 +
      C (4320 * a ^ 2 * b) * X ^ 5 + C (3600 * a * b ^ 3) * X ^ 4 +
      C (1728 * a ^ 3 + 750 * b ^ 5) * X ^ 3 +
      C (2160 * a ^ 2 * b ^ 2) * X ^ 2 + C (900 * a * b ^ 4) * X +
      C (125 * b ^ 6) := by
  simp only [freySexticModSeven, map_mul, map_add, map_pow, map_ofNat]
  ring

theorem frey_cube_coeff_six (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 6 = 0 := by
  rw [frey_cube_expansion]
  simp only [coeff_add, coeff_C_mul_X_pow, coeff_C_mul_X, coeff_X_pow, coeff_C]
  norm_num
  rw [show (1575 : ZMod 7) = 0 from by decide]
  simp only [zero_mul]

theorem frey_cube_coeff_five (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 5 = a ^ 2 * b := by
  rw [frey_cube_expansion]
  simp only [coeff_add, coeff_C_mul_X_pow, coeff_C_mul_X, coeff_X_pow, coeff_C]
  norm_num
  rw [show (4320 : ZMod 7) = 1 from by decide]
  simp only [one_mul]

theorem frey_cube_coeff_thirteen (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 13 = a := by
  rw [frey_cube_expansion]
  simp only [coeff_add, coeff_C_mul_X_pow, coeff_C_mul_X, coeff_X_pow, coeff_C]
  norm_num
  rw [show (36 : ZMod 7) = 1 from by decide]
  simp only [one_mul]

theorem frey_cube_coeff_twelve (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 12 = 0 := by
  rw [frey_cube_expansion]
  simp only [coeff_add, coeff_C_mul_X_pow, coeff_C_mul_X, coeff_X_pow, coeff_C]
  norm_num
  rw [show (315 : ZMod 7) = 0 from by decide]
  simp only [zero_mul]

/-- The determinant expression extracted from the four polynomial coefficients. -/
theorem frey_coeff_determinant (a b : ZMod 7) :
    ((freySexticModSeven a b) ^ 3).coeff 6 *
        ((freySexticModSeven a b) ^ 3).coeff 12 -
      ((freySexticModSeven a b) ^ 3).coeff 5 *
        ((freySexticModSeven a b) ^ 3).coeff 13 = -(a ^ 3 * b) := by
  rw [frey_cube_coeff_six, frey_cube_coeff_twelve,
    frey_cube_coeff_five, frey_cube_coeff_thirteen]
  ring

/-- Matrix assembled from the four coefficient positions. Identifying this
matrix with a geometric Cartier operator is not part of this formalization. -/
noncomputable def coefficientMatrix (a b : ZMod 7) :
    Matrix (Fin 2) (Fin 2) (ZMod 7) :=
  !![((freySexticModSeven a b) ^ 3).coeff 6,
      ((freySexticModSeven a b) ^ 3).coeff 5;
     ((freySexticModSeven a b) ^ 3).coeff 13,
      ((freySexticModSeven a b) ^ 3).coeff 12]

theorem coefficientMatrix_eq (a b : ZMod 7) :
    coefficientMatrix a b = !![0, a ^ 2 * b; a, 0] := by
  simp only [coefficientMatrix, frey_cube_coeff_six, frey_cube_coeff_five,
    frey_cube_coeff_thirteen, frey_cube_coeff_twelve]

theorem coefficientMatrix_det (a b : ZMod 7) :
    (coefficientMatrix a b).det = -(a ^ 3 * b) := by
  rw [coefficientMatrix_eq, Matrix.det_fin_two_of]
  ring

theorem coefficientMatrix_square (a b : ZMod 7) :
    coefficientMatrix a b * coefficientMatrix a b =
      (a ^ 3 * b) • (1 : Matrix (Fin 2) (Fin 2) (ZMod 7)) := by
  rw [coefficientMatrix_eq]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [Matrix.mul_apply, Fin.sum_univ_two] <;> ring

end KomorebiBeal.Block47
