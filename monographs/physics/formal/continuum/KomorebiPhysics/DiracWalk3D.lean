module

public import KomorebiPhysics.InvolutionExponential4
public import Mathlib.Tactic.Module
public import Mathlib.Tactic.NoncommRing
public import Mathlib.Tactic.Ring

/-!
The literal palindromic four-component walk from Chapter 8.2.
The exponential factors are retained and then reduced to a Clifford closed form.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.DiracWalk3D

open NormedSpace
open scoped Matrix ComplexConjugate BigOperators
open KomorebiPhysics.RelativisticClifford3D
open KomorebiPhysics.InvolutionExponential4

/-- Half mass rotation, equation (8.21). -/
def massHalf (m Δ : ℝ) : Mat4 :=
  exp (((-Complex.I * ((m * Δ / 2 : ℝ) : ℂ))) • beta)

/-- Half `x` shift, equation (8.22). -/
def xHalf (kx Δ : ℝ) : Mat4 :=
  exp (((-Complex.I * ((kx * Δ / 2 : ℝ) : ℂ))) • alphaX)

/-- Half `y` shift, equation (8.23). -/
def yHalf (ky Δ : ℝ) : Mat4 :=
  exp (((-Complex.I * ((ky * Δ / 2 : ℝ) : ℂ))) • alphaY)

/-- Full `z` shift, equation (8.24). -/
def zFull (kz Δ : ℝ) : Mat4 :=
  exp (((-Complex.I * ((kz * Δ : ℝ) : ℂ))) • alphaZ)

/-- Literal palindromic update, equation (8.25). -/
def walk (m kx ky kz Δ : ℝ) : Mat4 :=
  massHalf m Δ *
    (xHalf kx Δ * (yHalf ky Δ * zFull kz Δ * yHalf ky Δ) * xHalf kx Δ) *
    massHalf m Δ

/-- Scalar shell coefficient in equation (8.27). -/
def shell (m kx ky kz Δ : ℝ) : ℝ :=
  Real.cos (m * Δ) * Real.cos (kx * Δ) *
    Real.cos (ky * Δ) * Real.cos (kz * Δ)

/-- Coefficient of `β` in the exact closed walk. -/
def betaCoeff (m kx ky kz Δ : ℝ) : ℝ :=
  Real.sin (m * Δ) * Real.cos (kx * Δ) *
    Real.cos (ky * Δ) * Real.cos (kz * Δ)

/-- Coefficient of `α_x` in the exact closed walk. -/
def xCoeff (kx ky kz Δ : ℝ) : ℝ :=
  Real.sin (kx * Δ) * Real.cos (ky * Δ) * Real.cos (kz * Δ)

/-- Coefficient of `α_y` in the exact closed walk. -/
def yCoeff (ky kz Δ : ℝ) : ℝ :=
  Real.sin (ky * Δ) * Real.cos (kz * Δ)

/-- Coefficient of `α_z` in the exact closed walk. -/
def zCoeff (kz Δ : ℝ) : ℝ := Real.sin (kz * Δ)

/-- Clifford-vector part of the exact update. -/
def vectorPart (m kx ky kz Δ : ℝ) : Mat4 :=
  (betaCoeff m kx ky kz Δ : ℂ) • beta +
    (xCoeff kx ky kz Δ : ℂ) • alphaX +
    (yCoeff ky kz Δ : ℂ) • alphaY +
    (zCoeff kz Δ : ℂ) • alphaZ

/-- Closed Clifford form of the update. -/
def closedWalk (m kx ky kz Δ : ℝ) : Mat4 :=
  (shell m kx ky kz Δ : ℂ) • (1 : Mat4) -
    Complex.I • vectorPart m kx ky kz Δ

/-- The literal mass factor reduces to its trigonometric closed form. -/
theorem massHalf_closed (m Δ : ℝ) :
    massHalf m Δ = closedFactor beta (m * Δ / 2) := by
  rw [massHalf, exp_beta_closed]

