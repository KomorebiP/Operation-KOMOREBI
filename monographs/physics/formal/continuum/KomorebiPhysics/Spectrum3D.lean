module

public import KomorebiPhysics.Dispersion3D
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.Ring

/-!
Exact characteristic polynomial and doubled principal-phase roots of the 3D walk.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Spectrum3D

open scoped Matrix ComplexConjugate BigOperators
open KomorebiPhysics.RelativisticClifford3D
open KomorebiPhysics.DiracWalk3D
open KomorebiPhysics.Dispersion3D

/-- Linear Clifford pencil used to compute the four-by-four determinant. -/
def cliffordPencil (x a b c d : ℂ) : Mat4 :=
  x • (1 : Mat4) + Complex.I •
    (a • beta + b • alphaX + c • alphaY + d • alphaZ)

/-- Explicit coordinate form of the Clifford pencil. -/
theorem cliffordPencil_explicit (x a b c d : ℂ) :
    cliffordPencil x a b c d =
      !![x + Complex.I * a, 0, Complex.I * d, c + Complex.I * b;
         0, x + Complex.I * a, -c + Complex.I * b, -Complex.I * d;
         Complex.I * d, c + Complex.I * b, x - Complex.I * a, 0;
         -c + Complex.I * b, -Complex.I * d, 0, x - Complex.I * a] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [cliffordPencil, beta, alphaX, alphaY, alphaZ]
  all_goals ring_nf
  all_goals simp [sub_eq_add_neg]

set_option maxHeartbeats 1000000

/-- Determinant of the generic Clifford pencil. -/
theorem det_cliffordPencil (x a b c d : ℂ) :
    Matrix.det (cliffordPencil x a b c d) =
      (x ^ 2 + a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2) ^ 2 := by
  rw [cliffordPencil_explicit]
  rw [Matrix.det_succ_row_zero, Fin.sum_univ_four]
  norm_num
  simp only [Matrix.det_fin_three, Matrix.submatrix_apply]
  simp [Fin.succAbove]
  ring_nf
  simp
  ring

/-- The characteristic pencil is the generic Clifford pencil. -/
theorem characteristic_pencil (z : ℂ) (m kx ky kz Δ : ℝ) :
    z • (1 : Mat4) - walk m kx ky kz Δ =
      cliffordPencil
        (z - (shell m kx ky kz Δ : ℂ))
        (betaCoeff m kx ky kz Δ : ℂ)
        (xCoeff kx ky kz Δ : ℂ)
        (yCoeff ky kz Δ : ℂ)
        (zCoeff kz Δ : ℂ) := by
  rw [walk_eq_closedWalk]
  rw [closedWalk, vectorPart, cliffordPencil]
  module

/-- Exact squared quadratic characteristic polynomial, equation (8.28). -/
theorem characteristic_polynomial (z : ℂ) (m kx ky kz Δ : ℝ) :
    Matrix.det (z • (1 : Mat4) - walk m kx ky kz Δ) =
      (z ^ 2 - 2 * (shell m kx ky kz Δ : ℂ) * z + 1) ^ 2 := by
  rw [characteristic_pencil, det_cliffordPencil]
  have hnorm := coefficient_norm_complex m kx ky kz Δ
  have hinside :
      (z - (shell m kx ky kz Δ : ℂ)) ^ 2 +
          (betaCoeff m kx ky kz Δ : ℂ) ^ 2 +
          (xCoeff kx ky kz Δ : ℂ) ^ 2 +
          (yCoeff ky kz Δ : ℂ) ^ 2 +
          (zCoeff kz Δ : ℂ) ^ 2 =
        z ^ 2 - 2 * (shell m kx ky kz Δ : ℂ) * z + 1 := by
    calc
      _ = (z - (shell m kx ky kz Δ : ℂ)) ^ 2 +
          ((betaCoeff m kx ky kz Δ : ℂ) ^ 2 +
           (xCoeff kx ky kz Δ : ℂ) ^ 2 +
           (yCoeff ky kz Δ : ℂ) ^ 2 +
           (zCoeff kz Δ : ℂ) ^ 2) := by ring
      _ = (z - (shell m kx ky kz Δ : ℂ)) ^ 2 +
          (1 - (shell m kx ky kz Δ : ℂ) ^ 2) := by rw [hnorm]
      _ = z ^ 2 - 2 * (shell m kx ky kz Δ : ℂ) * z + 1 := by ring
  rw [hinside]

/-- Negative principal-phase root. -/
def rootMinus (m kx ky kz Δ : ℝ) : ℂ :=
  Complex.exp (-Complex.I * (phase m kx ky kz Δ : ℂ))

/-- Positive principal-phase root. -/
def rootPlus (m kx ky kz Δ : ℝ) : ℂ :=
  Complex.exp (Complex.I * (phase m kx ky kz Δ : ℂ))

