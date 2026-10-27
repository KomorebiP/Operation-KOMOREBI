module

public import KomorebiPhysics.Relativistic1DGroupVelocity
public import KomorebiPhysics.Relativistic1DAsymptoticAlgebra

/-!
Exact checks for the 1D shell expansion, correction coefficient, and group velocity.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic1DAsymptoticExamples

open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.Dispersion1D
open KomorebiPhysics.Relativistic1DShellAsymptotics
open KomorebiPhysics.Relativistic1DAsymptoticAlgebra
open KomorebiPhysics.Relativistic1DGroupVelocity

/-- At m=k=1 the shell polynomial is `1-ε²+ε⁴/3`. -/
theorem shellPoly4_one_one (ε : ℝ) :
    shellPoly4 1 1 ε = 1 - ε^2 + ε^4/3 := by
  norm_num [shellPoly4, shellQuarticCoeff]
  ring

/-- The fourth shell derivative is nonzero in the symmetric massive example. -/
theorem shell_deriv4_one_one :
    iteratedDeriv 4 (fun ε => shell 1 1 ε) 0 = 8 := by
  norm_num [shell_deriv4_zero]

/-- The sixth shell derivative is also nonzero, so the Taylor remainder control is not vacuous. -/
theorem shell_deriv6_one_one :
    iteratedDeriv 6 (fun ε => shell 1 1 ε) 0 = -32 := by
  norm_num [shell_deriv6_zero]

/-- Concrete source-shell remainder. -/
theorem shell_one_one_remainder :
    (fun ε => shell 1 1 ε - (1 - ε^2 + ε^4/3)) =O[𝓝 0]
      (fun ε : ℝ => ε^6) := by
  simpa only [shellPoly4_one_one] using (shell_expansion_isBigO (1 : ℝ) (1 : ℝ))

/-- Continuum energy at m=k=1 is sqrt 2 and is nonzero. -/
theorem energy_one_one : energy 1 1 = Real.sqrt 2 := by norm_num [energy]

theorem energy_one_one_ne_zero : energy 1 1 ≠ 0 := by
  rw [energy_one_one]
  positivity

/-- The correction has the expected exact radical form. -/
theorem correction_one_one : correction 1 1 = -(1 / (6 * Real.sqrt 2)) := by
  rw [correction, energy_one_one]
  norm_num
  ring

/-- The correction is strictly negative in the symmetric massive example. -/
theorem correction_one_one_neg : correction 1 1 < 0 := by
  rw [correction_one_one]
  have hs : 0 < Real.sqrt 2 := by positivity
  exact neg_lt_zero.mpr (div_pos one_pos (mul_pos (by norm_num) hs))

/-- The squared-shell coefficient is exactly `-1/3`. -/
theorem squared_coefficient_one_one :
    2 * energy 1 1 * correction 1 1 = -(1/3 : ℝ) := by
  have h := twice_energy_mul_correction (m := 1) (k := 1) energy_one_one_ne_zero
  norm_num at h
  exact h

/-- Exact polynomial squared-shell witness. -/
theorem frequencyPoly2_one_one_sq (ε : ℝ) :
    frequencyPoly2 1 1 ε ^ 2 - 2 =
      -(1/3 : ℝ) * ε^2 + correction 1 1 ^ 2 * ε^4 := by
  have h := frequencyPoly2_sq_mass_shell (m := 1) (k := 1) (ε := ε) energy_one_one_ne_zero
  calc
    frequencyPoly2 1 1 ε ^ 2 - 2 = frequencyPoly2 1 1 ε ^ 2 - 1^2 - 1^2 := by ring
    _ = -(1^2 * 1^2) / 3 * ε^2 + correction 1 1 ^ 2 * ε^4 := h
    _ = -(1/3 : ℝ) * ε^2 + correction 1 1 ^ 2 * ε^4 := by norm_num

/-- The doubly-degenerate point has zero continuum energy. -/
theorem degenerate_energy_zero : energy 0 0 = 0 := by simp [energy]

/-- The totalized correction formula evaluates to zero at the degenerate point;
this is not used as a license to divide by the physical energy there. -/
theorem degenerate_correction_zero : correction 0 0 = 0 := by simp [correction]

/-- At zero mass the shell is independent of the mass step and the second-order correction vanishes. -/
theorem massless_correction_zero (k : ℝ) : correction 0 k = 0 := correction_zero_mass k

/-- At zero momentum the second-order frequency correction vanishes. -/
theorem rest_correction_zero (m : ℝ) : correction m 0 = 0 := correction_zero_momentum m

/-- The exact shell derivative at k=0 is zero for every spacing. -/
theorem shell_momentum_derivative_at_rest (m ε : ℝ) :
    HasDerivAt (fun q => shell m q ε) 0 0 := by
  have h := hasDerivAt_shell_momentum m 0 ε
  convert h using 1
  simp

/-- At a regular point the exact group velocity changes sign under k -> -k. -/
theorem exact_group_velocity_odd (m k ε : ℝ) (hε : ε ≠ 0) :
    Real.cos (m*ε) * Real.sin ((-k)*ε) /
        Real.sin (principalFrequency m (-k) ε hε * ε) =
      -(Real.cos (m*ε) * Real.sin (k*ε) /
        Real.sin (principalFrequency m k ε hε * ε)) :=
  groupVelocity_neg_momentum m k ε hε

end KomorebiPhysics.Relativistic1DAsymptoticExamples
