module

public import KomorebiPhysics.RelativisticPauli
public import Mathlib.Tactic.Ring

/-!
Literal matrix-exponential formulas for the Pauli involutions in Chapter 8.1.
The `Matrix.exp` expressions are reduced to their trigonometric closed forms;
the source's exponential notation is therefore not merely replaced by a definition.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.InvolutionExponential

open NormedSpace
open scoped Matrix ComplexConjugate
open RelativisticPauli

/-- Closed trigonometric factor `cos θ I - i sin θ A`. -/
def closedFactor (A : Mat2) (θ : ℝ) : Mat2 :=
  (Real.cos θ : ℂ) • (1 : Mat2) - (Complex.I * (Real.sin θ : ℂ)) • A

/-- Euler identity for the negative imaginary phase. -/
theorem complex_exp_neg_I (θ : ℝ) :
    Complex.exp (-Complex.I * (θ : ℂ)) =
      (Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ) := by
  rw [show -Complex.I * (θ : ℂ) = ((-θ : ℝ) : ℂ) * Complex.I by push_cast; ring]
  rw [Complex.exp_ofReal_mul_I]
  simp [Real.cos_neg, Real.sin_neg]
  ring

/-- Euler identity for the positive imaginary phase. -/
theorem complex_exp_pos_I (θ : ℝ) :
    Complex.exp (Complex.I * (θ : ℂ)) =
      (Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ) := by
  rw [show Complex.I * (θ : ℂ) = ((θ : ℝ) : ℂ) * Complex.I by ring]
  rw [Complex.exp_ofReal_mul_I]
  ring

/-- The literal `α` exponential diagonalizes coordinatewise. -/
theorem exp_alpha_diagonal (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • alpha) =
      !![Complex.exp (-Complex.I * (θ : ℂ)), 0;
         0, Complex.exp (Complex.I * (θ : ℂ))] := by
  have hz : (((-Complex.I * (θ : ℂ))) • alpha) =
      Matrix.diagonal (fun i : Spin => if i = 0 then (-Complex.I * (θ : ℂ))
                                      else (Complex.I * (θ : ℂ))) := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [alpha]
  rw [hz, Matrix.exp_diagonal]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [← Complex.exp_eq_exp_ℂ]

/-- Explicit closed form for the `α` factor. -/
theorem closedFactor_alpha (θ : ℝ) :
    closedFactor alpha θ =
      !![(Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ), 0;
         0, (Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ)] := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [closedFactor, alpha]

/-- Equation (8.8) for the actual `α=σ_z` generator. -/
theorem exp_alpha_closed (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • alpha) = closedFactor alpha θ := by
  rw [exp_alpha_diagonal, closedFactor_alpha, complex_exp_neg_I, complex_exp_pos_I]

/-- Conjugating the scaled `α` generator gives the scaled `β` generator. -/
theorem scaled_beta_conj (θ : ℝ) :
    ((-Complex.I * (θ : ℂ)) • beta) =
      diagonalizer * ((-Complex.I * (θ : ℂ)) • alpha) * diagonalizer⁻¹ := by
  rw [RelativisticPauli.diagonalizer_inv]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [diagonalizer, alpha, beta, Matrix.mul_apply, Fin.sum_univ_two]
  all_goals ring

/-- Explicit closed form for the `β` factor. -/
theorem closedFactor_beta (θ : ℝ) :
    closedFactor beta θ =
      !![(Real.cos θ : ℂ), -Complex.I * (Real.sin θ : ℂ);
         -Complex.I * (Real.sin θ : ℂ), (Real.cos θ : ℂ)] := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [closedFactor, beta]

/-- The diagonalizer transports the closed `α` factor to the closed `β` factor. -/
theorem diagonalizer_closedFactor (θ : ℝ) :
    diagonalizer * closedFactor alpha θ * diagonalizer⁻¹ = closedFactor beta θ := by
  rw [RelativisticPauli.diagonalizer_inv, closedFactor_alpha, closedFactor_beta]
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [diagonalizer, Matrix.mul_apply, Fin.sum_univ_two]
  all_goals ring

/-- Equation (8.8) for the actual `β=σ_x` generator. -/
theorem exp_beta_closed (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • beta) = closedFactor beta θ := by
  rw [scaled_beta_conj θ,
    Matrix.exp_conj diagonalizer _ RelativisticPauli.diagonalizer_isUnit,
    exp_alpha_closed, diagonalizer_closedFactor]

/-- Determinant of the `α` factor is exactly one. -/
theorem det_closedFactor_alpha (θ : ℝ) : Matrix.det (closedFactor alpha θ) = 1 := by
  rw [closedFactor_alpha, Matrix.det_fin_two]
  change ((Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ)) *
      ((Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ)) - 0 * 0 = 1
  have h : ((Real.sin θ : ℂ)^2 + (Real.cos θ : ℂ)^2) = 1 := by
    exact_mod_cast Real.sin_sq_add_cos_sq θ
  rw [zero_mul, sub_zero]
  calc
    _ = (Real.cos θ : ℂ)^2 + (Real.sin θ : ℂ)^2 := by
      ring_nf
      rw [pow_two Complex.I, Complex.I_mul_I]
      ring
    _ = 1 := by
      rw [add_comm]
      exact h

