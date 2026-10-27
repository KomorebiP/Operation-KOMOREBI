module

public import KomorebiPhysics.RelativisticClifford3D
public import KomorebiPhysics.InvolutionExponential
public import Mathlib.Tactic.NoncommRing
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.Module

/-!
Closed matrix-exponential factors for the explicit four-component Clifford generators.
The spatial formulas are transported from the diagonal `β` factor by a proved
invertible algebraic bridge; no exponential closed form is assumed.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPhysics.InvolutionExponential4

open NormedSpace
open scoped Matrix ComplexConjugate BigOperators
open KomorebiPhysics.RelativisticClifford3D

/-- Closed trigonometric factor `cos θ I - i sin θ A`. -/
def closedFactor (A : Mat4) (θ : ℝ) : Mat4 :=
  (Real.cos θ : ℂ) • (1 : Mat4) -
    (Complex.I * (Real.sin θ : ℂ)) • A

/-- The diagonal closed form of the `β` factor. -/
theorem closedFactor_beta (θ : ℝ) :
    closedFactor beta θ =
      !![(Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ), 0, 0, 0;
         0, (Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ), 0, 0;
         0, 0, (Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ), 0;
         0, 0, 0, (Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ)] := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [closedFactor, beta]

/-- The literal scaled `β` exponential is diagonal. -/
theorem exp_beta_diagonal (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • beta) =
      !![Complex.exp (-Complex.I * (θ : ℂ)), 0, 0, 0;
         0, Complex.exp (-Complex.I * (θ : ℂ)), 0, 0;
         0, 0, Complex.exp (Complex.I * (θ : ℂ)), 0;
         0, 0, 0, Complex.exp (Complex.I * (θ : ℂ))] := by
  have hz : (((-Complex.I * (θ : ℂ))) • beta) =
      Matrix.diagonal (fun i : Spin4 => if i.val < 2 then
        (-Complex.I * (θ : ℂ)) else (Complex.I * (θ : ℂ))) := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp [beta]
  rw [hz, Matrix.exp_diagonal]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [← Complex.exp_eq_exp_ℂ]

/-- Literal equation (8.8) for the four-component `β`. -/
theorem exp_beta_closed (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • beta) = closedFactor beta θ := by
  rw [exp_beta_diagonal, closedFactor_beta,
    KomorebiPhysics.InvolutionExponential.complex_exp_neg_I,
    KomorebiPhysics.InvolutionExponential.complex_exp_pos_I]

/-- Algebraic bridge from `β` to an anticommuting Clifford involution. -/
def bridge (A : Mat4) : Mat4 := beta + A

/-- Square of the bridge. -/
theorem bridge_sq {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) :
    bridge A * bridge A = (2 : ℂ) • (1 : Mat4) := by
  rw [bridge]
  calc
    (beta + A) * (beta + A) = beta * beta + (A * beta + beta * A) + A * A := by
      noncomm_ring
    _ = (1 : Mat4) + 0 + 1 := by rw [beta_sq, hanti, hA]
    _ = (2 : ℂ) • (1 : Mat4) := by simp [two_smul]

/-- Explicit two-sided inverse of the bridge. -/
theorem bridge_mul_half {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) :
    bridge A * ((1 / 2 : ℂ) • bridge A) = 1 := by
  rw [Matrix.mul_smul, bridge_sq hA hanti]
  ext i j
  simp

theorem half_mul_bridge {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) :
    ((1 / 2 : ℂ) • bridge A) * bridge A = 1 := by
  rw [Matrix.smul_mul, bridge_sq hA hanti]
  ext i j
  simp

/-- The bridge is invertible. -/
theorem bridge_isUnit {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) : IsUnit (bridge A) := by
  rw [isUnit_iff_exists]
  exact ⟨(1 / 2 : ℂ) • bridge A, bridge_mul_half hA hanti,
    half_mul_bridge hA hanti⟩

/-- Exact inverse of the bridge. -/
theorem bridge_inv {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) :
    (bridge A)⁻¹ = (1 / 2 : ℂ) • bridge A := by
  apply Matrix.inv_eq_left_inv
  exact half_mul_bridge hA hanti

