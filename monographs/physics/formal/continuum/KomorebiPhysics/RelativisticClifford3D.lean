module

public import Mathlib.Analysis.Normed.Algebra.MatrixExponential
public import Mathlib.Analysis.Complex.Trigonometric
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.NoncommRing

/-!
Explicit four-component Clifford generators for Chapter 8.2.
The matrices are constructed entrywise; no Clifford relation is assumed.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.RelativisticClifford3D

open scoped Matrix ComplexConjugate BigOperators

abbrev Spin4 := Fin 4
abbrev Mat4 := Matrix Spin4 Spin4 ℂ
abbrev Axis3 := Fin 3

/-- Standard Dirac `β = σ_z ⊗ I₂`. -/
def beta : Mat4 :=
  !![(1 : ℂ), 0, 0, 0;
     0, 1, 0, 0;
     0, 0, -1, 0;
     0, 0, 0, -1]

/-- `α_x = σ_x ⊗ σ_x`. -/
def alphaX : Mat4 :=
  !![(0 : ℂ), 0, 0, 1;
     0, 0, 1, 0;
     0, 1, 0, 0;
     1, 0, 0, 0]

/-- `α_y = σ_x ⊗ σ_y`. -/
def alphaY : Mat4 :=
  !![(0 : ℂ), 0, 0, -Complex.I;
     0, 0, Complex.I, 0;
     0, -Complex.I, 0, 0;
     Complex.I, 0, 0, 0]

/-- `α_z = σ_x ⊗ σ_z`. -/
def alphaZ : Mat4 :=
  !![(0 : ℂ), 0, 1, 0;
     0, 0, 0, -1;
     1, 0, 0, 0;
     0, -1, 0, 0]

/-- Indexed spatial Clifford generator. -/
def alpha : Axis3 → Mat4
  | 0 => alphaX
  | 1 => alphaY
  | 2 => alphaZ

/-- `β² = I₄`, equation (8.20). -/
theorem beta_sq : beta * beta = (1 : Mat4) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [beta, Matrix.mul_apply, Fin.sum_univ_four]

/-- `α_x² = I₄`. -/
theorem alphaX_sq : alphaX * alphaX = (1 : Mat4) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaX, Matrix.mul_apply, Fin.sum_univ_four]

/-- `α_y² = I₄`. -/
theorem alphaY_sq : alphaY * alphaY = (1 : Mat4) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaY, Matrix.mul_apply, Fin.sum_univ_four, Complex.I_mul_I]

/-- `α_z² = I₄`. -/
theorem alphaZ_sq : alphaZ * alphaZ = (1 : Mat4) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaZ, Matrix.mul_apply, Fin.sum_univ_four]

/-- Every indexed spatial generator is an involution. -/
theorem alpha_sq (i : Axis3) : alpha i * alpha i = (1 : Mat4) := by
  fin_cases i <;> simp [alpha, alphaX_sq, alphaY_sq, alphaZ_sq]

/-- `α_x α_y + α_y α_x = 0`. -/
theorem alphaX_alphaY_anticommute : alphaX * alphaY + alphaY * alphaX = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaX, alphaY]

/-- `α_x α_z + α_z α_x = 0`. -/
theorem alphaX_alphaZ_anticommute : alphaX * alphaZ + alphaZ * alphaX = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaX, alphaZ]

/-- `α_y α_z + α_z α_y = 0`. -/
theorem alphaY_alphaZ_anticommute : alphaY * alphaZ + alphaZ * alphaY = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaY, alphaZ]

/-- `α_x β + β α_x = 0`. -/
theorem alphaX_beta_anticommute : alphaX * beta + beta * alphaX = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaX, beta]

/-- `α_y β + β α_y = 0`. -/
theorem alphaY_beta_anticommute : alphaY * beta + beta * alphaY = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaY, beta]

/-- `α_z β + β α_z = 0`. -/
theorem alphaZ_beta_anticommute : alphaZ * beta + beta * alphaZ = 0 := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alphaZ, beta]

/-- Indexed form of equation (8.19). -/
theorem alpha_beta_anticommute (i : Axis3) : alpha i * beta + beta * alpha i = 0 := by
  fin_cases i <;> simp [alpha, alphaX_beta_anticommute,
    alphaY_beta_anticommute, alphaZ_beta_anticommute]

/-- Full indexed Clifford relation (8.18). -/
theorem alpha_clifford (i j : Axis3) :
    alpha i * alpha j + alpha j * alpha i =
      if i = j then (2 : ℂ) • (1 : Mat4) else 0 := by
  by_cases h : i = j
  · subst j
    simp [alpha_sq, two_smul]
  · fin_cases i <;> fin_cases j <;>
      simp_all [alpha, alphaX_alphaY_anticommute,
        alphaX_alphaZ_anticommute, alphaY_alphaZ_anticommute, add_comm]

/-- `β` is Hermitian. -/
theorem beta_hermitian : beta.conjTranspose = beta := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [beta, Matrix.conjTranspose_apply]

/-- `α_x` is Hermitian. -/
theorem alphaX_hermitian : alphaX.conjTranspose = alphaX := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [alphaX, Matrix.conjTranspose_apply]

/-- `α_y` is Hermitian. -/
theorem alphaY_hermitian : alphaY.conjTranspose = alphaY := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [alphaY, Matrix.conjTranspose_apply]

/-- `α_z` is Hermitian. -/
theorem alphaZ_hermitian : alphaZ.conjTranspose = alphaZ := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [alphaZ, Matrix.conjTranspose_apply]

/-- Every indexed spatial generator is Hermitian. -/
theorem alpha_hermitian (i : Axis3) : (alpha i).conjTranspose = alpha i := by
  fin_cases i <;> simp [alpha, alphaX_hermitian, alphaY_hermitian, alphaZ_hermitian]

/-- `β` is traceless. -/
theorem trace_beta : Matrix.trace beta = 0 := by
  simp [beta, Matrix.trace, Fin.sum_univ_four]

/-- `α_x` is traceless. -/
theorem trace_alphaX : Matrix.trace alphaX = 0 := by
  simp [alphaX, Matrix.trace, Fin.sum_univ_four]

/-- `α_y` is traceless. -/
theorem trace_alphaY : Matrix.trace alphaY = 0 := by
  simp [alphaY, Matrix.trace, Fin.sum_univ_four]

/-- `α_z` is traceless. -/
theorem trace_alphaZ : Matrix.trace alphaZ = 0 := by
  simp [alphaZ, Matrix.trace, Fin.sum_univ_four]

/-- Every indexed spatial generator is traceless. -/
theorem trace_alpha (i : Axis3) : Matrix.trace (alpha i) = 0 := by
  fin_cases i <;> simp [alpha, trace_alphaX, trace_alphaY, trace_alphaZ]

/-- The four generators are pairwise distinct. -/
theorem alphaX_ne_alphaY : alphaX ≠ alphaY := by
  intro h
  have h' := congrArg (fun A : Mat4 => A 0 3) h
  change (1 : ℂ) = -Complex.I at h'
  have hr := congrArg Complex.re h'
  norm_num at hr

theorem alphaX_ne_alphaZ : alphaX ≠ alphaZ := by
  intro h
  have h' := congrArg (fun A : Mat4 => A 0 2) h
  change (0 : ℂ) = 1 at h'
  norm_num at h'

theorem beta_ne_alphaX : beta ≠ alphaX := by
  intro h
  have h' := congrArg (fun A : Mat4 => A 0 0) h
  norm_num [beta, alphaX] at h'

end KomorebiPhysics.RelativisticClifford3D