/-- Determinant of the `β` factor is exactly one. -/
theorem det_closedFactor_beta (θ : ℝ) : Matrix.det (closedFactor beta θ) = 1 := by
  rw [closedFactor_beta, Matrix.det_fin_two]
  change (Real.cos θ : ℂ) * (Real.cos θ : ℂ) -
      (-Complex.I * (Real.sin θ : ℂ)) * (-Complex.I * (Real.sin θ : ℂ)) = 1
  have h : ((Real.sin θ : ℂ)^2 + (Real.cos θ : ℂ)^2) = 1 := by
    exact_mod_cast Real.sin_sq_add_cos_sq θ
  calc
    _ = (Real.cos θ : ℂ)^2 + (Real.sin θ : ℂ)^2 := by
      ring_nf
      rw [pow_two Complex.I, Complex.I_mul_I]
      ring
    _ = 1 := by
      rw [add_comm]
      exact h

/-- The scaled `α` generator is skew-Hermitian. -/
theorem alpha_generator_skew (θ : ℝ) :
    (((-Complex.I * (θ : ℂ)) • alpha).conjTranspose) =
      - ((-Complex.I * (θ : ℂ)) • alpha) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [alpha, Matrix.conjTranspose_apply]

/-- The scaled `β` generator is skew-Hermitian. -/
theorem beta_generator_skew (θ : ℝ) :
    (((-Complex.I * (θ : ℂ)) • beta).conjTranspose) =
      - ((-Complex.I * (θ : ℂ)) • beta) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [beta, Matrix.conjTranspose_apply]

theorem exp_unitary_left_of_skew (G : Mat2) (hG : G.conjTranspose = -G) :
    (exp G).conjTranspose * exp G = 1 := by
  rw [← Matrix.exp_conjTranspose, hG, Matrix.exp_neg]
  have hu : IsUnit (exp G) := Matrix.isUnit_exp _
  have hd : IsUnit (Matrix.det (exp G)) := (Matrix.isUnit_iff_isUnit_det _).mp hu
  exact Matrix.nonsing_inv_mul _ hd

theorem exp_unitary_right_of_skew (G : Mat2) (hG : G.conjTranspose = -G) :
    exp G * (exp G).conjTranspose = 1 := by
  rw [← Matrix.exp_conjTranspose, hG, Matrix.exp_neg]
  have hu : IsUnit (exp G) := Matrix.isUnit_exp _
  have hd : IsUnit (Matrix.det (exp G)) := (Matrix.isUnit_iff_isUnit_det _).mp hu
  exact Matrix.mul_nonsing_inv _ hd

/-- Exact left-unitarity of the `α` exponential. -/
theorem exp_alpha_unitary_left (θ : ℝ) :
    (exp (((-Complex.I * (θ : ℂ))) • alpha)).conjTranspose *
      exp (((-Complex.I * (θ : ℂ))) • alpha) = 1 :=
  exp_unitary_left_of_skew _ (alpha_generator_skew θ)

/-- Exact right-unitarity of the `α` exponential. -/
theorem exp_alpha_unitary_right (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • alpha) *
      (exp (((-Complex.I * (θ : ℂ))) • alpha)).conjTranspose = 1 :=
  exp_unitary_right_of_skew _ (alpha_generator_skew θ)

/-- Exact left-unitarity of the `β` exponential. -/
theorem exp_beta_unitary_left (θ : ℝ) :
    (exp (((-Complex.I * (θ : ℂ))) • beta)).conjTranspose *
      exp (((-Complex.I * (θ : ℂ))) • beta) = 1 :=
  exp_unitary_left_of_skew _ (beta_generator_skew θ)

/-- Exact right-unitarity of the `β` exponential. -/
theorem exp_beta_unitary_right (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • beta) *
      (exp (((-Complex.I * (θ : ℂ))) • beta)).conjTranspose = 1 :=
  exp_unitary_right_of_skew _ (beta_generator_skew θ)

/-- Determinant one for the literal `α` exponential. -/
theorem det_exp_alpha (θ : ℝ) : Matrix.det (exp (((-Complex.I * (θ : ℂ))) • alpha)) = 1 := by
  rw [exp_alpha_closed, det_closedFactor_alpha]

/-- Determinant one for the literal `β` exponential. -/
theorem det_exp_beta (θ : ℝ) : Matrix.det (exp (((-Complex.I * (θ : ℂ))) • beta)) = 1 := by
  rw [exp_beta_closed, det_closedFactor_beta]

end KomorebiPhysics.InvolutionExponential
