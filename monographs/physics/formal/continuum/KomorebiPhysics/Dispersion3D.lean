module

public import KomorebiPhysics.DiracWalk3D
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.Module
public import Mathlib.Tactic.Ring

/-!
Exact Clifford norm, quadratic shell, and principal phase for the 3D walk.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Dispersion3D

open scoped Matrix ComplexConjugate BigOperators
open KomorebiPhysics.RelativisticClifford3D
open KomorebiPhysics.DiracWalk3D

/-- Square of a general vector in the four-generator Clifford span. -/
theorem cliffordVector_sq (a b c d : ℂ) :
    (a • beta + b • alphaX + c • alphaY + d • alphaZ) *
        (a • beta + b • alphaX + c • alphaY + d • alphaZ) =
      (a ^ 2 + b ^ 2 + c ^ 2 + d ^ 2) • (1 : Mat4) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [beta, alphaX, alphaY, alphaZ, Matrix.mul_apply, Fin.sum_univ_four]
  all_goals ring_nf <;> simp

/-- Telescoping trigonometric norm of the walk coefficients. -/
theorem coefficient_norm_real (m kx ky kz Δ : ℝ) :
    betaCoeff m kx ky kz Δ ^ 2 + xCoeff kx ky kz Δ ^ 2 +
        yCoeff ky kz Δ ^ 2 + zCoeff kz Δ ^ 2 =
      1 - shell m kx ky kz Δ ^ 2 := by
  have hm := Real.sin_sq_add_cos_sq (m * Δ)
  have hx := Real.sin_sq_add_cos_sq (kx * Δ)
  have hy := Real.sin_sq_add_cos_sq (ky * Δ)
  have hz := Real.sin_sq_add_cos_sq (kz * Δ)
  have hsm : Real.sin (m * Δ) ^ 2 = 1 - Real.cos (m * Δ) ^ 2 := by nlinarith
  have hsx : Real.sin (kx * Δ) ^ 2 = 1 - Real.cos (kx * Δ) ^ 2 := by nlinarith
  have hsy : Real.sin (ky * Δ) ^ 2 = 1 - Real.cos (ky * Δ) ^ 2 := by nlinarith
  have hsz : Real.sin (kz * Δ) ^ 2 = 1 - Real.cos (kz * Δ) ^ 2 := by nlinarith
  have hsx' : Real.sin (Δ * kx) ^ 2 = 1 - Real.cos (Δ * kx) ^ 2 := by
    simpa [mul_comm] using hsx
  have hsy' : Real.sin (Δ * ky) ^ 2 = 1 - Real.cos (Δ * ky) ^ 2 := by
    simpa [mul_comm] using hsy
  have hsz' : Real.sin (Δ * kz) ^ 2 = 1 - Real.cos (Δ * kz) ^ 2 := by
    simpa [mul_comm] using hsz
  rw [betaCoeff, xCoeff, yCoeff, zCoeff, shell]
  ring_nf
  rw [hsm, hsx', hsy', hsz']
  ring

/-- Complex-cast form of the coefficient norm. -/
theorem coefficient_norm_complex (m kx ky kz Δ : ℝ) :
    (betaCoeff m kx ky kz Δ : ℂ) ^ 2 + (xCoeff kx ky kz Δ : ℂ) ^ 2 +
        (yCoeff ky kz Δ : ℂ) ^ 2 + (zCoeff kz Δ : ℂ) ^ 2 =
      1 - (shell m kx ky kz Δ : ℂ) ^ 2 := by
  exact_mod_cast coefficient_norm_real m kx ky kz Δ

/-- The Clifford-vector part squares to the complementary shell weight. -/
theorem vectorPart_sq (m kx ky kz Δ : ℝ) :
    vectorPart m kx ky kz Δ * vectorPart m kx ky kz Δ =
      (1 - (shell m kx ky kz Δ : ℂ) ^ 2) • (1 : Mat4) := by
  rw [vectorPart, cliffordVector_sq, coefficient_norm_complex]

/-- Exact quadratic shell relation for the closed update. -/
theorem closedWalk_quadratic (m kx ky kz Δ : ℝ) :
    closedWalk m kx ky kz Δ * closedWalk m kx ky kz Δ -
        (2 * (shell m kx ky kz Δ : ℂ)) • closedWalk m kx ky kz Δ +
        (1 : Mat4) = 0 := by
  rw [closedWalk]
  rw [Matrix.sub_mul, Matrix.mul_sub, Matrix.mul_sub]
  rw [Matrix.smul_mul, Matrix.mul_smul, Matrix.smul_mul, Matrix.mul_smul,
    Matrix.smul_mul, Matrix.mul_smul, Matrix.smul_mul, Matrix.mul_smul]
  rw [vectorPart_sq]
  simp only [Matrix.one_mul, Matrix.mul_one, smul_smul]
  match_scalars
  all_goals ring_nf
  all_goals simp

/-- Exact quadratic shell relation for the literal walk. -/
theorem walk_quadratic (m kx ky kz Δ : ℝ) :
    walk m kx ky kz Δ * walk m kx ky kz Δ -
        (2 * (shell m kx ky kz Δ : ℂ)) • walk m kx ky kz Δ +
        (1 : Mat4) = 0 := by
  rw [walk_eq_closedWalk]
  exact closedWalk_quadratic m kx ky kz Δ

/-- Principal lattice phase of the 3D shell. -/
def phase (m kx ky kz Δ : ℝ) : ℝ :=
  Real.arccos (shell m kx ky kz Δ)

/-- The phase lies on the principal branch. -/
theorem phase_nonneg (m kx ky kz Δ : ℝ) :
    0 ≤ phase m kx ky kz Δ := by
  exact Real.arccos_nonneg _

theorem phase_le_pi (m kx ky kz Δ : ℝ) :
    phase m kx ky kz Δ ≤ Real.pi := by
  exact Real.arccos_le_pi _

/-- Exact shell equation (8.30). -/
theorem cos_phase (m kx ky kz Δ : ℝ) :
    Real.cos (phase m kx ky kz Δ) = shell m kx ky kz Δ := by
  rw [phase]
  exact Real.cos_arccos
    (abs_le.mp (abs_shell_le_one m kx ky kz Δ)).1
    (abs_le.mp (abs_shell_le_one m kx ky kz Δ)).2

/-- Positive-spacing frequency. -/
def frequency (m kx ky kz Δ : ℝ) : ℝ :=
  phase m kx ky kz Δ / Δ

/-- Exact frequency shell whenever the spacing is nonzero. -/
theorem cos_frequency_spacing (m kx ky kz Δ : ℝ) (hΔ : Δ ≠ 0) :
    Real.cos (frequency m kx ky kz Δ * Δ) = shell m kx ky kz Δ := by
  rw [frequency, div_mul_cancel₀ _ hΔ, cos_phase]

end KomorebiPhysics.Dispersion3D