/-- The bridge conjugates `β` to `A`. -/
theorem bridge_conj_beta {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) :
    A = bridge A * beta * (bridge A)⁻¹ := by
  rw [bridge_inv hA hanti]
  symm
  calc
    bridge A * beta * ((1 / 2 : ℂ) • bridge A)
        = (1 / 2 : ℂ) • (bridge A * beta * bridge A) := by
          rw [Matrix.mul_smul]
    _ = (1 / 2 : ℂ) • ((2 : ℂ) • A) := by
      congr 1
      have hab : A * beta = -(beta * A) :=
        eq_neg_of_add_eq_zero_left hanti
      have hAba : A * beta * A = -beta := by
        calc
          A * beta * A = (A * beta) * A := rfl
          _ = (-(beta * A)) * A := by rw [hab]
          _ = -(beta * (A * A)) := by simp [Matrix.mul_assoc]
          _ = -beta := by rw [hA]; simp
      rw [bridge]
      calc
        (beta + A) * beta * (beta + A)
            = beta * beta * beta + beta * beta * A +
                A * beta * beta + A * beta * A := by
              noncomm_ring
        _ = beta + A + A + (-beta) := by
          rw [hAba]
          simp [Matrix.mul_assoc, beta_sq]
        _ = (2 : ℂ) • A := by module
    _ = A := by module

/-- Scaled conjugation identity. -/
theorem scaled_conj_beta {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) (θ : ℝ) :
    ((-Complex.I * (θ : ℂ)) • A) =
      bridge A * ((-Complex.I * (θ : ℂ)) • beta) * (bridge A)⁻¹ := by
  calc
    ((-Complex.I * (θ : ℂ)) • A)
        = (-Complex.I * (θ : ℂ)) •
            (bridge A * beta * (bridge A)⁻¹) := by
          exact congrArg (fun X : Mat4 => (-Complex.I * (θ : ℂ)) • X)
            (bridge_conj_beta hA hanti)
    _ = bridge A * ((-Complex.I * (θ : ℂ)) • beta) *
          (bridge A)⁻¹ := by
      rw [Matrix.mul_smul, Matrix.smul_mul]

/-- The bridge transports the closed trigonometric factor. -/
theorem bridge_closedFactor {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) (θ : ℝ) :
    bridge A * closedFactor beta θ * (bridge A)⁻¹ = closedFactor A θ := by
  have hone : bridge A * (1 : Mat4) * (bridge A)⁻¹ = 1 := by
    simp only [Matrix.mul_one]
    rw [bridge_inv hA hanti]
    exact bridge_mul_half hA hanti
  have hbeta : bridge A * beta * (bridge A)⁻¹ = A :=
    (bridge_conj_beta hA hanti).symm
  rw [closedFactor, closedFactor]
  calc
    bridge A *
        ((Real.cos θ : ℂ) • (1 : Mat4) -
          (Complex.I * (Real.sin θ : ℂ)) • beta) *
        (bridge A)⁻¹
        = (Real.cos θ : ℂ) •
            (bridge A * (1 : Mat4) * (bridge A)⁻¹) -
          (Complex.I * (Real.sin θ : ℂ)) •
            (bridge A * beta * (bridge A)⁻¹) := by
      rw [Matrix.mul_sub, Matrix.sub_mul]
      rw [Matrix.mul_smul, Matrix.smul_mul,
        Matrix.mul_smul, Matrix.smul_mul]
    _ = (Real.cos θ : ℂ) • (1 : Mat4) -
          (Complex.I * (Real.sin θ : ℂ)) • A := by rw [hone, hbeta]


/-- Algebraic square of a linear involution factor. -/
theorem linearFactor_sq {A : Mat4} (hA : A * A = 1) (c d : ℂ) :
    (c • (1 : Mat4) - d • A) * (c • (1 : Mat4) - d • A) =
      (c * c + d * d) • (1 : Mat4) - (2 * c * d) • A := by
  rw [Matrix.sub_mul, Matrix.mul_sub, Matrix.mul_sub]
  rw [Matrix.smul_mul, Matrix.mul_smul, Matrix.smul_mul, Matrix.mul_smul,
      Matrix.smul_mul, Matrix.mul_smul, Matrix.smul_mul, Matrix.mul_smul]
  rw [hA]
  simp only [Matrix.one_mul, Matrix.mul_one, smul_smul]
  module

