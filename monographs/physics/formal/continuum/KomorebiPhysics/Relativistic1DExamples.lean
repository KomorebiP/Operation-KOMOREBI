module

public import KomorebiPhysics.Dispersion1D

/-!
Exact nonzero witnesses and hypothesis-sensitivity checks for the one-dimensional
relativistic update. These are algebraic examples, not asymptotic or numerical tests.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic1DExamples

open scoped Matrix ComplexConjugate
open KomorebiPhysics.RelativisticPauli
open KomorebiPhysics.InvolutionExponential
open KomorebiPhysics.DiracWalk1D
open KomorebiPhysics.Dispersion1D

/-- The half-turn test spacing is nonzero. -/
theorem pi_div_two_ne_zero : (Real.pi / 2 : ℝ) ≠ 0 := by
  positivity

/-- At `m=k=1, ε=π/2`, the exact shell vanishes. -/
theorem shell_pi_div_two : shell 1 1 (Real.pi / 2) = 0 := by
  simp [shell]

/-- The principal phase at the half-turn witness is exactly `π/2`. -/
theorem principalPhase_pi_div_two :
    principalPhase 1 1 (Real.pi / 2) = Real.pi / 2 := by
  rw [principalPhase, shell_pi_div_two, Real.arccos_zero]

/-- The principal frequency at the half-turn witness is exactly one. -/
theorem principalFrequency_pi_div_two :
    principalFrequency 1 1 (Real.pi / 2) pi_div_two_ne_zero = 1 := by
  rw [principalFrequency, principalPhase_pi_div_two]
  field_simp [Real.pi_ne_zero]

/-- The exact update at the witness is the nontrivial Pauli product `αβ`. -/
theorem update_pi_div_two :
    update 1 1 (Real.pi / 2) = alpha * beta := by
  rw [update_explicit]
  simp only [one_mul]
  rw [complex_exp_neg_I (Real.pi / 2), complex_exp_pos_I (Real.pi / 2)]
  simp [Real.cos_pi_div_two, Real.sin_pi_div_two]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alpha, beta, Matrix.mul_apply, Fin.sum_univ_two]

/-- The witness update is not the identity. -/
theorem update_pi_div_two_ne_one :
    update 1 1 (Real.pi / 2) ≠ (1 : Mat2) := by
  rw [update_pi_div_two]
  intro h
  have h01 := congrFun (congrFun h (0 : Fin 2)) (1 : Fin 2)
  norm_num [alpha, beta, Matrix.mul_apply, Fin.sum_univ_two] at h01

/-- The witness trace is exactly zero. -/
theorem trace_update_pi_div_two :
    Matrix.trace (update 1 1 (Real.pi / 2)) = 0 := by
  rw [trace_eq_two_shell, shell_pi_div_two]
  norm_num

/-- The witness determinant remains exactly one. -/
theorem det_update_pi_div_two :
    Matrix.det (update 1 1 (Real.pi / 2)) = 1 := by
  exact det_update _ _ _

/-- The exact characteristic polynomial at the witness is `z²+1`. -/
theorem characteristic_pi_div_two (z : ℂ) :
    Matrix.det (z • (1 : Mat2) - update 1 1 (Real.pi / 2)) = z ^ 2 + 1 := by
  rw [characteristic_polynomial, shell_pi_div_two]
  norm_num

/-- The two Pauli update factors genuinely fail to commute. -/
theorem pauli_products_ne : alpha * beta ≠ beta * alpha := by
  intro h
  have h01 := congrFun (congrFun h (0 : Fin 2)) (1 : Fin 2)
  norm_num [alpha, beta, Matrix.mul_apply, Fin.sum_univ_two] at h01

/-- Reversing the order of the two half-turn steps changes the update. -/
theorem reverse_order_changes_half_turn :
    massStep 1 (Real.pi / 2) * shiftStep 1 (Real.pi / 2) ≠
      shiftStep 1 (Real.pi / 2) * massStep 1 (Real.pi / 2) := by
  rw [← update]
  rw [update_pi_div_two]
  have hm : massStep 1 (Real.pi / 2) = (-Complex.I) • beta := by
    rw [massStep_closed]
    simp [closedFactor]
  have hs : shiftStep 1 (Real.pi / 2) = (-Complex.I) • alpha := by
    rw [shiftStep_closed]
    simp [closedFactor]
  rw [hm, hs]
  intro h
  have h01 := congrFun (congrFun h (0 : Fin 2)) (1 : Fin 2)
  norm_num [alpha, beta, Matrix.mul_apply, Fin.sum_univ_two] at h01

/-- Zero mass gives the exact massless shell `cos(k ε)`. -/
theorem shell_zero_mass (k ε : ℝ) : shell 0 k ε = Real.cos (k * ε) := by
  simp [shell]

/-- Zero momentum gives the exact rest shell `cos(m ε)`. -/
theorem shell_zero_momentum (m ε : ℝ) : shell m 0 ε = Real.cos (m * ε) := by
  simp [shell]

/-- The shell is one at zero spacing. -/
theorem shell_zero_spacing (m k : ℝ) : shell m k 0 = 1 := by
  simp [shell]

/-- The principal phase is zero at zero spacing, even though frequency division is not defined there. -/
theorem principalPhase_zero_spacing (m k : ℝ) : principalPhase m k 0 = 0 := by
  simp [principalPhase, shell, Real.arccos_one]

end KomorebiPhysics.Relativistic1DExamples
