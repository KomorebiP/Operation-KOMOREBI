module

public import KomorebiPhysics.Relativistic1DContinuumLimit

@[expose] public section

open Filter Asymptotics
open scoped Topology

set_option autoImplicit false

namespace KomorebiPhysics.Relativistic1DContinuumExamples

open KomorebiPhysics.Dispersion1D
open KomorebiPhysics.Relativistic1DShellAsymptotics
open KomorebiPhysics.Relativistic1DAsymptoticAlgebra
open KomorebiPhysics.Relativistic1DContinuumLimit

noncomputable section

@[simp] theorem energy_one_one : energy 1 1 = Real.sqrt 2 := by
  norm_num [energy]

theorem energy_one_one_ne_zero : energy 1 1 ≠ 0 := by
  rw [energy_one_one]
  positivity

theorem correction_one_one :
    correction 1 1 = -(1 : ℝ) / (6 * Real.sqrt 2) := by
  rw [correction]
  simp only [one_pow, one_mul, energy_one_one]

theorem correction_one_one_neg : correction 1 1 < 0 := by
  rw [correction_one_one]
  exact div_neg_of_neg_of_pos (by norm_num) (mul_pos (by norm_num) (Real.sqrt_pos.2 (by norm_num)))

theorem correction_one_one_ne_zero : correction 1 1 ≠ 0 :=
  ne_of_lt correction_one_one_neg

/-- Nontrivial exact-frequency instance of equation (8.11). -/
theorem frequency_one_one_expansion :
    (fun ε => positiveFrequency 1 1 ε - frequencyPoly2 1 1 ε) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^4) :=
  positiveFrequency_expansion_isBigO energy_one_one_ne_zero

/-- Nontrivial exact-frequency instance of equation (8.12). -/
theorem mass_shell_one_one_expansion :
    (fun ε => positiveFrequency 1 1 ε ^ 2 - 2 + (1/3 : ℝ) * ε^2) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^4) := by
  have h := positiveFrequency_mass_shell_isBigO energy_one_one_ne_zero
  convert h using 1
  · funext ε
    ring

/-- Nontrivial exact group-velocity instance of equation (8.14). -/
theorem velocity_one_one_expansion :
    (fun ε => positiveGroupVelocity 1 1 ε - 1 / Real.sqrt 2) =O[𝓝[>] 0]
      (fun ε : ℝ => ε^2) := by
  have h := positiveGroupVelocity_expansion_isBigO energy_one_one_ne_zero
  convert h using 1
  · funext ε
    norm_num [energy]

theorem shell_interior_one_one :
    ∀ᶠ ε in 𝓝[>] 0, |shell 1 1 ε| < 1 :=
  eventually_abs_shell_lt_one energy_one_one_ne_zero

theorem velocity_is_actual_derivative_one_one :
    ∀ᶠ ε in 𝓝[>] 0,
      HasDerivAt (fun q => positiveFrequency 1 q ε)
        (positiveGroupVelocity 1 1 ε) 1 :=
  eventually_hasDerivAt_positiveGroupVelocity energy_one_one_ne_zero

end

end KomorebiPhysics.Relativistic1DContinuumExamples