/-- Doubling law for the closed factor of an involution. -/
theorem closedFactor_sq {A : Mat4} (hA : A * A = 1) (θ : ℝ) :
    closedFactor A θ * closedFactor A θ = closedFactor A (2 * θ) := by
  rw [closedFactor, closedFactor, linearFactor_sq hA]
  have hc :
      (Real.cos θ : ℂ) * (Real.cos θ : ℂ) +
          (Complex.I * (Real.sin θ : ℂ)) *
            (Complex.I * (Real.sin θ : ℂ)) =
        (Real.cos (2 * θ) : ℂ) := by
    calc
      _ = (((Real.cos θ)^2 - (Real.sin θ)^2 : ℝ) : ℂ) := by
        push_cast
        ring_nf
        rw [pow_two Complex.I, Complex.I_mul_I]
        ring
      _ = (Real.cos (2 * θ) : ℂ) := by
        exact_mod_cast (Real.cos_two_mul' θ).symm
  have hs :
      2 * (Real.cos θ : ℂ) * (Complex.I * (Real.sin θ : ℂ)) =
        Complex.I * (Real.sin (2 * θ) : ℂ) := by
    rw [Real.sin_two_mul]
    push_cast
    ring
  rw [hc, hs]

/-- Symmetric Clifford sandwich: an anticommuting operator passes unchanged. -/
theorem closedFactor_sandwich_anticommute {A X : Mat4}
    (hA : A * A = 1) (hanti : A * X + X * A = 0) (θ : ℝ) :
    closedFactor A θ * X * closedFactor A θ = X := by
  have hax : A * X = -(X * A) := eq_neg_of_add_eq_zero_left hanti
  have haxa : A * X * A = -X := by
    calc
      A * X * A = (A * X) * A := rfl
      _ = (-(X * A)) * A := by rw [hax]
      _ = -(X * (A * A)) := by simp [Matrix.mul_assoc]
      _ = -X := by rw [hA]; simp
  rw [closedFactor]
  rw [Matrix.sub_mul, Matrix.mul_sub]
  rw [Matrix.smul_mul, Matrix.mul_smul, Matrix.smul_mul, Matrix.mul_smul]
  simp only [Matrix.one_mul, Matrix.mul_one]
  simp only [Matrix.sub_mul]
  rw [hax]
  simp [Matrix.mul_assoc, hA, smul_smul]
  have hscalar :
      (Real.cos θ : ℂ) * (Real.cos θ : ℂ) -
          (Complex.I * (Real.sin θ : ℂ)) *
            (Complex.I * (Real.sin θ : ℂ)) = 1 := by
    calc
      _ = (((Real.cos θ)^2 + (Real.sin θ)^2 : ℝ) : ℂ) := by
        push_cast
        ring_nf
        rw [pow_two Complex.I, Complex.I_mul_I]
        ring
      _ = 1 := by exact_mod_cast Real.cos_sq_add_sin_sq θ
  match_scalars
  · simpa [pow_two] using hscalar
  · ring


/-- Symmetric sandwich of one Clifford factor by another. -/
theorem closedFactor_sandwich_closedFactor {A B : Mat4}
    (hA : A * A = 1) (hanti : A * B + B * A = 0)
    (θ φ : ℝ) :
    closedFactor A θ * closedFactor B φ * closedFactor A θ =
      (Real.cos φ : ℂ) • closedFactor A (2 * θ) -
        (Complex.I * (Real.sin φ : ℂ)) • B := by
  rw [closedFactor]
  calc
    closedFactor A θ *
        ((Real.cos φ : ℂ) • (1 : Mat4) -
          (Complex.I * (Real.sin φ : ℂ)) • B) *
        closedFactor A θ
        = (Real.cos φ : ℂ) •
            (closedFactor A θ * closedFactor A θ) -
          (Complex.I * (Real.sin φ : ℂ)) •
            (closedFactor A θ * B * closedFactor A θ) := by
      rw [Matrix.mul_sub, Matrix.sub_mul]
      rw [Matrix.mul_smul, Matrix.smul_mul,
        Matrix.mul_smul, Matrix.smul_mul]
      simp only [Matrix.mul_one]
    _ = (Real.cos φ : ℂ) • closedFactor A (2 * θ) -
          (Complex.I * (Real.sin φ : ℂ)) • B := by
      rw [closedFactor_sq hA, closedFactor_sandwich_anticommute hA hanti]

/-- Generic closed exponential for any explicit anticommuting Clifford generator. -/
theorem exp_closed_of_clifford {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • A) = closedFactor A θ := by
  rw [scaled_conj_beta hA hanti θ,
    Matrix.exp_conj (bridge A) _ (bridge_isUnit hA hanti),
    exp_beta_closed, bridge_closedFactor hA hanti]

/-- Closed exponentials of the three spatial generators. -/
theorem exp_alphaX_closed (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • alphaX) = closedFactor alphaX θ :=
  exp_closed_of_clifford alphaX_sq alphaX_beta_anticommute θ

theorem exp_alphaY_closed (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • alphaY) = closedFactor alphaY θ :=
  exp_closed_of_clifford alphaY_sq alphaY_beta_anticommute θ

theorem exp_alphaZ_closed (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • alphaZ) = closedFactor alphaZ θ :=
  exp_closed_of_clifford alphaZ_sq alphaZ_beta_anticommute θ

/-- A scaled Hermitian Clifford generator is skew-Hermitian. -/
theorem generator_skew {A : Mat4} (hA : A.conjTranspose = A) (θ : ℝ) :
    (((-Complex.I * (θ : ℂ)) • A).conjTranspose) =
      - ((-Complex.I * (θ : ℂ)) • A) := by
  rw [Matrix.conjTranspose_smul, hA]
  ext i j
  simp

/-- Left-unitarity of the exponential of a skew-Hermitian four-by-four matrix. -/
theorem exp_unitary_left_of_skew (G : Mat4) (hG : G.conjTranspose = -G) :
    (exp G).conjTranspose * exp G = 1 := by
  rw [← Matrix.exp_conjTranspose, hG, Matrix.exp_neg]
  have hu : IsUnit (exp G) := Matrix.isUnit_exp _
  have hd : IsUnit (Matrix.det (exp G)) := (Matrix.isUnit_iff_isUnit_det _).mp hu
  exact Matrix.nonsing_inv_mul _ hd

/-- Right-unitarity of the exponential of a skew-Hermitian four-by-four matrix. -/
theorem exp_unitary_right_of_skew (G : Mat4) (hG : G.conjTranspose = -G) :
    exp G * (exp G).conjTranspose = 1 := by
  rw [← Matrix.exp_conjTranspose, hG, Matrix.exp_neg]
  have hu : IsUnit (exp G) := Matrix.isUnit_exp _
  have hd : IsUnit (Matrix.det (exp G)) := (Matrix.isUnit_iff_isUnit_det _).mp hu
  exact Matrix.mul_nonsing_inv _ hd

/-- Generic unitarity for the literal Clifford exponential. -/
theorem exp_unitary_left {A : Mat4} (hA : A.conjTranspose = A) (θ : ℝ) :
    (exp (((-Complex.I * (θ : ℂ))) • A)).conjTranspose *
      exp (((-Complex.I * (θ : ℂ))) • A) = 1 :=
  exp_unitary_left_of_skew _ (generator_skew hA θ)

theorem exp_unitary_right {A : Mat4} (hA : A.conjTranspose = A) (θ : ℝ) :
    exp (((-Complex.I * (θ : ℂ))) • A) *
      (exp (((-Complex.I * (θ : ℂ))) • A)).conjTranspose = 1 :=
  exp_unitary_right_of_skew _ (generator_skew hA θ)

/-- Determinant of the diagonal `β` factor. -/
theorem det_closedFactor_beta (θ : ℝ) : Matrix.det (closedFactor beta θ) = 1 := by
  rw [closedFactor_beta]
  rw [show (!![(Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ), 0, 0, 0;
         0, (Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ), 0, 0;
         0, 0, (Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ), 0;
         0, 0, 0, (Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ)] : Mat4) =
       Matrix.diagonal (fun i : Spin4 => if i.val < 2 then
         (Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ)
       else (Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ)) by
       ext i j; fin_cases i <;> fin_cases j <;> simp]
  rw [Matrix.det_diagonal, Fin.prod_univ_four]
  norm_num
  rw [← Complex.ofReal_cos, ← Complex.ofReal_sin]
  have htrig : (Real.cos θ : ℂ) ^ 2 + (Real.sin θ : ℂ) ^ 2 = 1 := by
    exact_mod_cast Real.cos_sq_add_sin_sq θ
  calc
    ((Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ)) *
          ((Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ)) *
        ((Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ)) *
          ((Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ))
        = (((Real.cos θ : ℂ) - Complex.I * (Real.sin θ : ℂ)) *
            ((Real.cos θ : ℂ) + Complex.I * (Real.sin θ : ℂ))) ^ 2 := by ring
    _ = (((Real.cos θ : ℂ) ^ 2 + (Real.sin θ : ℂ) ^ 2)) ^ 2 := by
      ring_nf
      simp
    _ = 1 := by rw [htrig]; norm_num

/-- Determinant one for the literal `β` exponential. -/
theorem det_exp_beta (θ : ℝ) :
    Matrix.det (exp (((-Complex.I * (θ : ℂ))) • beta)) = 1 := by
  rw [exp_beta_closed, det_closedFactor_beta]

/-- Determinant is preserved by the proved bridge conjugation. -/
theorem det_exp_of_clifford {A : Mat4} (hA : A * A = 1)
    (hanti : A * beta + beta * A = 0) (θ : ℝ) :
    Matrix.det (exp (((-Complex.I * (θ : ℂ))) • A)) = 1 := by
  rw [scaled_conj_beta hA hanti θ,
    Matrix.exp_conj (bridge A) _ (bridge_isUnit hA hanti)]
  rw [Matrix.det_conj (bridge_isUnit hA hanti), det_exp_beta]

end KomorebiPhysics.InvolutionExponential4
