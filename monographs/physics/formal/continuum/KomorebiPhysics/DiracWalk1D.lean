module

public import KomorebiPhysics.InvolutionExponential
public import Mathlib.Tactic.NoncommRing

/-!
Exact one-dimensional discrete relativistic update, equations (8.2)--(8.5),
before any small-spacing asymptotics.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.DiracWalk1D

open NormedSpace
open scoped Matrix ComplexConjugate
open RelativisticPauli InvolutionExponential

/-- Mass rotation `exp(-i m ε β)`. -/
def massStep (m ε : ℝ) : Mat2 :=
  exp (((-Complex.I * ((m * ε : ℝ) : ℂ))) • beta)

/-- Spatial phase `exp(-i k ε α)`. -/
def shiftStep (k ε : ℝ) : Mat2 :=
  exp (((-Complex.I * ((k * ε : ℝ) : ℂ))) • alpha)

/-- The ordered update `U_ε(k)` from (8.2). -/
def update (m k ε : ℝ) : Mat2 := massStep m ε * shiftStep k ε

/-- Mass factor in the closed involution form. -/
theorem massStep_closed (m ε : ℝ) :
    massStep m ε = closedFactor beta (m * ε) := by
  exact exp_beta_closed (m * ε)

/-- Shift factor in the closed involution form. -/
theorem shiftStep_closed (k ε : ℝ) :
    shiftStep k ε = closedFactor alpha (k * ε) := by
  exact exp_alpha_closed (k * ε)

/-- Exact mass-factor entries. -/
theorem massStep_explicit (m ε : ℝ) :
    massStep m ε =
      !![(Real.cos (m * ε) : ℂ), -Complex.I * (Real.sin (m * ε) : ℂ);
         -Complex.I * (Real.sin (m * ε) : ℂ), (Real.cos (m * ε) : ℂ)] := by
  rw [massStep_closed, closedFactor_beta]

/-- Exact spatial-factor entries. -/
theorem shiftStep_explicit (k ε : ℝ) :
    shiftStep k ε =
      !![(Real.cos (k * ε) : ℂ) - Complex.I * (Real.sin (k * ε) : ℂ), 0;
         0, (Real.cos (k * ε) : ℂ) + Complex.I * (Real.sin (k * ε) : ℂ)] := by
  rw [shiftStep_closed, closedFactor_alpha]

/-- Equation (8.9): the literal exponential product equals the two closed involution factors. -/
theorem update_closed_product (m k ε : ℝ) :
    update m k ε = closedFactor beta (m * ε) * closedFactor alpha (k * ε) := by
  rw [update, massStep_closed, shiftStep_closed]

/-- Exact entry formula for the ordered update. -/
theorem update_explicit (m k ε : ℝ) :
    update m k ε =
      !![(Real.cos (m * ε) : ℂ) * Complex.exp (-Complex.I * ((k * ε : ℝ) : ℂ)),
         -Complex.I * (Real.sin (m * ε) : ℂ) * Complex.exp (Complex.I * ((k * ε : ℝ) : ℂ));
         -Complex.I * (Real.sin (m * ε) : ℂ) * Complex.exp (-Complex.I * ((k * ε : ℝ) : ℂ)),
         (Real.cos (m * ε) : ℂ) * Complex.exp (Complex.I * ((k * ε : ℝ) : ℂ))] := by
  rw [update, massStep_explicit, shiftStep_explicit,
    complex_exp_neg_I (k * ε), complex_exp_pos_I (k * ε)]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [Matrix.mul_apply, Fin.sum_univ_two]

/-- Exact left-unitarity of the mass factor. -/
theorem massStep_unitary_left (m ε : ℝ) :
    (massStep m ε).conjTranspose * massStep m ε = 1 :=
  exp_beta_unitary_left (m * ε)

/-- Exact right-unitarity of the mass factor. -/
theorem massStep_unitary_right (m ε : ℝ) :
    massStep m ε * (massStep m ε).conjTranspose = 1 :=
  exp_beta_unitary_right (m * ε)

/-- Exact left-unitarity of the shift factor. -/
theorem shiftStep_unitary_left (k ε : ℝ) :
    (shiftStep k ε).conjTranspose * shiftStep k ε = 1 :=
  exp_alpha_unitary_left (k * ε)