/-- The literal spatial factors reduce to their trigonometric closed forms. -/
theorem xHalf_closed (kx Δ : ℝ) :
    xHalf kx Δ = closedFactor alphaX (kx * Δ / 2) := by
  rw [xHalf, exp_alphaX_closed]

theorem yHalf_closed (ky Δ : ℝ) :
    yHalf ky Δ = closedFactor alphaY (ky * Δ / 2) := by
  rw [yHalf, exp_alphaY_closed]

theorem zFull_closed (kz Δ : ℝ) :
    zFull kz Δ = closedFactor alphaZ (kz * Δ) := by
  rw [zFull, exp_alphaZ_closed]

/-- The innermost `y-z-y` palindrome. -/
theorem yzy_closed (ky kz Δ : ℝ) :
    closedFactor alphaY (ky * Δ / 2) * closedFactor alphaZ (kz * Δ) *
        closedFactor alphaY (ky * Δ / 2) =
      ((Real.cos (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) • (1 : Mat4) -
        Complex.I •
          (((Real.sin (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) • alphaY +
            (Real.sin (kz * Δ) : ℂ) • alphaZ) := by
  rw [closedFactor_sandwich_closedFactor alphaY_sq
    alphaY_alphaZ_anticommute]
  rw [show 2 * (ky * Δ / 2) = ky * Δ by ring]
  rw [closedFactor]
  module

/-- The `x-y-z-y-x` palindrome. -/
theorem xyzyx_closed (kx ky kz Δ : ℝ) :
    closedFactor alphaX (kx * Δ / 2) *
        (closedFactor alphaY (ky * Δ / 2) * closedFactor alphaZ (kz * Δ) *
          closedFactor alphaY (ky * Δ / 2)) *
        closedFactor alphaX (kx * Δ / 2) =
      ((Real.cos (kx * Δ) * Real.cos (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) •
          (1 : Mat4) -
        Complex.I •
          (((Real.sin (kx * Δ) * Real.cos (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) •
              alphaX +
            ((Real.sin (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) • alphaY +
            (Real.sin (kz * Δ) : ℂ) • alphaZ) := by
  rw [yzy_closed]
  rw [Matrix.mul_sub, Matrix.sub_mul]
  rw [Matrix.mul_smul, Matrix.smul_mul,
    Matrix.mul_smul, Matrix.smul_mul]
  simp only [Matrix.mul_one]
  have hanti :
      alphaX *
          (((Real.sin (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) • alphaY +
            (Real.sin (kz * Δ) : ℂ) • alphaZ) +
        (((Real.sin (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) • alphaY +
            (Real.sin (kz * Δ) : ℂ) • alphaZ) * alphaX = 0 := by
    rw [Matrix.mul_add, Matrix.add_mul]
    rw [Matrix.mul_smul, Matrix.smul_mul,
      Matrix.mul_smul, Matrix.smul_mul]
    calc
      _ = ((Real.sin (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) •
            (alphaX * alphaY + alphaY * alphaX) +
          (Real.sin (kz * Δ) : ℂ) •
            (alphaX * alphaZ + alphaZ * alphaX) := by module
      _ = 0 := by rw [alphaX_alphaY_anticommute, alphaX_alphaZ_anticommute]; simp
  rw [closedFactor_sq alphaX_sq]
  rw [closedFactor_sandwich_anticommute alphaX_sq hanti]
  rw [show 2 * (kx * Δ / 2) = kx * Δ by ring]
  rw [closedFactor]
  module

/-- Exact closed form of the literal palindromic walk. -/
theorem walk_eq_closedWalk (m kx ky kz Δ : ℝ) :
    walk m kx ky kz Δ = closedWalk m kx ky kz Δ := by
  rw [walk, massHalf_closed, xHalf_closed, yHalf_closed, zFull_closed]
  rw [xyzyx_closed]
  rw [Matrix.mul_sub, Matrix.sub_mul]
  rw [Matrix.mul_smul, Matrix.smul_mul,
    Matrix.mul_smul, Matrix.smul_mul]
  simp only [Matrix.mul_one]
  have hanti :
      beta *
          (((Real.sin (kx * Δ) * Real.cos (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) •
              alphaX +
            ((Real.sin (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) • alphaY +
            (Real.sin (kz * Δ) : ℂ) • alphaZ) +
        (((Real.sin (kx * Δ) * Real.cos (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) •
              alphaX +
            ((Real.sin (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) • alphaY +
            (Real.sin (kz * Δ) : ℂ) • alphaZ) * beta = 0 := by
    rw [Matrix.mul_add, Matrix.add_mul, Matrix.mul_add, Matrix.add_mul]
    rw [Matrix.mul_smul, Matrix.smul_mul,
      Matrix.mul_smul, Matrix.smul_mul,
      Matrix.mul_smul, Matrix.smul_mul]
    have hx : beta * alphaX + alphaX * beta = 0 := by
      simpa [add_comm] using alphaX_beta_anticommute
    have hy : beta * alphaY + alphaY * beta = 0 := by
      simpa [add_comm] using alphaY_beta_anticommute
    have hz : beta * alphaZ + alphaZ * beta = 0 := by
      simpa [add_comm] using alphaZ_beta_anticommute
    calc
      _ = ((Real.sin (kx * Δ) * Real.cos (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) •
            (beta * alphaX + alphaX * beta) +
          ((Real.sin (ky * Δ) * Real.cos (kz * Δ) : ℝ) : ℂ) •
            (beta * alphaY + alphaY * beta) +
          (Real.sin (kz * Δ) : ℂ) •
            (beta * alphaZ + alphaZ * beta) := by module
      _ = 0 := by rw [hx, hy, hz]; simp
  rw [closedFactor_sq beta_sq]
  rw [closedFactor_sandwich_anticommute beta_sq hanti]
  rw [show 2 * (m * Δ / 2) = m * Δ by ring]
  rw [closedFactor]
  rw [closedWalk, vectorPart, shell, betaCoeff, xCoeff, yCoeff, zCoeff]
  module

/-- A matrix is unitary on both sides. -/
def IsUnitary (U : Mat4) : Prop :=
  U.conjTranspose * U = 1 ∧ U * U.conjTranspose = 1

/-- Products of unitary matrices are unitary. -/
theorem isUnitary_mul {U V : Mat4} (hU : IsUnitary U) (hV : IsUnitary V) :
    IsUnitary (U * V) := by
  constructor
  · rw [Matrix.conjTranspose_mul]
    calc
      (V.conjTranspose * U.conjTranspose) * (U * V) =
          V.conjTranspose * (U.conjTranspose * U) * V := by
            simp only [Matrix.mul_assoc]
      _ = V.conjTranspose * V := by rw [hU.1]; simp
      _ = 1 := hV.1
  · rw [Matrix.conjTranspose_mul]
    calc
      (U * V) * (V.conjTranspose * U.conjTranspose) =
          U * (V * V.conjTranspose) * U.conjTranspose := by
            simp only [Matrix.mul_assoc]
      _ = U * U.conjTranspose := by rw [hV.2]; simp
      _ = 1 := hU.2

/-- Each literal factor is unitary. -/
theorem massHalf_unitary (m Δ : ℝ) : IsUnitary (massHalf m Δ) := by
  constructor
  · exact exp_unitary_left beta_hermitian _
  · exact exp_unitary_right beta_hermitian _

theorem xHalf_unitary (kx Δ : ℝ) : IsUnitary (xHalf kx Δ) := by
  constructor
  · exact exp_unitary_left alphaX_hermitian _
  · exact exp_unitary_right alphaX_hermitian _

theorem yHalf_unitary (ky Δ : ℝ) : IsUnitary (yHalf ky Δ) := by
  constructor
  · exact exp_unitary_left alphaY_hermitian _
  · exact exp_unitary_right alphaY_hermitian _

theorem zFull_unitary (kz Δ : ℝ) : IsUnitary (zFull kz Δ) := by
  constructor
  · exact exp_unitary_left alphaZ_hermitian _
  · exact exp_unitary_right alphaZ_hermitian _

/-- Exact unitarity of the full update. -/
theorem walk_unitary (m kx ky kz Δ : ℝ) : IsUnitary (walk m kx ky kz Δ) := by
  have hyzy : IsUnitary (yHalf ky Δ * zFull kz Δ * yHalf ky Δ) :=
    isUnitary_mul (isUnitary_mul (yHalf_unitary ky Δ) (zFull_unitary kz Δ))
      (yHalf_unitary ky Δ)
  have hxyzyx :
      IsUnitary (xHalf kx Δ * (yHalf ky Δ * zFull kz Δ * yHalf ky Δ) * xHalf kx Δ) :=
    isUnitary_mul (isUnitary_mul (xHalf_unitary kx Δ) hyzy) (xHalf_unitary kx Δ)
  rw [walk]
  exact isUnitary_mul (isUnitary_mul (massHalf_unitary m Δ) hxyzyx)
    (massHalf_unitary m Δ)

/-- Equation (8.3) in four components: left-unitarity. -/
theorem walk_unitary_left (m kx ky kz Δ : ℝ) :
    (walk m kx ky kz Δ).conjTranspose * walk m kx ky kz Δ = 1 :=
  (walk_unitary m kx ky kz Δ).1

/-- Right-unitarity of the full update. -/
theorem walk_unitary_right (m kx ky kz Δ : ℝ) :
    walk m kx ky kz Δ * (walk m kx ky kz Δ).conjTranspose = 1 :=
  (walk_unitary m kx ky kz Δ).2

/-- Determinant one for each factor. -/
theorem det_massHalf (m Δ : ℝ) : Matrix.det (massHalf m Δ) = 1 := by
  exact det_exp_beta _

theorem det_xHalf (kx Δ : ℝ) : Matrix.det (xHalf kx Δ) = 1 := by
  exact det_exp_of_clifford alphaX_sq alphaX_beta_anticommute _

theorem det_yHalf (ky Δ : ℝ) : Matrix.det (yHalf ky Δ) = 1 := by
  exact det_exp_of_clifford alphaY_sq alphaY_beta_anticommute _

theorem det_zFull (kz Δ : ℝ) : Matrix.det (zFull kz Δ) = 1 := by
  exact det_exp_of_clifford alphaZ_sq alphaZ_beta_anticommute _

/-- Exact determinant one for the seven-factor walk. -/
theorem det_walk (m kx ky kz Δ : ℝ) : Matrix.det (walk m kx ky kz Δ) = 1 := by
  simp [walk, Matrix.det_mul, det_massHalf, det_xHalf, det_yHalf, det_zFull]

/-- The shell lies in the closed interval `[-1,1]`. -/
theorem abs_shell_le_one (m kx ky kz Δ : ℝ) :
    |shell m kx ky kz Δ| ≤ 1 := by
  rw [shell, abs_mul, abs_mul, abs_mul]
  calc
    |Real.cos (m * Δ)| * |Real.cos (kx * Δ)| *
          |Real.cos (ky * Δ)| * |Real.cos (kz * Δ)|
        ≤ 1 * 1 * 1 * 1 := by
          gcongr <;> exact Real.abs_cos_le_one _
    _ = 1 := by norm_num

/-- Exact trace of the walk. -/
theorem trace_walk (m kx ky kz Δ : ℝ) :
    Matrix.trace (walk m kx ky kz Δ) = (4 * shell m kx ky kz Δ : ℝ) := by
  rw [walk_eq_closedWalk]
  simp [closedWalk, vectorPart, Matrix.trace, Fin.sum_univ_four,
    beta, alphaX, alphaY, alphaZ, shell, betaCoeff, xCoeff, yCoeff, zCoeff]

end KomorebiPhysics.DiracWalk3D
