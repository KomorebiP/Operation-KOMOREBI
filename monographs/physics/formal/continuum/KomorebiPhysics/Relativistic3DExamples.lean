module

public import KomorebiPhysics.Spectrum3D
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.Ring

/-!
Exact nontrivial and boundary witnesses for the three-dimensional Clifford walk.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.Relativistic3DExamples

open scoped Matrix ComplexConjugate BigOperators
open KomorebiPhysics.RelativisticClifford3D
open KomorebiPhysics.InvolutionExponential4
open KomorebiPhysics.DiracWalk3D
open KomorebiPhysics.Dispersion3D
open KomorebiPhysics.Spectrum3D

/-- Microcell spacing from equation (8.26). -/
def microcell (Δ : ℝ) : ℝ := Δ / 2

/-- Two microcells recover one full lattice spacing. -/
theorem two_mul_microcell (Δ : ℝ) : 2 * microcell Δ = Δ := by
  rw [microcell]
  ring

/-- A pure `z` quarter-turn has vanishing scalar shell. -/
theorem axis_shell : shell 0 0 0 1 (Real.pi / 2) = 0 := by
  simp [shell, Real.cos_pi_div_two]

/-- Its vector part is exactly `α_z`. -/
theorem axis_vectorPart :
    vectorPart 0 0 0 1 (Real.pi / 2) = alphaZ := by
  simp [vectorPart, betaCoeff, xCoeff, yCoeff, zCoeff,
    Real.cos_pi_div_two, Real.sin_pi_div_two]

/-- Exact nontrivial axis walk. -/
theorem axis_walk :
    walk 0 0 0 1 (Real.pi / 2) = -Complex.I • alphaZ := by
  rw [walk_eq_closedWalk]
  simp [closedWalk, axis_shell, axis_vectorPart]

/-- The axis walk is not the identity. -/
theorem axis_walk_ne_one :
    walk 0 0 0 1 (Real.pi / 2) ≠ (1 : Mat4) := by
  rw [axis_walk]
  intro h
  have h02 := congrArg (fun A : Mat4 => A 0 2) h
  simp [alphaZ] at h02

/-- The axis witness has trace zero. -/
theorem axis_trace :
    Matrix.trace (walk 0 0 0 1 (Real.pi / 2)) = 0 := by
  rw [trace_walk, axis_shell]
  norm_num

/-- The axis witness retains determinant one. -/
theorem axis_det :
    Matrix.det (walk 0 0 0 1 (Real.pi / 2)) = 1 :=
  det_walk 0 0 0 1 (Real.pi / 2)

/-- Its characteristic polynomial is `(z²+1)²`. -/
theorem axis_characteristic (z : ℂ) :
    Matrix.det
        (z • (1 : Mat4) - walk 0 0 0 1 (Real.pi / 2)) =
      (z ^ 2 + 1) ^ 2 := by
  rw [characteristic_polynomial, axis_shell]
  norm_num

/-- The principal phase of the axis witness is `π/2`. -/
theorem axis_phase : phase 0 0 0 1 (Real.pi / 2) = Real.pi / 2 := by
  rw [phase, axis_shell, Real.arccos_zero]

/-- The doubled roots specialize to `-i` and `+i`. -/
theorem axis_rootMinus :
    rootMinus 0 0 0 1 (Real.pi / 2) = -Complex.I := by
  rw [rootMinus_closed, axis_phase]
  simp [Real.cos_pi_div_two, Real.sin_pi_div_two]

theorem axis_rootPlus :
    rootPlus 0 0 0 1 (Real.pi / 2) = Complex.I := by
  rw [rootPlus_closed, axis_phase]
  simp [Real.cos_pi_div_two, Real.sin_pi_div_two]

/-- The two spectral branches are genuinely distinct in the axis witness. -/
theorem axis_roots_ne :
    rootMinus 0 0 0 1 (Real.pi / 2) ≠
      rootPlus 0 0 0 1 (Real.pi / 2) := by
  rw [axis_rootMinus, axis_rootPlus]
  intro h
  have hi := congrArg Complex.im h
  norm_num at hi

/-- Closed quarter-turn factors about `x` and `y` do not commute. -/
theorem quarter_x_y_noncommute :
    closedFactor alphaX (Real.pi / 2) * closedFactor alphaY (Real.pi / 2) ≠
      closedFactor alphaY (Real.pi / 2) * closedFactor alphaX (Real.pi / 2) := by
  intro h
  have h00 := congrArg (fun A : Mat4 => A 0 0) h
  simp [closedFactor, alphaX, alphaY, Matrix.mul_apply, Fin.sum_univ_four,
    Real.cos_pi_div_two, Real.sin_pi_div_two] at h00
  have hi := congrArg Complex.im h00
  norm_num at hi

/-- At zero parameters the update is exactly the identity. -/
theorem zero_walk : walk 0 0 0 0 0 = (1 : Mat4) := by
  rw [walk_eq_closedWalk]
  simp [closedWalk, vectorPart, shell, betaCoeff, xCoeff, yCoeff, zCoeff]

/-- The zero-parameter shell has a quadruple root at one. -/
theorem zero_characteristic (z : ℂ) :
    Matrix.det (z • (1 : Mat4) - walk 0 0 0 0 0) = (z - 1) ^ 4 := by
  rw [characteristic_polynomial]
  simp [shell]
  ring

/-- Reversing the sign of the `z` momentum conjugates the axis update. -/
theorem axis_sign_flip :
    walk 0 0 0 (-1) (Real.pi / 2) = Complex.I • alphaZ := by
  rw [walk_eq_closedWalk]
  simp [closedWalk, vectorPart, shell, betaCoeff, xCoeff, yCoeff, zCoeff,
    Real.cos_pi_div_two, Real.sin_pi_div_two, Real.cos_neg, Real.sin_neg]

/-- Opposite axis momenta give different updates. -/
theorem opposite_axis_walks_ne :
    walk 0 0 0 1 (Real.pi / 2) ≠ walk 0 0 0 (-1) (Real.pi / 2) := by
  rw [axis_walk, axis_sign_flip]
  intro h
  have h02 := congrArg (fun A : Mat4 => A 0 2) h
  simp [alphaZ] at h02
  have hi := congrArg Complex.im h02
  norm_num at hi

end KomorebiPhysics.Relativistic3DExamples
