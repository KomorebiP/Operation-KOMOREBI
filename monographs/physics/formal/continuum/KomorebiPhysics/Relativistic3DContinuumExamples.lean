module

public import KomorebiPhysics.Relativistic3DAnisotropy

/-!
Concrete witnesses for the checked three-dimensional continuum, velocity, and
axis-versus-diagonal anisotropy formulas.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DContinuumExamples

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Relativistic3DShellAsymptotics
open KomorebiPhysics.Relativistic3DContinuumLimit
open KomorebiPhysics.Relativistic3DGroupVelocity
open KomorebiPhysics.Relativistic3DAnisotropy

@[simp] theorem energy3_one_one_zero_zero :
    energy3 1 1 0 0 = Real.sqrt 2 := by
  norm_num [energy3]

theorem energy3_one_one_zero_zero_ne_zero : energy3 1 1 0 0 ≠ 0 := by
  rw [energy3_one_one_zero_zero]
  positivity

@[simp] theorem anisotropyQ_one_one_zero_zero :
    anisotropyQ 1 1 0 0 = 1 := by
  norm_num [anisotropyQ]

theorem correction3_one_one_zero_zero :
    correction3 1 1 0 0 = -(1 : ℝ) / (6 * Real.sqrt 2) := by
  rw [correction3, anisotropyQ_one_one_zero_zero,
    energy3_one_one_zero_zero]

theorem correction3_one_one_zero_zero_neg :
    correction3 1 1 0 0 < 0 := by
  rw [correction3_one_one_zero_zero]
  exact div_neg_of_neg_of_pos (by norm_num)
    (mul_pos (by norm_num) (Real.sqrt_pos.2 (by norm_num)))

/-- Nontrivial exact-frequency witness for equations (8.31)--(8.33). -/
theorem frequency3_one_one_zero_zero_expansion :
    (fun ε => positiveFrequency3 1 1 0 0 ε -
      frequencyPoly2_3 1 1 0 0 ε) =O[𝓝[>] 0]
        (fun ε : ℝ => ε^4) :=
  positiveFrequency3_expansion_isBigO energy3_one_one_zero_zero_ne_zero

/-- The x velocity has the expected relativistic continuum limit. -/
theorem velocityX3_one_one_zero_zero_expansion :
    (fun ε => positiveGroupVelocityX3 1 1 0 0 ε -
      1 / Real.sqrt 2) =O[𝓝[>] 0] (fun ε : ℝ => ε^2) := by
  have h := positiveGroupVelocityX3_expansion_isBigO
    energy3_one_one_zero_zero_ne_zero
  convert h using 1
  funext ε
  rw [energy3_one_one_zero_zero]

/-- The transverse y velocity is quadratically small in the same witness. -/
theorem velocityY3_one_one_zero_zero_expansion :
    (fun ε => positiveGroupVelocityY3 1 1 0 0 ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have h := positiveGroupVelocityY3_expansion_isBigO
    energy3_one_one_zero_zero_ne_zero
  simpa using h

/-- The transverse z velocity is quadratically small in the same witness. -/
theorem velocityZ3_one_one_zero_zero_expansion :
    (fun ε => positiveGroupVelocityZ3 1 1 0 0 ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have h := positiveGroupVelocityZ3_expansion_isBigO
    energy3_one_one_zero_zero_ne_zero
  simpa using h

/-- The checked velocity components are eventually the actual momentum derivatives. -/
theorem velocity3_one_one_zero_zero_actual_derivatives :
    ∀ᶠ ε in 𝓝[>] 0,
      HasDerivAt (fun q => positiveFrequency3 1 q 0 0 ε)
          (positiveGroupVelocityX3 1 1 0 0 ε) 1 ∧
      HasDerivAt (fun q => positiveFrequency3 1 1 q 0 ε)
          (positiveGroupVelocityY3 1 1 0 0 ε) 0 ∧
      HasDerivAt (fun q => positiveFrequency3 1 1 0 q ε)
          (positiveGroupVelocityZ3 1 1 0 0 ε) 0 :=
  eventually_hasDerivAt_positiveGroupVelocityVector3
    energy3_one_one_zero_zero_ne_zero

@[simp] theorem fixedRadiusEnergy_zero_one :
    fixedRadiusEnergy 0 1 = 1 := by
  norm_num [fixedRadiusEnergy]

/-- Concrete nonzero anisotropy coefficient. -/
theorem massless_unit_axis_diagonal_coefficient :
    (1 : ℝ)^4 / (18 * fixedRadiusEnergy 0 1) = 1 / 18 :=
  massless_unit_axis_sub_diagonal_coefficient

/-- Concrete exact-frequency witness for equations (8.37)--(8.41). -/
theorem massless_unit_axis_sub_diagonal_expansion :
    (fun ε => axisFrequency3 0 1 ε - diagonalFrequency3 0 1 ε -
      (1 / 18 : ℝ) * ε^2) =O[𝓝[>] 0] (fun ε : ℝ => ε^4) := by
  have h := axis_sub_diagonal_frequency_expansion_isBigO
    (m := 0) (κ := 1) (by norm_num [fixedRadiusEnergy])
  convert h using 1
  funext ε
  rw [fixedRadiusEnergy_zero_one]
  ring

/-- The concrete anisotropy coefficient is strictly positive. -/
theorem massless_unit_axis_diagonal_coefficient_pos :
    0 < (1 / 18 : ℝ) := by norm_num

end KomorebiPhysics.Relativistic3DContinuumExamples
