import GeneralDualMatrixNorm
import Mathlib.Algebra.Field.ZMod
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases

/-! Actual unipotent Frobenius: the norm is nonzero although its sole eigenvalue is one. -/
noncomputable section
namespace Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples
open Komorebi.StrongArtin.NonsemisimpleNorm
open GeneralDualMatrix
abbrev k := ZMod 3
abbrev n := Fin 2
abbrev Mat := Matrix n n k
abbrev D := GeneralDualMatrix.D k n

def F : Matˣ where
  val := !![1, 1; 0, 1]
  inv := !![1, -1; 0, 1]
  val_inv := by decide
  inv_val := by decide

def upper : Mat := !![0, 1; 0, 0]
def lower : Mat := !![0, 0; 1, 0]
def diagonalError : Mat := !![1, 0; 0, 0]
abbrev T : Module.End k Mat := conjugationOperator k n F

/-- The actual nilpotent-square image is the upper off-diagonal line. -/
theorem nilpotent_square_apply (X : Mat) :
    ((T - 1 : Module.End k Mat)^2) X = X 1 0 • upper := by
  change (T - 1 : Module.End k Mat) ((T - 1 : Module.End k Mat) X) = _
  simp only [LinearMap.sub_apply, Module.End.one_apply]
  dsimp [T, conjugationOperator, F]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.vecMul, dotProduct, Fin.sum_univ_two, upper, Matrix.mul_apply]
  ring_nf
  simp [show (2 : k) = -1 by decide]

theorem nilpotent_cube_zero : (T - 1)^3 = 0 := by
  apply LinearMap.ext
  intro X
  rw [pow_succ', Module.End.mul_apply, nilpotent_square_apply]
  simp only [LinearMap.sub_apply, Module.End.one_apply]
  dsimp [T, conjugationOperator, F]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [upper]

theorem nilpotent_square_nonzero : (T - 1)^2 ≠ 0 := by
  intro h
  have hx := congrArg (fun L : Module.End k Mat => L lower) h
  rw [nilpotent_square_apply] at hx
  have he := congrArg (fun X : Mat => X 0 1) hx
  norm_num [lower, upper, Matrix.smul_apply] at he

theorem norm_three_apply (X : Mat) : operatorNorm T 3 X = X 1 0 • upper := by
  rw [operatorNorm_prime T 3]
  exact nilpotent_square_apply X

theorem norm_image_iff (e : Mat) :
    e ∈ LinearMap.range (operatorNorm T 3) ↔ ∃ a : k, e = a • upper := by
  constructor
  · rintro ⟨x, rfl⟩
    exact ⟨x 1 0, norm_three_apply x⟩
  · rintro ⟨a, rfl⟩
    refine ⟨a • lower, ?_⟩
    rw [norm_three_apply]
    simp [lower, Matrix.smul_apply]

end Komorebi.StrongArtin.SquareZeroH2.UnipotentNormExamples