/-- Exact right-unitarity of the shift factor. -/
theorem shiftStep_unitary_right (k ε : ℝ) :
    shiftStep k ε * (shiftStep k ε).conjTranspose = 1 :=
  exp_alpha_unitary_right (k * ε)

/-- Equation (8.3), left-unitarity of the full update. -/
theorem update_unitary_left (m k ε : ℝ) :
    (update m k ε).conjTranspose * update m k ε = 1 := by
  rw [update, Matrix.conjTranspose_mul]
  calc
    (shiftStep k ε).conjTranspose * (massStep m ε).conjTranspose *
        (massStep m ε * shiftStep k ε)
        = (shiftStep k ε).conjTranspose *
            ((massStep m ε).conjTranspose * massStep m ε) * shiftStep k ε := by
              noncomm_ring
    _ = (shiftStep k ε).conjTranspose * shiftStep k ε := by rw [massStep_unitary_left]; simp
    _ = 1 := shiftStep_unitary_left k ε

/-- Right-unitarity of the full update. -/
theorem update_unitary_right (m k ε : ℝ) :
    update m k ε * (update m k ε).conjTranspose = 1 := by
  rw [update, Matrix.conjTranspose_mul]
  calc
    massStep m ε * shiftStep k ε *
        ((shiftStep k ε).conjTranspose * (massStep m ε).conjTranspose)
        = massStep m ε *
            (shiftStep k ε * (shiftStep k ε).conjTranspose) * (massStep m ε).conjTranspose := by
              noncomm_ring
    _ = massStep m ε * (massStep m ε).conjTranspose := by rw [shiftStep_unitary_right]; simp
    _ = 1 := massStep_unitary_right m ε

/-- Each mass factor has determinant one. -/
theorem det_massStep (m ε : ℝ) : Matrix.det (massStep m ε) = 1 :=
  det_exp_beta (m * ε)

/-- Each spatial factor has determinant one. -/
theorem det_shiftStep (k ε : ℝ) : Matrix.det (shiftStep k ε) = 1 :=
  det_exp_alpha (k * ε)

/-- Equation (8.4): determinant of the full update is one. -/
theorem det_update (m k ε : ℝ) : Matrix.det (update m k ε) = 1 := by
  rw [update, Matrix.det_mul, det_massStep, det_shiftStep, one_mul]

/-- Exact trace before normalizing by two. -/
theorem trace_update (m k ε : ℝ) :
    Matrix.trace (update m k ε) =
      2 * ((Real.cos (m * ε) * Real.cos (k * ε) : ℝ) : ℂ) := by
  rw [update_explicit, Matrix.trace_fin_two]
  change (Real.cos (m * ε) : ℂ) * Complex.exp (-Complex.I * ((k * ε : ℝ) : ℂ)) +
      (Real.cos (m * ε) : ℂ) * Complex.exp (Complex.I * ((k * ε : ℝ) : ℂ)) = _
  rw [complex_exp_neg_I (k * ε), complex_exp_pos_I (k * ε)]
  push_cast
  ring

/-- Equations (8.5)/(8.10): normalized trace gives the exact product shell. -/
theorem half_trace_update (m k ε : ℝ) :
    (1 / 2 : ℂ) * Matrix.trace (update m k ε) =
      ((Real.cos (m * ε) * Real.cos (k * ε) : ℝ) : ℂ) := by
  rw [trace_update]
  ring

/-- At zero spacing the exact update is the identity. -/
theorem update_zero_spacing (m k : ℝ) : update m k 0 = 1 := by
  rw [update_closed_product]
  simp [closedFactor]

/-- Vanishing mass leaves only the spatial phase. -/
theorem update_zero_mass (k ε : ℝ) : update 0 k ε = shiftStep k ε := by
  rw [update, massStep_closed]
  simp [closedFactor]

/-- Vanishing momentum leaves only the mass rotation. -/
theorem update_zero_momentum (m ε : ℝ) : update m 0 ε = massStep m ε := by
  rw [update, shiftStep_closed]
  simp [closedFactor]

end KomorebiPhysics.DiracWalk1D
