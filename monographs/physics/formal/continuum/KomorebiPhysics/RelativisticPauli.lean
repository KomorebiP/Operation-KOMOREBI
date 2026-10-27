module

public import Mathlib.Analysis.Normed.Algebra.MatrixExponential
public import Mathlib.Analysis.SpecialFunctions.Exponential
public import Mathlib.Analysis.Complex.Trigonometric
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.NormNum

/-!
Exact Pauli algebra for Chapter 8.1 of the full physics edition.
The matrices are the literal two-component generators used by the one-dimensional
relativistic update. No Clifford relation is assumed as an axiom.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.RelativisticPauli

open scoped Matrix ComplexConjugate BigOperators

abbrev Spin := Fin 2
abbrev Mat2 := Matrix Spin Spin ℂ

/-- `α = σ_z` from (8.1). -/
def alpha : Mat2 := !![(1 : ℂ), 0; 0, -1]

/-- `β = σ_x` from (8.1). -/
def beta : Mat2 := !![(0 : ℂ), 1; 1, 0]

/-- The change-of-basis matrix used to diagonalize `β`. -/
def diagonalizer : Mat2 := !![(1 : ℂ), 1; 1, -1]

@[simp] theorem alpha_apply_00 : alpha 0 0 = 1 := by norm_num [alpha]
@[simp] theorem alpha_apply_01 : alpha 0 1 = 0 := by norm_num [alpha]
@[simp] theorem alpha_apply_10 : alpha 1 0 = 0 := by norm_num [alpha]
@[simp] theorem alpha_apply_11 : alpha 1 1 = -1 := by norm_num [alpha]

@[simp] theorem beta_apply_00 : beta 0 0 = 0 := by norm_num [beta]
@[simp] theorem beta_apply_01 : beta 0 1 = 1 := by norm_num [beta]
@[simp] theorem beta_apply_10 : beta 1 0 = 1 := by norm_num [beta]
@[simp] theorem beta_apply_11 : beta 1 1 = 0 := by norm_num [beta]

/-- First Clifford involution in (8.1). -/
theorem alpha_sq : alpha * alpha = (1 : Mat2) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [alpha, Matrix.mul_apply, Fin.sum_univ_two]

/-- Second Clifford involution in (8.1). -/
theorem beta_sq : beta * beta = (1 : Mat2) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [beta, Matrix.mul_apply, Fin.sum_univ_two]

/-- Exact ordered product `αβ`. -/
theorem alpha_mul_beta :
    alpha * beta = !![(0 : ℂ), 1; -1, 0] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [alpha, beta, Matrix.mul_apply, Fin.sum_univ_two]

/-- Exact reverse ordered product `βα`. -/
theorem beta_mul_alpha :
    beta * alpha = !![(0 : ℂ), -1; 1, 0] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [alpha, beta, Matrix.mul_apply, Fin.sum_univ_two]

/-- Anticommutation in (8.1). -/
theorem anticommute : alpha * beta + beta * alpha = 0 := by
  rw [alpha_mul_beta, beta_mul_alpha]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num

/-- Equivalent ordered anticommutation form. -/
theorem alpha_beta_eq_neg_beta_alpha : alpha * beta = -(beta * alpha) := by
  rw [alpha_mul_beta, beta_mul_alpha]
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num

/-- `α` is Hermitian. -/
theorem alpha_hermitian : alpha.conjTranspose = alpha := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [alpha, Matrix.conjTranspose_apply]

/-- `β` is Hermitian. -/
theorem beta_hermitian : beta.conjTranspose = beta := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [beta, Matrix.conjTranspose_apply]

/-- `α` is traceless. -/
theorem trace_alpha : Matrix.trace alpha = 0 := by
  norm_num [alpha, Matrix.trace, Fin.sum_univ_two]

/-- `β` is traceless. -/
theorem trace_beta : Matrix.trace beta = 0 := by
  norm_num [beta, Matrix.trace, Fin.sum_univ_two]

/-- Exact determinant of `α`. -/
theorem det_alpha : Matrix.det alpha = -1 := by
  norm_num [alpha, Matrix.det_fin_two]

/-- Exact determinant of `β`. -/
theorem det_beta : Matrix.det beta = -1 := by
  norm_num [beta, Matrix.det_fin_two]

/-- The diagonalizing matrix has determinant `-2`, hence is invertible. -/
theorem det_diagonalizer : Matrix.det diagonalizer = -2 := by
  norm_num [diagonalizer, Matrix.det_fin_two]

/-- The diagonalizer is a unit of the matrix ring. -/
theorem diagonalizer_isUnit : IsUnit diagonalizer := by
  rw [Matrix.isUnit_iff_isUnit_det]
  norm_num [diagonalizer, Matrix.det_fin_two]

/-- Exact inverse of the unnormalized Hadamard diagonalizer. -/
theorem diagonalizer_inv : diagonalizer⁻¹ = ((1 / 2 : ℂ) • diagonalizer) := by
  apply Matrix.inv_eq_left_inv
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [diagonalizer, Matrix.mul_apply, Fin.sum_univ_two]

/-- `β` is conjugate to `α`; this is used to transport the matrix exponential. -/
theorem beta_conj_alpha : beta = diagonalizer * alpha * diagonalizer⁻¹ := by
  rw [diagonalizer_inv]
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [diagonalizer, alpha, beta, Matrix.mul_apply, Fin.sum_univ_two]

/-- `α` and `β` are genuinely distinct. -/
theorem alpha_ne_beta : alpha ≠ beta := by
  intro h
  have := congrArg (fun M : Mat2 => M 0 0) h
  norm_num [alpha, beta] at this

end KomorebiPhysics.RelativisticPauli