/-- Closed Euler form of the negative root. -/
theorem rootMinus_closed (m kx ky kz Δ : ℝ) :
    rootMinus m kx ky kz Δ =
      (Real.cos (phase m kx ky kz Δ) : ℂ) -
        Complex.I * (Real.sin (phase m kx ky kz Δ) : ℂ) := by
  rw [rootMinus]
  exact KomorebiPhysics.InvolutionExponential.complex_exp_neg_I _

/-- Closed Euler form of the positive root. -/
theorem rootPlus_closed (m kx ky kz Δ : ℝ) :
    rootPlus m kx ky kz Δ =
      (Real.cos (phase m kx ky kz Δ) : ℂ) +
        Complex.I * (Real.sin (phase m kx ky kz Δ) : ℂ) := by
  rw [rootPlus]
  exact KomorebiPhysics.InvolutionExponential.complex_exp_pos_I _

/-- The principal roots multiply to one. -/
theorem rootMinus_mul_rootPlus (m kx ky kz Δ : ℝ) :
    rootMinus m kx ky kz Δ * rootPlus m kx ky kz Δ = 1 := by
  rw [rootMinus_closed, rootPlus_closed]
  have htrig :
      ((Real.cos (phase m kx ky kz Δ) : ℂ) ^ 2 +
        (Real.sin (phase m kx ky kz Δ) : ℂ) ^ 2) = 1 := by
    exact_mod_cast Real.cos_sq_add_sin_sq (phase m kx ky kz Δ)
  calc
    _ = (Real.cos (phase m kx ky kz Δ) : ℂ) ^ 2 +
        (Real.sin (phase m kx ky kz Δ) : ℂ) ^ 2 := by
      ring_nf
      simp
    _ = 1 := htrig

/-- The two roots sum to twice the shell coefficient. -/
theorem rootMinus_add_rootPlus (m kx ky kz Δ : ℝ) :
    rootMinus m kx ky kz Δ + rootPlus m kx ky kz Δ =
      2 * (shell m kx ky kz Δ : ℂ) := by
  rw [rootMinus_closed, rootPlus_closed]
  rw [cos_phase]
  ring

/-- Factorization of the exact quadratic shell. -/
theorem quadratic_factorization (z : ℂ) (m kx ky kz Δ : ℝ) :
    z ^ 2 - 2 * (shell m kx ky kz Δ : ℂ) * z + 1 =
      (z - rootMinus m kx ky kz Δ) *
        (z - rootPlus m kx ky kz Δ) := by
  have hsum := rootMinus_add_rootPlus m kx ky kz Δ
  have hprod := rootMinus_mul_rootPlus m kx ky kz Δ
  calc
    z ^ 2 - 2 * (shell m kx ky kz Δ : ℂ) * z + 1 =
        z ^ 2 -
          (rootMinus m kx ky kz Δ + rootPlus m kx ky kz Δ) * z +
          rootMinus m kx ky kz Δ * rootPlus m kx ky kz Δ := by
      rw [hsum, hprod]
    _ = (z - rootMinus m kx ky kz Δ) *
        (z - rootPlus m kx ky kz Δ) := by ring

/-- Characteristic polynomial factored into two doubled phase roots. -/
theorem characteristic_double_factorization (z : ℂ) (m kx ky kz Δ : ℝ) :
    Matrix.det (z • (1 : Mat4) - walk m kx ky kz Δ) =
      (z - rootMinus m kx ky kz Δ) ^ 2 *
        (z - rootPlus m kx ky kz Δ) ^ 2 := by
  rw [characteristic_polynomial, quadratic_factorization]
  ring

/-- Each negative-phase root is spectral. -/
theorem det_at_rootMinus (m kx ky kz Δ : ℝ) :
    Matrix.det
      (rootMinus m kx ky kz Δ • (1 : Mat4) - walk m kx ky kz Δ) = 0 := by
  rw [characteristic_double_factorization]
  ring

/-- Each positive-phase root is spectral. -/
theorem det_at_rootPlus (m kx ky kz Δ : ℝ) :
    Matrix.det
      (rootPlus m kx ky kz Δ • (1 : Mat4) - walk m kx ky kz Δ) = 0 := by
  rw [characteristic_double_factorization]
  ring

/-- The two roots have unit modulus. -/
theorem norm_rootMinus (m kx ky kz Δ : ℝ) :
    ‖rootMinus m kx ky kz Δ‖ = 1 := by
  rw [rootMinus, Complex.norm_exp]
  simp

theorem norm_rootPlus (m kx ky kz Δ : ℝ) :
    ‖rootPlus m kx ky kz Δ‖ = 1 := by
  rw [rootPlus, Complex.norm_exp]
  simp

end KomorebiPhysics.Spectrum3D
